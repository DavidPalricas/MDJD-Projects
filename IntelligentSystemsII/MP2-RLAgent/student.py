"""
Train and run policy for the Snake game.
Authors: [David Palricas, Daniel Emídio, Marcio Tavares]
"""
import asyncio
import getpass
import json
import os
from sys import argv
import time
from datetime import datetime
import websockets
from snake_train_env import SnakeTrainEnv
from agents.snake_dqn_agent import DQNAgent
from agents.snake_ppo_agent import PPOAgent
from snake_game import SnakeGame, setup_logging


# Dictionary to map "agent types" to their classes
AGENTS = {
    "dqn": DQNAgent,
    "ppo": PPOAgent,
    # Add other agents here
}

async def play_single_episode(
    websocket, agent_name,
    game, train_env, agent,
    episode_num, total_steps, logger
):
    """Play a single episode and return updated total_steps and episode_reward."""
    
    episode_start_time = time.time()
    print("\n")
    # logger.info(f"Starting Episode {episode_num}")
    
    # Reset game state for new episode
    game.reset()

    # Start listening for messages
    await game.start_listener(websocket)

    # Join the game
    await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
    logger.debug("Sent join command to server")

    # Wait for first state
    if not await game.wait_for_first_state():
        logger.error(f"Failed to receive first state for episode {episode_num}, skipping episode")
        await game.stop_listener()
        return total_steps, 0, False

    logger.info(f"Episode {episode_num} started successfully")
    
    time_step = train_env.call_reset(game.get_first_state())
    episode_reward = 0
    episode_steps = 0
    episode_score = 0
    
    try:
        while not time_step.is_last():
            # Get action from agent
            action = agent.get_action(time_step)
            
            # Send action to server
            directions = ["w", "s", "a", "d"]  # up, down, left, right
            key = directions[action]
            
            if episode_steps % 50 == 0:  # Log every 50 steps to reduce noise
                logger.debug(f"Episode {episode_num}, Step {episode_steps}, Action: {key}")
            
            try:
                await websocket.send(json.dumps({"cmd": "key", "key": key}))
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection closed while sending action in episode {episode_num}")
                break
            
            # Get next state
            try:
                current_state = await game.get_state()

                # Also check if this is an incomplete state (missing essential fields)
                if not is_valid_game_state(current_state):
                    # logger.debug(f"Episode {episode_num} - Skipping incomplete state: {current_state}")
                    # Get the next state (should be the highscores message)
                    try:
                        current_state = await game.get_state()
                    except ConnectionError:
                        logger.warning(f"Connection lost while waiting for final message in episode {episode_num}")
                        break

                if current_state.get('score') is not None:
                    episode_score = current_state.get('score')

            except ConnectionError:
                logger.warning(f"Connection lost during episode {episode_num}")
                break

            next_time_step = train_env.call_step(current_state, action)
            
            # Store experience and train
            agent.store_experience(time_step, action, next_time_step)
            
            # Update for next iteration
            time_step = next_time_step
            episode_reward += time_step.reward
            episode_steps += 1
            total_steps += 1
            
            # Check if game ended
            if current_state.get('highscores') is not None:
                logger.info(f"Episode {episode_num} - Game Over! Final score: {episode_score}")
                break
            
    except websockets.exceptions.ConnectionClosed:
        logger.warning(f"WebSocket connection closed during episode {episode_num}")
    except Exception as e:
        logger.error(f"Error during episode {episode_num}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Always stop the listener
        await game.stop_listener()
    
    # Perform training step periodically
    if episode_num % 4 == 0:
        loss = agent.train_step()
        if loss is not None:
            logger.info(f"Episode {episode_num}, Training Loss: {loss:.4f}")

    # Episode ended
    agent.on_episode_end()
    episode_duration = time.time() - episode_start_time
    
    logger.info(f"Episode {episode_num} completed - Reward: {episode_reward:.2f}, "
               f"Steps: {episode_steps}, Score: {episode_score}, Duration: {episode_duration:.2f}s")
    
    return total_steps, episode_reward, True, episode_score

async def agent_loop(server_address="localhost:8000", agent_name="student",
                     episode_limit=100, policy_train=None, agent_type="dqn"):
    """Example client loop with proper RL integration and logging."""
   
    logger = setup_logging()
    logger.info("Starting training mode...")
    logger.info(f"Server: {server_address}, Agent: {agent_name}, Episode limit: {episode_limit}, Agent Type: {agent_type}")
    
    if policy_train:
        logger.info(f"Pre-trained policy will be loaded: {policy_train}")
    
    game = SnakeGame(logger)

    # Initialize environment with initial state
    train_env = SnakeTrainEnv()
    logger.info("Environment initialized")

    # Initialize agent
    if agent_type not in AGENTS:
        logger.error(f"Unknown agent type: {agent_type}. Available agents: {list(AGENTS.keys())}")
        return
    
    agent = AGENTS[agent_type](train_env)
    logger.info("Agent initialized")

    episode = 0
    if policy_train:
        # Load a pre-trained policy if specified
        try:
            agent.load(policy_train)
            logger.info(f"Pre-trained policy loaded from {policy_train}")
            episode = int(policy_train.split('_')[-1]) if '_' in policy_train else 0
            episode_limit = episode_limit + episode  
            logger.info(f"Starting from episode {episode}, new limit: {episode_limit}")
        except Exception as e:
            logger.error(f"Failed to load pre-trained policy: {e}")
            return
    
    total_steps = 0
    episode_rewards = []
    episode_scores = []
    training_start_time = time.time()
    
    while episode < episode_limit:
        try:
            # Create new WebSocket connection for each episode
            logger.debug(f"Creating WebSocket connection for episode {episode + 1}")
            async with websockets.connect(f"ws://{server_address}/player") as websocket:
                episode += 1
                total_steps, episode_reward, success, episode_score = await play_single_episode(
                    websocket, agent_name, game,
                    train_env, agent, episode,
                    total_steps, logger
                )
                
                if not success:
                    episode -= 1  # Don't count failed episodes
                    logger.warning(f"Episode {episode + 1} failed, retrying...")
                    continue
                
                episode_rewards.append(episode_reward)
                episode_scores.append(episode_score)
                
                # Print training stats periodically
                # if episode % 10 == 0:
                #     stats = agent.get_training_stats()
                #     avg_reward_last_10 = sum(episode_rewards[-10:]) / min(10, len(episode_rewards))
                #     logger.info(f"Training Stats after {episode} episodes:")
                #     logger.info(f"  Average reward (last 10): {avg_reward_last_10:.2f}")
                #     for key, value in stats.items():
                #         logger.info(f"  {key}: {value}")
                
                # Save model periodically
                if episode % 1000 == 0:
                    model_path = f"policy/backups/{agent_type}_agent_episode_{episode}"
                    agent.save(model_path)
                    logger.info(f"Model saved: {model_path}")
                
                # Progress report every 25 episodes
                # if episode % 25 == 0:
                #     elapsed_time = time.time() - training_start_time
                #     avg_time_per_episode = elapsed_time / episode
                #     remaining_episodes = episode_limit - episode
                #     estimated_remaining_time = avg_time_per_episode * remaining_episodes
                    
                #     logger.info(f"Progress Report - Episode {episode}/{episode_limit}")
                #     logger.info(f"  Elapsed time: {elapsed_time/60:.1f} minutes")
                #     logger.info(f"  Estimated remaining time: {estimated_remaining_time/60:.1f} minutes")
                #     logger.info(f"  Average episode duration: {avg_time_per_episode:.2f} seconds")

        except Exception as e:
            logger.error(f"Error in episode {episode}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
            
    total_training_time = time.time() - training_start_time
    logger.info(f"Training completed! Total time: {total_training_time/60:.1f} minutes")
    logger.info(f"Reached episode limit of {episode_limit}")
    
    # Save final model
    final_model_path = f"policy/{agent_type}_agent_final_{episode}"
    agent.save(final_model_path)
    logger.info(f"Final model saved: {final_model_path}")
    
    # Training summary
    if episode_rewards:
        avg_reward = sum(episode_rewards) / len(episode_rewards)
        max_reward = max(episode_rewards)
        max_score = max(episode_scores) if episode_scores else 0
        logger.info(f"Training Summary:")
        logger.info(f"  Total episodes: {len(episode_rewards)}")
        logger.info(f"  Average reward: {avg_reward:.2f}")
        logger.info(f"  Maximum reward: {max_reward:.2f}")
        logger.info(f"  Maximum score: {max_score}")

async def run_policy(server_address="localhost:8000", agent_name="student",
                     model_path='dqn_agent_final', agent_type="dqn"):
    """Load a trained model and use it to play the game WITHOUT training infrastructure."""
    logger = setup_logging(log_file=f'logs/snake_inference_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logger.info(f"Loading trained model from {model_path}...")
    
    # Initialize minimal environment just for specs (no training logic)
    dummy_env = SnakeTrainEnv()

    # Load Agent and weights
    if agent_type not in AGENTS:
        logger.error(f"Unknown agent type: {agent_type}. Available agents: {list(AGENTS.keys())}")
        return
    
    agent = AGENTS[agent_type](dummy_env)
    
    # Load ONLY the policy
    try:
        agent.load(model_path)
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    try:
        async with websockets.connect(f"ws://{server_address}/player") as websocket:
            game = SnakeGame(logger)
            await game.start_listener(websocket)
            
            # Join the game
            await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
            logger.info("Trained agent joined the game!")

            if not await game.wait_for_first_state():
                logger.error("Failed to receive initial state.")
                return

            # Convert initial state to TensorFlow time_step format
            initial_state = game.get_first_state()
            time_step = dummy_env.call_reset(initial_state)
            steps = 0
            game_start_time = time.time()

            dummy_env.render('human')  # Render the initial state

            while True:
                # Get action from the trained policy (NO exploration)
                action = agent.get_action(time_step, False)
                
                # Map action to key
                key = ["w", "s", "a", "d"][action]
                await websocket.send(json.dumps({"cmd": "key", "key": key}))
                
                if steps % 50 == 0:  # Log every 50 steps
                    logger.debug(f"Step {steps}, Action: {key}")
                    # dummy_env.render('human')  # Render the current state
               # Get next state from the server
                try:
                    state = await game.get_state()
                    current_score = state.get('score', 0)
                    
                    if state.get('highscores') is not None:
                        game_duration = time.time() - game_start_time
                        logger.info(f"Game Over! Final score: {current_score}, "
                                   f"Steps: {steps}, Duration: {game_duration:.2f}s")
                        break
                    
                    # Convert state to time_step
                    time_step = dummy_env.call_step(state, action)
                    steps += 1
                    
                    if steps % 100 == 0:  # Progress update every 100 steps
                        logger.info(f"Game in progress - Steps: {steps}, Score: {current_score}")
                    
                except ConnectionError:
                    logger.error("Connection lost during game")
                    break

            await game.stop_listener()
            logger.info(f"Game session completed. Total steps: {steps}")
            
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        import traceback
        logger.error(traceback.format_exc())

def is_valid_game_state(state):
    """
    Check if a game state contains the essential fields for a valid game state.
    Returns False for incomplete/partial states that should be skipped.
    """
    # Define what constitutes a valid game state
    # Adjust these based on what your environment expects
    essential_fields = ['body']  # Add other essential fields as needed
    
    # Check if all essential fields are present
    for field in essential_fields:
        if field not in state:
            return False
    
    # Additional validation can be added here
    # For example, check if the state has reasonable values
    # if 'step' in state and not isinstance(state['step'], (int, float)):
    #     return False
        
    return True


# DO NOT CHANGE THE LINES BELOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 student.py train

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    SERVER = os.environ.get("SERVER", "localhost")
    PORT = os.environ.get("PORT", "8000")
    NAME = os.environ.get("NAME", getpass.getuser())
    AGENT_TYPE = os.environ.get("AGENT_TYPE", "dqn").lower().strip()

    episode_limit = 100
    train = False
    policy_name = f"{AGENT_TYPE}_agent_final"

    if len(argv) > 1:
        if argv[1] == "train":
            train = True

            # Check for episode limit
            if len(argv) > 2:
                try:
                    episode_limit = int(argv[2])
                except ValueError:
                    print("Episode limit must be an integer")
                    exit(1)
            
            # Check for policy training file
            policy_name = argv[3] if len(argv) > 3 else None
        else:
            policy_name = argv[1]
    else:
        print("Usage:")
        print("  python3 student.py train [episode_limit] [policy_train]")
        print("  python3 student.py <policy_file>")
        print("Running in non-training mode (using trained policy)...")
    
    policy_path = f"policy/{policy_name}" if policy_name else None
    if train:
        loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME, episode_limit, policy_path, AGENT_TYPE))
    else:
        loop.run_until_complete(run_policy(f"{SERVER}:{PORT}", NAME, policy_path, AGENT_TYPE))
