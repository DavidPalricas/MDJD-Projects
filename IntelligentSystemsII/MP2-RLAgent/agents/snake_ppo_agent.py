import numpy as np
import tensorflow as tf
import os

from tf_agents.agents.ppo import ppo_agent
from tf_agents.networks import actor_distribution_network, value_network
from tf_agents import trajectories
from tf_agents.trajectories import policy_step
from tf_agents.environments import tf_py_environment

from agents.snake_base_agent import SnakeBaseAgent


@tf.keras.utils.register_keras_serializable()
class Clip0To10Layer(tf.keras.layers.Layer):
    def call(self, inputs):
        x = tf.cast(inputs, tf.float32)
        return tf.clip_by_value(x, 0, 10)

@tf.keras.utils.register_keras_serializable()
class CastFloat32Layer(tf.keras.layers.Layer):
    def call(self, inputs):
        return tf.cast(inputs, tf.float32)

@tf.keras.utils.register_keras_serializable()
class Scale1000Layer(tf.keras.layers.Layer):
    def call(self, inputs):
        return tf.cast(inputs, tf.float32) / 1000.0

@tf.keras.utils.register_keras_serializable()
class Scale100Layer(tf.keras.layers.Layer):
    def call(self, inputs):
        return tf.cast(inputs, tf.float32) / 100.0


class PPOAgent(SnakeBaseAgent):
    def __init__(self, env, learning_rate=3e-4, num_epochs=10, batch_size=64,
                 actor_fc_layers=(128, 64), value_fc_layers=(128, 64),
                 collect_steps_per_iteration=128, entropy_regularization=0.01):
        super().__init__(env)

        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.actor_fc_layers = actor_fc_layers
        self.value_fc_layers = value_fc_layers
        self.collect_steps_per_iteration = collect_steps_per_iteration
        self.entropy_regularization = entropy_regularization

        self.tf_env = tf_py_environment.TFPyEnvironment(env)
        self.train_step_counter = tf.Variable(0)

        self.collected_experience = []

        self._initialize_agent()

    def _create_networks(self, observation_spec, action_spec):
        preprocessing_layers = {
            'map': tf.keras.Sequential([
                CastFloat32Layer(),
                tf.keras.layers.Reshape((*observation_spec['map'].shape, 1)),
                tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same'),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same'),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.GlobalAveragePooling2D()
            ]),
            'traverse': tf.keras.Sequential([
                CastFloat32Layer(),
                tf.keras.layers.Embedding(2, 4),
                tf.keras.layers.Flatten()
            ]),
            'range': tf.keras.Sequential([
                Clip0To10Layer(),
                tf.keras.layers.Embedding(11, 4),
                tf.keras.layers.Flatten()
            ]),
            'direction': tf.keras.Sequential([
                CastFloat32Layer(),
                tf.keras.layers.Embedding(4, 4),
                tf.keras.layers.Flatten()
            ]),
            'timeout': tf.keras.Sequential([
                Scale1000Layer(),
                tf.keras.layers.Reshape((1,))
            ]),
            'score': tf.keras.Sequential([
                Scale100Layer(),
                tf.keras.layers.Reshape((1,))
            ])
        }

        preprocessing_combiner = tf.keras.layers.Concatenate()

        actor_net = actor_distribution_network.ActorDistributionNetwork(
            observation_spec,
            action_spec,
            preprocessing_layers=preprocessing_layers,
            preprocessing_combiner=preprocessing_combiner,
            fc_layer_params=self.actor_fc_layers
        )

        value_net = value_network.ValueNetwork(
            observation_spec,
            preprocessing_layers=preprocessing_layers,
            preprocessing_combiner=preprocessing_combiner,
            fc_layer_params=self.value_fc_layers
        )

        return actor_net, value_net

    def _initialize_agent(self):
        observation_spec = self.tf_env.observation_spec()
        action_spec = self.tf_env.action_spec()
        time_step_spec = self.tf_env.time_step_spec()

        self.actor_net, self.value_net = self._create_networks(observation_spec, action_spec)

        optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)

        self.agent = ppo_agent.PPOAgent(
            time_step_spec=time_step_spec,
            action_spec=action_spec,
            optimizer=optimizer,
            actor_net=self.actor_net,
            value_net=self.value_net,
            normalize_observations=False,
            normalize_rewards=False,
            entropy_regularization=self.entropy_regularization,
            importance_ratio_clipping=0.2,
            use_gae=True,
            num_epochs=self.num_epochs,
            train_step_counter=self.train_step_counter
        )
        self.agent.initialize()
        self.collect_policy = self.agent.collect_policy
        self.eval_policy = self.agent.policy

    def get_action(self, time_step, use_exploration_policy=True):
        def preprocess_observation(obs):
            return {
                key: tf.convert_to_tensor(value) if not tf.is_tensor(value) else value
                for key, value in obs.items()
            }

        # Patch the observation
        patched_time_step = time_step._replace(
            observation=preprocess_observation(time_step.observation)
        )

        if use_exploration_policy:
            action_step = self.collect_policy.action(patched_time_step)
        else:
            action_step = self.eval_policy.action(patched_time_step)

        return action_step.action.numpy() if isinstance(action_step.action, tf.Tensor) else action_step.action

    def store_experience(self, time_step, action, next_time_step):
        traj = trajectories.from_transition(time_step, policy_step.PolicyStep(action=action), next_time_step)
        self.collected_experience.append(traj)
        self.step_count += 1

    def train_step(self):
        if not self.collected_experience:
            return None

        experience = tf.nest.map_structure(lambda *x: tf.stack(x), *self.collected_experience)
        experience = tf.nest.map_structure(lambda x: tf.expand_dims(x, axis=1), experience)
        
        loss_info = self.agent.train(experience)
        self.training_losses.append(loss_info.loss.numpy())

        # Clear experience after training
        self.collected_experience = []

        return loss_info.loss.numpy()

    def evaluate(self, num_episodes=5):
        total_reward = 0
        total_score = 0

        for _ in range(num_episodes):
            time_step = self.env.reset()
            episode_reward = 0

            while not time_step.is_last():
                action = self.get_action(time_step, False)
                time_step = self.env.step(action)
                reward = time_step.reward
                if hasattr(reward, 'numpy'):
                    episode_reward += reward.numpy().item()
                else:
                    episode_reward += float(reward)

            try:
                final_score = self.env.get_state().get('score', 0)
            except:
                final_score = 0

            total_reward += episode_reward
            total_score += final_score

        return total_reward / num_episodes, total_score / num_episodes

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
            print(f"Episode {self.episode_count}, Avg Score (last 50): {avg_score:.2f}")

    def get_training_stats(self):
        return {
            'episode_count': self.episode_count,
            'step_count': int(self.train_step_counter.numpy()),
            'avg_loss': np.mean(self.training_losses[-100:]) if self.training_losses else 0.0,
            'avg_score': np.mean(self.scores[-10:]) if self.scores else 0.0,
            'max_score': max(self.scores) if self.scores else 0.0,
        }

    def save(self, filepath):
        if self.agent is None:
            return
        
        ckpt = tf.train.Checkpoint(policy=self.collect_policy)
        ckpt.save(filepath)

    def load(self, filepath):
        ckpt = tf.train.Checkpoint(policy=self.collect_policy)
        ckpt.restore(tf.train.latest_checkpoint(os.path.dirname(filepath))).expect_partial()
