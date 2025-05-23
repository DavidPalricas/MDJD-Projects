from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import googlemaps
import os
import actions.aux_python_modules.utils as utils
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from actions.aux_python_modules.retrieve_locations import RetrieveLocations


class ActionRetrieveLocation(Action):
    """ 
    The ActionRetrieveLocation class (exetends the Action Class from Rasa SDK) 
    is used to extract a location from the user's message and store it in the location slot,
    for using in future interactions, like searching for points of interest in that location.
    
    Attributes:
        retireve_locations: Instance of RetrieveLocations for extraciing a location from user messages.
    """
    
    def __init__(self):
        """ The __init__ method initialize the  attribute of the class."""

        self.retireve_locations = RetrieveLocations.get_instance()
   
    def name(self) -> Text:
        """The name method returns the name of the action.
        
        Returns:
            Text: The name of the action which is used to identify it in the Rasa domain file.
        """

        return "action_retrieve_location"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        The run method executes the location retrieval action.
        
        Args:
            dispatcher: Rasa dispatcher for sending messages
            tracker: Rasa tracker for current conversation state
            domain: Rasa domain configuration
            
        Returns:
            List of SlotSet events if location found, otherwise empty list
        """

        location = self.retireve_locations.get_location(tracker.latest_message.get('text'))

        if location:
            dispatcher.utter_message(text=f"Great! now give me the type of place you want to visit in {location}")
            return [SlotSet("location", location)]
           
        dispatcher.utter_message(text="You have to give me a location first\nI'm not a mind reader! 😜")
        return []
    
class Give_points_of_interest(Action):
    """ 
    Action class for finding and displaying points of interest near a specified location.
    
    Uses Google Maps Places API to find nearby places of specified types and displays
    detailed information including ratings, opening hours, and Google Maps links.
    
    Attributes:
        gmaps (googlemaps.Client): Google Maps client for API requests.
        retireve_locations (RetrieveLocations): Instance of RetrieveLocations for extracting locations from user messages.
    """
    
    def __init__(self):
        """
        The __init__ method Initialize the  Google Maps client atribute (gmaps) with API key 
        and location retriever atibute (retireve_locations).
        """
        
        # Load environment variables from .env file
        load_dotenv()

        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        self.retireve_locations = RetrieveLocations.get_instance()

    def name(self) -> Text:
        """The name method returns the name of the action.
        
        Returns:
            Text: The name of the action which is used to identify it in the Rasa domain file.
        """

        return "action_give_points_of_interest"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        The run method is the main entry point for the action.
        It retrieves the Rasa slots values (location and interest_type) and the user message
        thens calls the get_intretests_points method to find points of interest.
        If the location is updated on the method mentioned above, it will update the location slot in the tracker.
        And if the slot interest_type is not set, it will ask the user to provide it again.
        
        Args:
            dispatcher: Rasa dispatcher for sending messages
            tracker: Rasa tracker for current conversation state
            domain: Rasa domain configuration
            
        Returns:
            List of SlotSet events if location updated, otherwise empty list
        """

        location = tracker.get_slot("location")
        type_of_place = tracker.get_slot("interest_type")

        if not type_of_place:
            dispatcher.utter_message(text="I didn't understand the type of place you want to visit.\n Could you please repeat it?")
            return []
         
        user_messaged = tracker.latest_message.get('text')

        user_name = tracker.get_slot("user_name")
        location_updated = self.get_intretests_points(location, dispatcher, type_of_place, user_messaged, user_name)

        if location_updated:
            return [SlotSet("location", location_updated)]
        return []
    
    def get_intretests_points(self, location: str, dispatcher: CollectingDispatcher, 
                            type_of_place: str, user_messaged: str, user_name: str) -> str:
        """
        The get_intretests_points method retrieves points of interest based on the user's location and type of place requested.
        It uses the Google Maps API to find nearby places and displays the results to the user.

        If the location is not provided by the user(by the slot location or by the user message), it will not search the places, 
        and will ask the user to provide a location first.

        If any error occurs during the process, it will inform the user about it.
        
        Args:
            location: The base location for the search
            dispatcher: Rasa message dispatcher
            type_of_place: Category of places to search for
            user_messaged: Original user message for potential location updates
            user_name: The name of the user
            
        Returns:
            If the location is updated (new location provided in the user's message), it returns the updated location to
            update the location slot in the tracker.
            Otherwise, it returns None.
        """

        location_updated = False

        try: 
            new_location = self.retireve_locations.get_location(user_messaged)

            if new_location: 
                location = new_location
                location_updated = True

            if not location:
                dispatcher.utter_message(text="You have to give me a location first\nI'm not a mind reader! 😜")
                return
        
            coordinates = self.gmaps.geocode(location)

            if not coordinates:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any interest points in {location}.")
                return
            
            type_of_place = self.check_plural(type_of_place)

            places = self.gmaps.places_nearby(
                location=coordinates[0]['geometry']['location'],
                radius=2000,
                type=type_of_place
            )

            if places['results']:
                self.show_results(places['results'], location, dispatcher, user_name)
                return location if location_updated else None
            
            dispatcher.utter_message(text=f"Sorry, I couldn't find any {type_of_place} in {location}.")
              
        except Exception as e:
            print(f"Error: {e}")

            error_message = (
                f"Apologies—I hit a snag while searching for places in **{location}**. "  
                "This might be a temporary issue. "  
                "Could you double-check the name or try again in a moment? 🌐"  
            )
            dispatcher.utter_message(text=error_message)

    def show_results(self, places: List[Dict], location: str, dispatcher: CollectingDispatcher, user_name: str):
        """
        The show_results method lists the best palces by rating found in the location given by the user.
        It shows the name, address, rating, link to Google Maps, total reviews and if the place is open or not.
        
        Args:
            places: List of place dictionaries from Google Maps API
            location: The search location
            dispatcher: Rasa message dispatcher
            user_name: The name of the user
        """

        divisory_line = f"{'=' * 100}\n"
        best_places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
        
        response =  f" {user_name} I have found the best places for you in {location}:\n{divisory_line}" if user_name else f"I have found the best places for you in {location}:\n{divisory_line}"
        
        MAX_STARS_GOOGLE_MAPS = 5.0
        MAX_PLACES_TO_SHOW = 10

        for i, place in enumerate(best_places[:MAX_PLACES_TO_SHOW], 1):
            response += (
                f"{i}️⃣ {place['name']}\n"
                f"📍 Address: {place['vicinity']}\n"
                f"🌟 Rating: {utils.get_rating_stars(place.get('rating', None),MAX_STARS_GOOGLE_MAPS)}\n"
                f"👥 Reviews: {place.get('user_ratings_total', 'N/A')}\n"
                f"🔗 Map link: https://www.google.com/maps/place/?q=place_id:{place['place_id']}\n"
            )
            
            if 'opening_hours' in place:
                response += "🟢 OPEN NOW!\n" if place['opening_hours'].get('open_now', False) else "🔴 CURRENTLY CLOSED\n"
            else:
                response += "🟡 HOURS UNKNOWN\n"
            
            response += divisory_line

        dispatcher.utter_message(text=response)

    def check_plural(self, type_of_place: str) -> str:
        """
        The check_plural methods check if the value of the slot type_of_place is in the plural form or not.
        if its is, it is coverted to the singular form, to be used in the Google Maps API.
        
        Args:
            type_of_place: The place type to check
            
        Returns:
            The singular form of the value of the type_of_place slot
        """
        type_of_place_singular_map = {
            'hotels': 'hotel', 'hostels': 'hostel', 'motels': 'motel', 'restaurants': 'restaurant',
            'cafes': 'cafe', 'diners': 'diner', 'bakeries': 'bakery', 'museums': 'museum',
            'art galleries': 'art gallery', 'tourist attractions': 'tourist attraction',
            'landmarks': 'landmark', 'pharmacies': 'pharmacy', 'drugstores': 'drugstore',
            'hospitals': 'hospital', 'clinics': 'clinic', 'shopping malls': 'shopping mall',
            'supermarkets': 'supermarket', 'convenience stores': 'convenience store',
            'parks': 'park', 'zoos': 'zoo', 'aquariums': 'aquarium', 'cinemas': 'cinema',
            'movie theaters': 'movie theater', 'airports': 'airport', 'train stations': 'train station',
            'bus stations': 'bus station', 'subways': 'subway', 'gas stations': 'gas station',
            'atms': 'atm', 'banks': 'bank', 'churches': 'church', 'temples': 'temple',
            'mosques': 'mosque', 'stadiums': 'stadium', 'gyms': 'gym', 'spas': 'spa'
        }
        
        return type_of_place_singular_map.get(type_of_place, type_of_place)