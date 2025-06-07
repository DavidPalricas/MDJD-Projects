"""
Base for all the snake agents.
Authors: [David Palricas, Daniel Emídio, Marcio Tavares]
"""
from abc import ABC, abstractmethod


class SnakeBaseAgent(ABC):
    """
    Abstract base class for Snake agents.
    Defines the interface for agent actions and training.
    """

    def __init__(self, env):
        """
        Initialize the agent with the given environment.

        Args:
            env: The Snake training environment
        """
        self.env = env
    
        # Action space
        self.action_size = 4  # up, down, left, right

        # Training tracking
        self.step_count = 0
        self.episode_count = 0
        self.training_losses = []
        self.episode_rewards = []
        self.scores = []
    

    @abstractmethod
    def get_action(self, time_step, use_exploration_policy=True):
        """
        Get action to take based on the current time step.
        
        Args:
            time_step: Current time step from environment
            use_exploration_policy: Whether to use the exploration policy or the evaluation policy
            
        Returns:
            Action to take (0-3)
        """
        pass

    @abstractmethod
    def store_experience(self, state, action, next_state):
        """
        Store the experience in the agent's memory.

        Args:
            state: Current time step
            action: Action taken
            next_state: Next time step
        """
        pass

    @abstractmethod
    def train_step(self):
        """
        Perform one training step.
        """
        pass

    @abstractmethod
    def on_episode_end(self):
        """
        Called at the end of each episode.
        """
        pass

    @abstractmethod
    def evaluate(self, num_episodes=5):
        """
        Evaluate the agent performance.
        
        Args:
            num_episodes: Number of episodes to evaluate
            
        Returns:
            Average reward over evaluation episodes
        """
        pass

    @abstractmethod
    def get_training_stats(self):
        """
        Get training statistics.
        
        Returns:
            Dictionary of training statistics
        """
        pass

    @abstractmethod
    def save(self, filepath):
        """Save the trained model.
        
        Args:
            filepath: Path to save the model
        """
        pass

    @abstractmethod
    def load(self, filepath):
        """Load a trained model.
        
        Args:
            filepath: Path to load the model from
        """
        pass
