from typing import Any, Text, Dict, List
import os
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action

class ActionTellJoke(Action):
    """Action to tell a random joke."""

    def __init__(self):
        """Initialize the action and load jokes from a file."""
        super().__init__()
        self.load_jokes()
    
    def load_jokes(self):
        """Load jokes from a text file."""
        # Load jokes from a text file (jokes.txt in the project directory)
        jokes_file_path = os.path.join(os.path.dirname(__file__), "../jokes.txt")

        try:
            with open(jokes_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                self.jokes = [line.strip() for line in lines if line.strip()]
        except Exception as e:
            print(f"Error loading jokes: {e}")
            self.jokes = ["Sorry, I couldn't find a joke right now."]


    def name(self):
        """Name of the action."""
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Run the action to tell a random joke."""
        # Get a random joke from the list and send it to the user
        joke = random.choice(self.jokes)
        dispatcher.utter_message(joke)
        return []