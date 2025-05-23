from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime

class ActionAge(Action):
    """ 
    The ActionAge class (exetends the Action Class from Rasa SDK) 
    is used to provide the age of the assistant and its birthday date to the user.
    
    Attributes:
        retireve_locations: Instance of RetrieveLocations for extraciing a location from user messages.
    """
   
    def name(self) -> Text:
        """The name method returns the name of the action.
        
        Returns:
            Text: The name of the action which is used to identify it in the Rasa domain file.
        """

        return "action_give_age"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        The run method is the main entry point for the action.
        It gets the current date and calculates the age of the assisntant based on its day of creation.

        Then sends a message to the user with its age and birthday date.
        
        Args:
            dispatcher: Rasa dispatcher for sending messages
            tracker: Rasa tracker for current conversation state
            domain: Rasa domain configuration
            
        Returns:
            List of SlotSet events if location found, otherwise empty list
        """
        
        # Th day when the assistant was created.
        CHILL_DETI_DUDE_BIRTHDAY = datetime(2025, 3, 26)  

        today = datetime.now()
        age = today.year - CHILL_DETI_DUDE_BIRTHDAY.year
 
        if (today.month, today.day) <= (CHILL_DETI_DUDE_BIRTHDAY.month, CHILL_DETI_DUDE_BIRTHDAY.day):
            age -= 1
        
        response = f"I am {age} years old!" if age > 0 else "I was born this year, I am just a little baby !\n"

        response += "🎉 My birthday is on March 26, 2025, if you want to know.\n"

        dispatcher.utter_message(text=response)

        return []