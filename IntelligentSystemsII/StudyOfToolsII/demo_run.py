import numpy as np
import tensorflow as tf
import pygame
from tf_agents.environments import suite_gym
from tf_agents.trajectories.time_step import TimeStep


# Environment name + policy directory
env_name = "CartPole-v1"
policy_dir = "saved_policy"


def watch_agent_pygame(env, policy, num_episodes=3):
    """
    Visualizes an agent's behavior in a given environment using Pygame for rendering.
    
    This function creates a Pygame window and displays the agent's actions in the environment
    for a specified number of episodes. The visualization runs until all episodes are completed
    or until the user closes the window.
    
    Args:
        env: The environment in which the agent will act. Must support reset(), step(),
             and render(mode="rgb_array") methods.
        policy: The agent's policy that determines actions. Must have an action() method
                that accepts a TimeStep object and returns an action.
        num_episodes (int, optional): The number of episodes to run. Defaults to 3.
    
    Returns:
        None: This function does not return anything, it only visualizes the agent's behavior.
        
    Note:
        - The environment's render() method should support the "rgb_array" mode.
        - The function handles the Pygame initialization and cleanup.
        - The visualization runs at 60 FPS.
        - The function will exit early if the user closes the Pygame window.
    """
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()

    running = True  

    while running:  
        for _ in range(num_episodes):
            # Reset the environment and get the initial state
            time_step = env.reset()
            state = time_step.observation  # Get the observation from time_step

            done = False
            while not done:
                screen.fill((0, 0, 0))  # Black background

                # Adjust the input shape to include the batch size
                state = np.expand_dims(state, axis=0)

                # Create a suitable "TimeStep" to pass to the policy
                step_type = np.array([time_step.step_type], dtype=np.int32)
                reward = np.array([0], dtype=np.float32)  # dummy reward, as the agent hasn't received it yet
                discount = np.array([1.0], dtype=np.float32)  # No future discount for this step

                # Create the complete TimeStep
                time_step_to_pass = TimeStep(  # Now we use TimeStep directly
                    step_type=step_type, reward=reward, discount=discount, observation=state
                )

                # Get the agent's action based on time_step
                action = policy.action(time_step_to_pass)

                # Execute the action in the environment and get the next state
                time_step = env.step(action.action.numpy()[0])
                next_state = time_step.observation
                reward = time_step.reward
                done = time_step.is_last()

                # Render the environment
                frame = env.render(mode="rgb_array")
                frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                screen.blit(frame, (0, 0))
                pygame.display.flip()
                clock.tick(60)  # 60 FPS limit

                # Update the state
                state = next_state

                # Check window close events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False  # If the user closes the window, we exit the main loop
                        pygame.quit()
                        return

    pygame.quit()


def run():
    # 1. Configure the environment
    eval_env = suite_gym.load(env_name)  # Evaluation environment (non-TF)

    # 2. Load the saved policy
    saved_policy = tf.saved_model.load(policy_dir)

    # 3. Watch the agent in action
    print("Watching the agent...")
    watch_agent_pygame(eval_env, saved_policy)


if __name__ == "__main__":
    run()
