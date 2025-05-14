import tensorflow as tf
from tf_agents.environments import suite_gym
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.agents.dqn.dqn_agent import DqnAgent
from tf_agents.networks.q_network import QNetwork
from tf_agents.drivers.dynamic_step_driver import DynamicStepDriver
from tf_agents.replay_buffers.tf_uniform_replay_buffer import TFUniformReplayBuffer
from tf_agents.utils.common import function
from tf_agents.policies import PolicySaver
from tf_agents.metrics import tf_metrics


# Environment name + policy directory
env_name = "CartPole-v1"
policy_dir = "saved_policy"
log_dir = "logs"  # Directory for TensorBoard logs

# Training parameters
num_iterations = 10000 # Training iterations
collect_steps_per_iteration = 1
eval_interval = 1000


def _setup():
    # 1. Configure the environment
    train_env = TFPyEnvironment(suite_gym.load(env_name))  # Training environment
    eval_env = suite_gym.load(env_name)  # Evaluation environment (non-TF)

    # Define the metrics + TensorBoard writer
    train_metrics = [
        tf_metrics.NumberOfEpisodes(),
        tf_metrics.EnvironmentSteps(),
        tf_metrics.AverageReturnMetric(),
        tf_metrics.AverageEpisodeLengthMetric(),
    ]
    train_summary_writer = tf.summary.create_file_writer(log_dir)
    train_summary_writer.set_as_default()


    # 2. Create the Q network and agent
    fc_layer_params = (100,)  # Neural network parameters

    q_net = QNetwork(
        train_env.observation_spec(),
        train_env.action_spec(),
        fc_layer_params=fc_layer_params
    )

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
    global_step = tf.compat.v1.train.get_or_create_global_step()

    agent = DqnAgent(
        train_env.time_step_spec(),
        train_env.action_spec(),
        q_network=q_net,
        optimizer=optimizer,
        td_errors_loss_fn=tf.keras.losses.Huber(reduction="none"),
        train_step_counter=global_step
    )
    agent.initialize()


    # 3. Configure the replay buffer and data collection
    replay_buffer = TFUniformReplayBuffer(
        data_spec=agent.collect_data_spec,
        batch_size=train_env.batch_size,
        max_length=10000
    )


    # 4. Driver for data collection + Data collection
    collect_driver = DynamicStepDriver(
        train_env,
        agent.collect_policy,
        # Add batch to the replay buffer + update metrics 
        observers=[replay_buffer.add_batch] + train_metrics, 
        num_steps=collect_steps_per_iteration
    )
    collect_driver.run()

    # Create training dataset from replay buffer
    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=64,
        num_steps=2
    ).prefetch(3)
    iterator = iter(dataset)

    return agent, train_env, eval_env, collect_driver, iterator, global_step, train_metrics


def _calculate_avg_return(train_env, eval_env, agent, num_episodes=10):
    avg_return = 0

    for _ in range(num_episodes):
        time_step = eval_env.reset()
        episode_return = 0

        while not time_step.is_last():
            action_step = agent.policy.action(train_env.current_time_step())
            time_step = eval_env.step(action_step.action.numpy()[0])
            episode_return += time_step[1]  # Reward

        avg_return += episode_return

    return avg_return / num_episodes


def _training_loop(agent, train_env, eval_env, collect_driver, iterator, global_step, train_metrics):
    # 5. Training loop
    agent.train = function(agent.train)
    returns = []

    for iteration in range(num_iterations):
        # Collect data from the environment
        collect_driver.run()

        # Train the agent with the replay buffer
        experience, _ = next(iterator)
        train_loss = agent.train(experience).loss

        # Log the loss + metrics
        with tf.name_scope('Losses'):
            tf.summary.scalar('loss', train_loss, step=global_step)
        for metric in train_metrics:
            metric.tf_summaries(train_step=global_step)

        # Evaluate the agent periodically
        if iteration % eval_interval == 0:
            avg_return = _calculate_avg_return(train_env, eval_env, agent)
            returns.append(avg_return)

            print(f"Iteration: {iteration}, Average Return: {avg_return}")


def _save_policy(agent):
    # 6. Save the policy
    tf_policy_saver = PolicySaver(agent.policy)
    tf_policy_saver.save(policy_dir)


def train():
    variables = _setup()
    _training_loop(*variables)
    _save_policy(variables[0]) # variables[0] is the agent

    print(f"Training of {num_iterations} iterations completed.")
    print(f"Policy saved to {policy_dir}.")
    print(f"To visualize metrics, run: tensorboard --logdir {log_dir}")


if __name__ == "__main__":
    train()
