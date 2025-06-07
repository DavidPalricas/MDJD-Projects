"""
Logging and WebSocket management for Snake game.
Authors: [David Palricas, Daniel Emídio, Marcio Tavares]
"""
import asyncio
import json
import os
import logging
from datetime import datetime
import websockets


def setup_logging(log_level=logging.INFO, log_file=None):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Default log file with timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'logs/snake_training_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger('SnakeGame')
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


class SnakeGame:
    """Class to manage the Snake game state and communication."""
    
    def __init__(self, logger=None):
        self.first_state = None
        self.message_queue = asyncio.Queue()
        self.listener_task = None
        self.first_state_received = asyncio.Event()
        self.logger = logger or logging.getLogger('SnakeGame')

    async def start_listener(self, websocket):
        """Start the WebSocket listener task."""
        self.listener_task = asyncio.create_task(self.websocket_listener(websocket))
        self.logger.debug("WebSocket listener task started")

    async def stop_listener(self):
        """Stop the WebSocket listener task."""
        if self.listener_task and not self.listener_task.done():
            self.listener_task.cancel()
            try:
                await self.listener_task
                self.logger.debug("WebSocket listener task stopped successfully")
            except asyncio.CancelledError:
                self.logger.debug("WebSocket listener task cancelled")

    async def websocket_listener(self, websocket):
        """Continuously listens for messages and manages first state + queue."""
        try:
            message_count = 0
            async for message in websocket:
                state = json.loads(message)
                message_count += 1
                
                # If this is the first state, set it and signal
                if self.first_state is None:
                    self.first_state = state
                    # self.logger.info(f"First state received: Score={state.get('score', 0)}, Lives={state.get('lives', 0)}")
                    self.first_state_received.set()
                else:
                    # Put subsequent states in the queue
                    await self.message_queue.put(state)
                    if message_count % 100 == 0:  # Log every 100 messages to avoid spam
                        self.logger.debug(f"Processed {message_count} WebSocket messages")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket connection closed in listener")
            await self.message_queue.put(None)
        except Exception as e:
            self.logger.error(f"Error in websocket listener: {e}")
            await self.message_queue.put(None)

    async def wait_for_first_state(self, timeout=10.0):
        """Wait for the first state to be received."""
        try:
            await asyncio.wait_for(self.first_state_received.wait(), timeout=timeout)
            self.logger.debug("First state received successfully")
            return True
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout waiting for first state (timeout={timeout}s)")
            return False

    def get_first_state(self):
        """Get the first state (synchronous)."""
        if self.first_state is None:
            self.logger.error("first_state not received from server")
        return self.first_state

    async def get_state(self):
        """Async method to get the next state from the queue."""
        try:
            state = await self.message_queue.get()
            if state is None:
                raise ConnectionError("WebSocket connection closed or error occurred")
            return state
        except Exception as e:
            self.logger.error(f"Error getting state: {e}")
            raise

    def reset(self):
        """Reset the game state for a new episode."""
        self.logger.debug("Resetting game state")
        self.first_state = None
        # Clear the message queue
        cleared_messages = 0
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
                cleared_messages += 1
            except asyncio.QueueEmpty:
                break
        if cleared_messages > 0:
            self.logger.debug(f"Cleared {cleared_messages} messages from queue")
        self.first_state_received.clear()
