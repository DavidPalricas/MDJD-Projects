import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts


class SnakeTrainEnv(py_environment.PyEnvironment):
    """TF-Agents environment wrapper for Snake game."""
    
    def __init__(self):
        self._grid_sizeY = 48  # Default size
        self._grid_sizeX = 24  # Default size
        self._timeout = 3000   # Default timeout

        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=3, name='action')
        
        # Initialize observation spec with default values
        self._observation_spec = self._create_observation_spec((self._grid_sizeY, self._grid_sizeX), self._timeout)
        
        # Game state
        self._episode_ended = False
        self._is_game_over = False
        self._last_score = 0
        self._previous_distance = None
        self._state = {}  # Store the complete game state
        self._action = None
        self._steps_without_food = 0
        self._steps_in_episode = 0
        
        # Exploration tracking
        self._visited_positions = set()

        # Initialize observation dictionary with default values
        self._observation = self._create_default_observation()

    def _create_observation_spec(self, map_shape, timeout):
        """Create observation spec with given parameters."""
        return {
            'map': array_spec.BoundedArraySpec(
                shape=map_shape, 
                dtype=np.int32,   
                minimum=0, 
                maximum=4, 
                name='map'),
            'traverse': array_spec.BoundedArraySpec(
                shape=(), 
                dtype=np.int32,
                minimum=0,
                maximum=1,
                name='traverse'),
            'range': array_spec.ArraySpec(
                shape=(), 
                dtype=np.int32,
                name='range'),
            'direction': array_spec.BoundedArraySpec(
                shape=(), 
                dtype=np.int32,
                minimum=0,
                maximum=3,  
                name='direction'),
            'timeout': array_spec.BoundedArraySpec(
                shape=(), 
                dtype=np.int32,
                minimum=0,
                maximum=timeout,
                name='timeout'),
            'score': array_spec.ArraySpec(
                shape=(), 
                dtype=np.int32,
                name='score')
        }

    def _create_default_observation(self):
        """Create default observation dictionary."""
        return {
            'map': np.zeros((self._grid_sizeY, self._grid_sizeX), dtype=np.int32),
            'traverse': np.int32(0),
            'range': np.int32(1),
            'direction': np.int32(0),
            'timeout': np.int32(self._timeout),
            'score': np.int32(0)
        }

    def action_spec(self):
        """Return the action spec."""
        return self._action_spec
    
    def observation_spec(self):
        """Return the observation spec."""
        return self._observation_spec
    

    def call_reset(self, map_dict):
        """Reset the environment and return the initial observation."""
        # CORREÇÃO: Validar entrada
        if map_dict is None:
            print("Warning: map_dict is None, using default state")
            map_dict = {}
        
        self._state = map_dict
        return self._reset()
    
    def _reset(self):
        # Reset episode state
        self._episode_ended = False
        self._is_game_over = False
        self._last_score = 0
        self._action = None
        self._previous_distance = None
        self._steps_without_food = 0
        self._steps_in_episode = 0
        
        # Reset exploration tracking
        self._visited_positions = set()
        
        try:
            # CORREÇÃO: Validar se _state tem as chaves necessárias
            if not self._state or 'size' not in self._state:
                print("Warning: Invalid state, using defaults")
                self._state = {
                    'size': [self._grid_sizeY, self._grid_sizeX],
                    'timeout': self._timeout,
                    'map': [],
                    'body': [[0, 0]],  # Default snake position
                    'score': 0
                }
            
            # Update environment dimensions if they changed
            new_grid_sizeY = self._state['size'][0]
            new_grid_sizeX = self._state['size'][1]
            new_timeout = self._state.get('timeout', self._timeout)
            
            # Check if dimensions changed
            dimensions_changed = (
                new_grid_sizeY != self._grid_sizeY or 
                new_grid_sizeX != self._grid_sizeX or 
                new_timeout != self._timeout
            )
            
            if dimensions_changed:
                print(f"Environment dimensions changed: {(self._grid_sizeY, self._grid_sizeX)} -> {(new_grid_sizeY, new_grid_sizeX)}")
                self._grid_sizeY = new_grid_sizeY
                self._grid_sizeX = new_grid_sizeX
                self._timeout = new_timeout

                # Update observation spec
                self._observation_spec = self._create_observation_spec(
                    (self._grid_sizeY, self._grid_sizeX), self._timeout)
            
            # Create new observation with correct dimensions
            self._observation = {
                'map': np.array(self._state.get('map', []), dtype=np.int32) if self._state.get('map') else np.zeros((self._grid_sizeY, self._grid_sizeX), dtype=np.int32),
                'traverse': np.int32(self._state.get('traverse', 0)),
                'range': np.int32(self._state.get('range', 1)),
                'direction': np.int32(0),  # Reset direction
                'timeout': np.int32(self._state.get('timeout', self._timeout)),
                'score': np.int32(self._state.get('score', 0))
            }
            
            # Ensure map has correct shape
            if self._observation['map'].shape != (self._grid_sizeY, self._grid_sizeX):
                print(f"Warning: Map shape mismatch. Expected {(self._grid_sizeY, self._grid_sizeX)}, got {self._observation['map'].shape}")
                # Resize or pad the map if necessary
                current_map = self._observation['map']
                new_map = np.zeros((self._grid_sizeY, self._grid_sizeX), dtype=np.int32)
                
                if current_map.size > 0:  # CORREÇÃO: Verificar se o array não está vazio
                    # Copy what fits
                    copy_rows = min(current_map.shape[0], self._grid_sizeY)
                    copy_cols = min(current_map.shape[1], self._grid_sizeX)
                    new_map[:copy_rows, :copy_cols] = current_map[:copy_rows, :copy_cols]
                
                self._observation['map'] = new_map
            
            # Initialize distance to fruit
            fruit_pos = self._find_fruit_position()
            if fruit_pos is not None:
                # CORREÇÃO: Validar se body existe e não está vazio
                snake_body = self._state.get('body', [[0, 0]])
                if snake_body and len(snake_body) > 0:
                    snake_head = snake_body[0]
                    head_x, head_y = snake_head[1], snake_head[0]  # Convert to x, y
                    fruit_x, fruit_y = fruit_pos[0], fruit_pos[1]
                    self._previous_distance = abs(head_x - fruit_x) + abs(head_y - fruit_y)
            
        except Exception as e:
            print(f"Error in reset: {e}")
            # Use default observation if getting new state fails
            self._observation = self._create_default_observation()
            self._state = {
                'size': [self._grid_sizeY, self._grid_sizeX],
                'timeout': self._timeout,
                'map': [],
                'body': [[0, 0]],
                'score': 0
            }
            
        return ts.restart(self._observation)
    
    def call_step(self, state, action):
        """Take a step in the environment with the given action.
        
        Args:
            state: The current state of the game.
            action: An integer representing one of four directions (0=up, 1=down, 2=left, 3=right).
            
        Returns:
            time_step: The next time step in the environment.
        """
        # CORREÇÃO: Validar entrada
        if state is None:
            print("Warning: state is None in call_step")
            self._episode_ended = True
            return ts.termination(self._observation, -50.0)
        
        self._state = state
        self._action = action
        return self._step()
    
    def _step(self):
        """Take a step in the environment.
        
        Returns:
            time_step: The next time step in the environment.
        """
        if self._episode_ended:
            # If episode has ended, reset the environment
            return self.reset()
        
        try:
            # Update internal state and observation BEFORE calculating reward
            self._update_state()
            
            # Calculate reward AFTER state update
            reward = self._calculate_reward()
                          
            # Check for episode termination
            if self._is_game_over:
                self._episode_ended = True
                return ts.termination(self._observation, reward)
            
            return ts.transition(self._observation, reward, discount=0.99)
            
        except Exception as e:
            print(f"Error in step: {e}")
            print(f"State keys: {list(self._state.keys()) if self._state else 'None'}")
            print(f"Action: {self._action}")
            # Return termination on error
            self._episode_ended = True
            return ts.termination(self._observation, -50.0)
    
    def _calculate_reward(self):
        reward = 0.0
        
        if not self._state:
            return -10.0
        
        game_over_penalty = self._check_game_over_penalty()
        if game_over_penalty != 0:
           return game_over_penalty
        
        food_reward = self._calculate_food_reward()
        reward += food_reward
        
        survival_reward = 0.5  
        reward += survival_reward
        
        distance_reward = self._calculate_distance_reward_fixed()
        reward += distance_reward
        
        danger_penalty = self._calculate_smart_danger_penalty()
        reward += danger_penalty
        
        efficiency_penalty = self._calculate_gentle_efficiency_penalty()
        reward += efficiency_penalty
        
        exploration_bonus = self._calculate_exploration_bonus()
        reward += exploration_bonus
        
        # Normalize reward with wider range for positive rewards
        reward = max(-50, min(reward, 150))
        return float(reward)
    
    def _check_game_over_penalty(self):
        return -100.0 if self._state.get("highscores") is not None else 0.0
  

    def _calculate_food_reward(self):
        current_score = self._state.get('score', 0)
        score_diff = current_score - getattr(self, '_last_score', 0)
        
        if score_diff > 0:
            snake_body = self._state.get('body', [])
            snake_length = len(snake_body) if snake_body else 1
            base_reward = 50.0  
            length_bonus = min(snake_length * 0.5, 10.0)  
            food_reward = base_reward + length_bonus
            
            self._steps_without_food = 0
            self._last_score = current_score
            
            return food_reward
        
        self._last_score = current_score
        return 0.0

    def _calculate_distance_reward_fixed(self):
        snake_body = self._state.get('body', [])
        if not snake_body:
            return 0.0
        
        snake_head = snake_body[0]
        fruit_pos = self._find_fruit_position()
        
        if fruit_pos is None:
            return 0.0
        
        head_y, head_x = snake_head[0], snake_head[1]  
        fruit_y, fruit_x = fruit_pos[1], fruit_pos[0]  
        
        current_distance = abs(head_x - fruit_x) + abs(head_y - fruit_y)
        
        if hasattr(self, '_previous_distance') and self._previous_distance is not None:
            distance_change = self._previous_distance - current_distance
            
            if distance_change > 0:
                distance_reward = 0.1 * distance_change  
            elif distance_change < 0:
                distance_reward = 0.02 * distance_change  
            else:
                distance_reward = 0.0  
        else:
            distance_reward = 0.0
        
        self._previous_distance = current_distance
        return distance_reward

    def _calculate_smart_danger_penalty(self):
        if self._action is None:
            return 0.0
        
        snake_body = self._state.get('body', [])
        if not snake_body:
            return 0.0
            
        snake_head = snake_body[0]
        next_pos = self._get_next_position(snake_head, self._action)
        
        if self._is_position_deadly(next_pos):
            return -8.0 
        
        return 0.0

    def _calculate_gentle_efficiency_penalty(self):
        self._steps_without_food += 1
        
        if self._steps_without_food > 200:  
            excess_steps = self._steps_without_food - 200
            efficiency_penalty = -0.01 * excess_steps * 0.1
            return max(efficiency_penalty, -2.0)  
        
        return 0.0
    
    def _find_fruit_position(self):
        if not hasattr(self, '_observation') or self._observation is None:
            return None
        
        game_map = self._observation.get('map')
        if game_map is None:
            return None
            
        for y in range(len(game_map)):
            for x in range(len(game_map[y])):
                if game_map[y][x] == 2:  
                    return [x, y]  
            
        return None

    def _get_next_position(self, current_pos, action):
        if not current_pos or len(current_pos) < 2:
            return [0, 0]
        
        head_y, head_x = current_pos[0], current_pos[1]
            
        # Actions: 0=up, 1=down, 2=left, 3=right
        if action == 0:    # up
            return [head_y - 1, head_x]
        elif action == 1:  # down
            return [head_y + 1, head_x]
        elif action == 2:  # left
            return [head_y, head_x - 1]
        elif action == 3:  # right
            return [head_y, head_x + 1]
            
        return current_pos

    def _calculate_exploration_bonus(self):
        if not hasattr(self, '_visited_positions'):
            self._visited_positions = set()
        
        snake_body = self._state.get('body', [])
        if not snake_body:
            return 0.0
        
        snake_head = snake_body[0]
        head_pos = tuple(snake_head) 
        
        if head_pos not in self._visited_positions:
            self._visited_positions.add(head_pos)
            return 0.1  
        
        return 0.0

    def _is_position_deadly(self, pos):
        if not pos or len(pos) < 2:
            return True
        
        y, x = pos
        
        if not self._state.get('traverse', False):
            if y < 0 or y >= self._grid_sizeY or x < 0 or x >= self._grid_sizeX:
                return True
        else:
            y = y % self._grid_sizeY
            x = x % self._grid_sizeX
        
        if not (0 <= y < self._grid_sizeY and 0 <= x < self._grid_sizeX):
            return False
        
        if not hasattr(self, '_observation') or self._observation is None:
            return False
        
        game_map = self._observation.get('map')
        if game_map is None:
            return False
        
        if game_map[y][x] == 4:  
            return True
        
        return False
              
    def _update_state(self):
        if not self._state:
            print("Warning: _state is None in _update_state")
            self._is_game_over = True
            return
        
        state_dict = self._state 
        action = self._action 
        
        if state_dict.get("highscores") is not None:
            self._is_game_over = True
            return

        self._observation["range"] = np.int32(state_dict.get("range", 1))
        self._observation["traverse"] = np.int32(state_dict.get("traverse", 0))
        self._observation["score"] = np.int32(state_dict.get("score", 0))
        
        # Calculate remaining timeout
        current_step = state_dict.get("step", 0)
        total_timeout = state_dict.get("timeout", self._timeout)
        remaining_timeout = max(0, total_timeout - current_step)
        self._observation["timeout"] = np.int32(remaining_timeout)
        
        # Store the action taken
        self._observation["direction"] = np.int32(action if action is not None else 0)
        
        # Clear the map first
        current_map = np.zeros((self._grid_sizeY, self._grid_sizeX), dtype=np.int32)
        
        # Update sight information
        sight = state_dict.get('sight', {})
        if sight:
            for x_str, y_dict in sight.items():
                try:
                    x = int(x_str)
                    if 0 <= x < self._grid_sizeX:
                        for y_str, obj_type in y_dict.items():
                            try:
                                y = int(y_str)
                                if 0 <= y < self._grid_sizeY:
                                    # Map object types
                                    mapped_type = min(max(int(obj_type), 0), 4)
                                    if mapped_type <= 4:  # Valid object types
                                        current_map[y, x] = mapped_type
                            except (ValueError, IndexError):
                                continue
                except (ValueError, IndexError):
                    continue
        
        # Update snake body positions (override sight data for snake)
        snake_body = state_dict.get('body', [])
        if snake_body:  
            for i, pos in enumerate(snake_body):
                try:
                    if pos is None or len(pos) < 2:  
                        continue
                    y, x = pos  
                    if 0 <= y < self._grid_sizeY and 0 <= x < self._grid_sizeX:
                        if i == 0:
                            current_map[y, x] = 1  # Head
                        else:
                            current_map[y, x] = 4  # Body
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Error updating snake position {pos}: {e}")
                    continue
        
        self._observation["map"] = current_map

    def get_state(self):
        """Get the current complete game state."""
        return self._state.copy() if self._state else {}
    
    def render(self, mode='human'):
        """Render the environment (optional for debugging)."""
        if mode == 'human':
            print("\nCurrent Map:")
            symbols = {0: '.', 1: 'H', 2: 'F', 3: 'S', 4: 'B'}

            # Print map with row numbers
            for row in range(self._grid_sizeY):
                print(f"{row:2d} ", end="")
                for col in range(self._grid_sizeX):
                    cell_value = self._observation['map'][row][col]
                    print(symbols.get(cell_value, '?'), end="")
                print()