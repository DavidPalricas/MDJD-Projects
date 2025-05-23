from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime
import pytz

class ActionGetTime(Action):
    """An action to get the current time in a specified location."""

    def get_time_in_location(self, location: str) -> str:
        """Fetch the current time in the specified location.
        If the location is not found, return a message indicating that.
        """
        try:
            # Convert city/country to coordinates using geopy
            geolocator = Nominatim(user_agent="rasa_time_bot")
            geo_data = geolocator.geocode(location)

            # If the location is not found, return a message indicating that
            if not geo_data:
                return f"Sorry, I don't know where {location} is."

            # Get the timezone using timezonefinder
            tf = TimezoneFinder()
            lat, lon = geo_data.latitude, geo_data.longitude
            timezone_str = tf.timezone_at(lng=lon, lat=lat)
            
            # If the timezone is not found, return a message indicating that
            if not timezone_str:
                return f"Sorry, I don't know the timezone for {location} (lat: {lat}, lon: {lon})."

            # Get the proper timezone (with pytz) and return the current time message
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz).strftime("%H:%M:%S %d-%m-%Y")
            return f"The current time in {location} ({timezone_str}) is {current_time}."
        except Exception as e:
            # Handle any exceptions that occur during the process
            return f"An error occurred while getting the time of {location}: {str(e)}"


    def name(self):
        """Name of the action"""
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Fetch the current time for the specified location (default to UTC time)."""
        # Get the location from the entity 'GPE'
        location = next((tracker.get_latest_entity_values("GPE")), None)
        utter_msg = ""
        
        if not location:
            # If no location is provided, use the default UTC time
            utc_time = datetime.now(pytz.utc).strftime("%H:%M:%S %d-%m-%Y")
            utter_msg = f"The current time in UTC is {utc_time}."
        else:
            utter_msg = self.get_time_in_location(location)
        
        dispatcher.utter_message(text=utter_msg)
        return []
        