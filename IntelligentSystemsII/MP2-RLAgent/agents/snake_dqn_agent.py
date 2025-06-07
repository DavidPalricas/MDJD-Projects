import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
import json
import os
from agents.snake_base_agent import SnakeBaseAgent


class DQNAgent(SnakeBaseAgent):
    """Deep Q-Network agent for Snake game with dynamic observation handling."""
    
    def __init__(self, env, learning_rate=0.0005, epsilon=0.95, epsilon_decay=0.9995, 
                 epsilon_min=0.05, memory_size=50000, batch_size=64, target_update_freq=500):
        """Initialize the DQN agent with improved hyperparameters."""
        super().__init__(env)

        # Initialize all required attributes
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        
        # Experience replay buffer
        self.memory = deque(maxlen=memory_size)
        
        # Networks - will be initialized on first state
        self.q_network = None
        self.target_network = None
        self.optimizer = None
        
        # Current network input shape (will be set dynamically)
        self.current_map_shape = None
        
        # Training variables
        self.warmup_steps = 1000  # Steps before training starts
        self.step_count = 0  # Initialize step counter
        
        # Initialize tracking attributes that might be expected by base class
        self.episode_count = 0
        self.scores = []
        self.training_losses = []
        
        # Set action size - assuming 4 actions for snake (up, down, left, right)
        self.action_size = 4
        
    def _create_network(self, map_shape):
        """Create a simpler but more effective neural network architecture."""
        # Input layers for each observation component
        map_input = keras.layers.Input(shape=map_shape, name='map_input')
        traverse_input = keras.layers.Input(shape=(), name='traverse_input')
        range_input = keras.layers.Input(shape=(), name='range_input')
        direction_input = keras.layers.Input(shape=(), name='direction_input')
        timeout_input = keras.layers.Input(shape=(), name='timeout_input')
        
        # Process map with simplified CNN
        map_expanded = keras.layers.Reshape((*map_shape, 1))(map_input)
        
        # Simpler CNN architecture
        conv1 = keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(map_expanded)
        conv1 = keras.layers.BatchNormalization()(conv1)
        
        conv2 = keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
        conv2 = keras.layers.BatchNormalization()(conv2)
        pool1 = keras.layers.MaxPooling2D((2, 2), padding='same')(conv2)
        
        conv3 = keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
        conv3 = keras.layers.BatchNormalization()(conv3)
        
        # Global average pooling
        map_features = keras.layers.GlobalAveragePooling2D()(conv3)
        
        # Simplified scalar processing
        traverse_embedded = keras.layers.Embedding(2, 4)(traverse_input)
        traverse_flat = keras.layers.Flatten()(traverse_embedded)
        
        range_embedded = keras.layers.Embedding(11, 4)(range_input)
        range_flat = keras.layers.Flatten()(range_embedded)
        
        direction_embedded = keras.layers.Embedding(4, 4)(direction_input)
        direction_flat = keras.layers.Flatten()(direction_embedded)
        
        # Simpler timeout processing
        timeout_normalized = keras.layers.Lambda(lambda x: tf.cast(x, tf.float32) / 1000.0)(timeout_input)
        timeout_reshaped = keras.layers.Reshape((1,))(timeout_normalized)
        
        # Combine features
        combined = keras.layers.Concatenate()([
            map_features,
            traverse_flat,
            range_flat,
            direction_flat,
            timeout_reshaped
        ])
        
        # Simplified dense layers
        dense1 = keras.layers.Dense(256, activation='relu')(combined)
        dense1 = keras.layers.Dropout(0.2)(dense1)
        
        dense2 = keras.layers.Dense(128, activation='relu')(dense1)
        dense2 = keras.layers.Dropout(0.2)(dense2)
        
        dense3 = keras.layers.Dense(64, activation='relu')(dense2)
        
        # Output layer
        q_values = keras.layers.Dense(self.action_size, activation='linear', name='q_values')(dense3)
        
        # Create model
        model = keras.Model(
            inputs=[map_input, traverse_input, range_input, direction_input, timeout_input],
            outputs=q_values
        )
        
        return model
    
    def _initialize_networks(self, observation):
        """Initialize networks based on first observation."""
        map_shape = observation['map'].shape
        self.current_map_shape = map_shape
        
        print(f"Initializing networks with map shape: {map_shape}")
        
        # Create main and target networks
        self.q_network = self._create_network(map_shape)
        self.target_network = self._create_network(map_shape)
        
        # Use a more conservative optimizer
        self.optimizer = keras.optimizers.Adam(
            learning_rate=self.learning_rate,
            clipnorm=1.0  # Gradient clipping
        )
        
        # Copy weights to target network
        self.target_network.set_weights(self.q_network.get_weights())
        
        print("Networks initialized successfully")
        print(f"Network summary:")
        self.q_network.summary()
    
    def _preprocess_observation(self, observation):
        """Preprocess observation for network input."""
        return [
            np.expand_dims(observation['map'].astype(np.float32), axis=0),
            np.expand_dims(observation['traverse'], axis=0),
            np.expand_dims(np.clip(observation['range'], 0, 10), axis=0),  # Clip range
            np.expand_dims(observation['direction'], axis=0),
            np.expand_dims(observation['timeout'].astype(np.float32), axis=0)
        ]
    
    def get_action(self, time_step, use_exploration_policy=True):
        """Get action using epsilon-greedy policy with improved exploration."""
        # Initialize networks on first call
        if self.q_network is None:
            self._initialize_networks(time_step.observation)
        
        # Check if map shape changed
        current_shape = time_step.observation['map'].shape
        if current_shape != self.current_map_shape:
            print(f"Map shape changed from {self.current_map_shape} to {current_shape}")
            self._initialize_networks(time_step.observation)
        
        # Epsilon-greedy with improved exploration
        if use_exploration_policy and np.random.random() <= self.epsilon:
            return np.random.randint(0, self.action_size)
        
        # Get Q-values from network
        try:
            inputs = self._preprocess_observation(time_step.observation)
            q_values = self.q_network(inputs, training=False)
            action = np.argmax(q_values[0])
            return int(action)
        except Exception as e:
            print(f"Error in get_action: {e}")
            return np.random.randint(0, self.action_size)
    
    def store_experience(self, state, action, next_state):
        """Store experience in replay buffer with validation."""
        # Only store if networks are initialized and shapes match
        if self.q_network is None:
            return
            
        # Validate state shapes
        current_shape = state.observation['map'].shape
        next_shape = next_state.observation['map'].shape
        
        if (current_shape != self.current_map_shape or 
            next_shape != self.current_map_shape):
            return  # Skip storing if shapes don't match
        
        # Validate action
        if not (0 <= action <= 3):
            return
            
        self.memory.append((state, action, next_state))
    
    def train_step(self):
        """Improved training step with better stability."""
        if (len(self.memory) < max(self.batch_size, self.warmup_steps) or 
            self.q_network is None):
            return None
        
        # Sample batch
        try:
            batch = random.sample(self.memory, self.batch_size)
        except ValueError:
            return None
        
        # Process batch
        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []
        
        for state, action, next_state in batch:
            # Validate shapes
            if (state.observation['map'].shape != self.current_map_shape or
                next_state.observation['map'].shape != self.current_map_shape):
                continue
                
            states.append(state.observation)
            actions.append(action)
            
            # Handle reward properly
            reward = next_state.reward
            if hasattr(reward, 'numpy'):
                reward_value = float(reward.numpy())
            elif isinstance(reward, np.ndarray):
                reward_value = float(reward.item() if reward.size == 1 else reward.mean())
            else:
                reward_value = float(reward)
            
            # Clip extreme rewards for stability
            reward_value = np.clip(reward_value, -100, 100)
            rewards.append(reward_value)
            
            next_states.append(next_state.observation)
            dones.append(next_state.is_last())
        
        if len(states) < self.batch_size // 2:  # Need minimum samples
            return None
        
        try:
            # Prepare batch inputs
            current_inputs = self._prepare_batch_inputs(states)
            next_inputs = self._prepare_batch_inputs(next_states)
            
            # Get Q-values
            current_q_values = self.q_network(current_inputs, training=False)
            next_q_values = self.target_network(next_inputs, training=False)
            
            # Compute targets using Double DQN
            next_actions = tf.argmax(self.q_network(next_inputs, training=False), axis=1)
            next_q_values_selected = tf.reduce_sum(
                next_q_values * tf.one_hot(next_actions, self.action_size), axis=1
            )
            
            # Compute target Q-values
            targets = current_q_values.numpy()
            for i in range(len(states)):
                if dones[i]:
                    targets[i][actions[i]] = rewards[i]
                else:
                    targets[i][actions[i]] = rewards[i] + 0.99 * next_q_values_selected[i]
            
            # Train network
            with tf.GradientTape() as tape:
                q_values = self.q_network(current_inputs, training=True)
                loss = keras.losses.Huber()(targets, q_values)  # Use Huber loss for stability
            
            gradients = tape.gradient(loss, self.q_network.trainable_variables)
            # Clip gradients
            gradients = [tf.clip_by_norm(g, 1.0) for g in gradients]
            self.optimizer.apply_gradients(zip(gradients, self.q_network.trainable_variables))
            
            # Update target network
            self.step_count += 1
            if self.step_count % self.target_update_freq == 0:
                self.target_network.set_weights(self.q_network.get_weights())
                print(f"Target network updated at step {self.step_count}")
            
            # Decay epsilon more gradually
            if self.epsilon > self.epsilon_min:
                self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
            loss_value = tf.reduce_mean(loss).numpy()
            self.training_losses.append(loss_value)
            
            return loss_value
            
        except Exception as e:
            print(f"Error in training step: {e}")
            return None
    
    def _prepare_batch_inputs(self, observations):
        """Prepare batch inputs for the network."""
        return [
            np.array([obs['map'].astype(np.float32) for obs in observations]),
            np.array([obs['traverse'] for obs in observations]),
            np.array([np.clip(obs['range'], 0, 10) for obs in observations]),
            np.array([obs['direction'] for obs in observations]),
            np.array([obs['timeout'].astype(np.float32) for obs in observations])
        ]
    
    def on_episode_end(self):
        """Called at the end of each episode."""
        self.episode_count += 1
        
        # Get final score from environment if available
        try:
            state = self.env.get_state()
            final_score = state.get('score', 0) if isinstance(state, dict) else 0
        except:
            final_score = 0
            
        self.scores.append(final_score)
        
        # Print progress every 50 episodes
        if self.episode_count % 50 == 0:
            avg_score = np.mean(self.scores[-50:]) if len(self.scores) >= 50 else np.mean(self.scores)
            print(f"Episode {self.episode_count}, Avg Score (last 50): {avg_score:.2f}, "
                  f"Epsilon: {self.epsilon:.3f}, Memory: {len(self.memory)}")
    
    def evaluate(self, num_episodes=5):
        """Evaluate the agent performance."""
        if self.q_network is None:
            return 0.0
        
        total_reward = 0
        total_score = 0
        original_epsilon = self.epsilon
        self.epsilon = 0  # No exploration during evaluation
        
        for episode in range(num_episodes):
            time_step = self.env.reset()
            episode_reward = 0
            
            while not time_step.is_last():
                action = self.get_action(time_step, False)
                time_step = self.env.step(action)
                
                # Handle reward
                reward = time_step.reward
                if hasattr(reward, 'numpy'):
                    reward_value = reward.numpy().item()
                elif isinstance(reward, np.ndarray):
                    reward_value = reward.item() if reward.size == 1 else float(reward)
                else:
                    reward_value = float(reward)
                
                episode_reward += reward_value
            
            # Get final score
            try:
                final_score = self.env.get_state().get('score', 0)
            except:
                final_score = 0
                
            total_reward += episode_reward
            total_score += final_score
        
        self.epsilon = original_epsilon  # Restore original epsilon
        
        return total_reward / num_episodes, total_score / num_episodes
    
    def get_training_stats(self):
        """Get current training statistics."""
        stats = {
            'epsilon': self.epsilon,
            'memory_size': len(self.memory),
            'episode_count': self.episode_count,
        }
        
        if self.training_losses:
            stats['avg_loss'] = np.mean(self.training_losses[-100:])  # Last 100 losses
        
        if self.scores:
            stats['avg_score'] = np.mean(self.scores[-10:])  # Last 10 scores
            stats['max_score'] = max(self.scores)
        
        return stats
    
    def save(self, filepath):
        """Save the trained model."""
        if self.q_network is None:
            print("No model to save - networks not initialized")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the main network
            self.q_network.save_weights(f"{filepath}_weights.h5")
            
            # Save configuration
            config = {
                'learning_rate': self.learning_rate,
                'epsilon': self.epsilon,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
                'memory_size': self.memory_size,
                'batch_size': self.batch_size,
                'target_update_freq': self.target_update_freq,
                'current_map_shape': self.current_map_shape,
                'episode_count': self.episode_count,
                'step_count': self.step_count
            }
            
            with open(f"{filepath}_config.json", 'w') as f:
                json.dump(config, f)
            
            print(f"Model saved successfully to {filepath}")
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load(self, filepath):
        """Load a trained model."""
        try:
            # Load configuration
            with open(f"{filepath}_config.json", 'r') as f:
                config = json.load(f)
            
            # Restore configuration
            self.learning_rate = config.get('learning_rate', self.learning_rate)
            self.epsilon = config.get('epsilon', self.epsilon)
            self.epsilon_decay = config.get('epsilon_decay', self.epsilon_decay)
            self.epsilon_min = config.get('epsilon_min', self.epsilon_min)
            self.memory_size = config.get('memory_size', self.memory_size)
            self.batch_size = config.get('batch_size', self.batch_size)
            self.target_update_freq = config.get('target_update_freq', self.target_update_freq)
            self.current_map_shape = config.get('current_map_shape')
            self.episode_count = config.get('episode_count', 0)
            self.step_count = config.get('step_count', 0)
            
            # Initialize networks if we have map shape
            if self.current_map_shape:
                # Create dummy observation to initialize networks
                dummy_obs = {
                    'map': np.zeros(self.current_map_shape),
                    'traverse': 0,
                    'range': 5,
                    'direction': 0,
                    'timeout': 1000
                }
                self._initialize_networks(dummy_obs)
                
                # Load weights
                self.q_network.load_weights(f"{filepath}_weights.h5")
                self.target_network.set_weights(self.q_network.get_weights())
                
                print(f"Model loaded successfully from {filepath}")
            else:
                print("Warning: Map shape not found in config. Networks will be initialized on first use.")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
