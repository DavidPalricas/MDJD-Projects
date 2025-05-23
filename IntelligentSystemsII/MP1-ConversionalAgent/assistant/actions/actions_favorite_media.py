from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import json

class ActionSetFavoriteMedia(Action):
    """Action to set the user's favorite media."""

    def name(self):
        """Name of the action."""
        return "action_set_favorite_media"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Set the user's favorite media (if provided)."""
        # Extract the media type and name from the tracker
        media_type = next(tracker.get_latest_entity_values("media_type"), None)
        media_name = next(tracker.get_latest_entity_values("media_name"), None)

        # Check if one or both are missing
        if not media_type and not media_name:
            dispatcher.utter_message(text="I didn't get the media type and the name.")
            return []
        elif not media_type:
            dispatcher.utter_message(text=f"I didn't get the media type of {media_name}.")
            return []
        elif not media_name:
            dispatcher.utter_message(text=f"I didn't get the name of the {media_type}.")
            return []
        
        # Inform the user about the media type and name they provided
        dispatcher.utter_message(text=f"I'll remember that your favorite {media_type} is {media_name}.")

        # Get the current favorite media from the slot
        json_fav_media = tracker.get_slot("favorite_media") or "{}"
        fav_media = json.loads(json_fav_media)
        
        # Update the favorite media slot with the new values
        fav_media[media_type] = media_name
        json_fav_media = json.dumps(fav_media)

        return [SlotSet("favorite_media", json_fav_media)]

class ActionShowName(Action):
    """Action to show the user's favorite media."""
    
    def name(self):
        """Name of the action."""
        return "action_show_favorite_media"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Show the user's favorite media (of the specified type)."""
        # Get the media type from the tracker
        media_type = next(tracker.get_latest_entity_values("media_type"), None)

        # Check if the media type is missing
        if not media_type:
            dispatcher.utter_message(text="I didn't get the media type.")
            return []

        # Get the favorite media from the slot
        json_fav_media = tracker.get_slot("favorite_media") or "{}"
        fav_media = json.loads(json_fav_media)

        # Check if the media type is in the favorite media
        if media_type not in fav_media:
            dispatcher.utter_message(text=f"You haven't set a favorite {media_type} yet.")
            return []
        
        # Get the favorite media name
        media_name = fav_media[media_type]
        dispatcher.utter_message(text=f"Your favorite {media_type} is {media_name}.")
        return []
