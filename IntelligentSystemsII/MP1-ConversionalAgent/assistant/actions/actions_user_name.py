from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionGreet(Action):
    """Action to greet the user (with or without their name)."""

    def name(self):
        """Name of the action."""
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Greet the user with their name (if provided)."""
        # Get the user's name (entity or slot)
        user_name = next(
            tracker.get_latest_entity_values("PERSON"),
            tracker.get_slot("user_name") or None
        ) 

        # Select the appropriate response based on whether the name is provided or not
        response = "utter_greet_with_name" if user_name else "utter_greet_no_name"
        dispatcher.utter_message(response=response, user_name=user_name)

        # Set the slot to the user's name
        return [SlotSet("user_name", user_name)]

class ActionSetName(Action):
    """Action to set the user's name."""

    def name(self):
        """Name of the action."""
        return "action_set_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Set the user's name and acknowledge it (if provided)."""
        # Get the user's name (entity or slot)
        user_name = next(
            tracker.get_latest_entity_values("PERSON"),
            tracker.get_slot("user_name") or None
        ) 

        # Set the appropriate response based on whether the name is provided or not
        response = "utter_provided_name" if user_name else "utter_ask_user_name"
        dispatcher.utter_message(response=response, user_name=user_name)

        # Set the slot to the user's name
        return [SlotSet("user_name", user_name)]
    
class ActionShowName(Action):
    """Action to show the user's name (if provided)."""
    
    def name(self):
        """Name of the action."""
        return "action_show_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Show the user's name (if provided)."""
        # Get the user's name from the slot
        user_name = tracker.get_slot("user_name") or None

        # Set the appropriate response based on whether the name is provided or not
        response = "utter_show_name" if user_name else "utter_ask_user_name"
        dispatcher.utter_message(response=response, user_name=user_name)

        return []
