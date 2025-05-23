import actions.aux_python_modules.utils as utils
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.aux_python_modules.get_media_sugestions import GetMediaSugestions


class ActionAskMediaGenre(Action):
    """
    The ActionAskMediaGenre class (extends the Action Class from Rasa SDK)
    is used to ask the user about their preferred media genre.
    This action is triggered when the bot needs to know whether the user wants
    movie or TV series recommendations and asks for their preferred genre.
    """

    def name(self) -> Text:
        """The name method returns the name of the action.
        
        Returns:
            Text: The name of the action which is used to identify it in the Rasa domain file.
        """

        return "action_ask_media_genre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        
        The run method executes the action's main functionality.
        
        Asks the user for their preferred genre based on whether they selected
        movies or TV series.
        
        Args:
            dispatcher: Rasa dispatcher for sending messages
            tracker: Rasa tracker for current conversation state
            domain: Rasa domain configuration
            
        Returns:
            List[Dict[Text, Any]]: An empty list since no slots are set.
        """

        is_movie = tracker.get_slot("is_movie")

        response = "What movie genre are you interested in?" if is_movie else "What TV series genre are you interested in?"

        dispatcher.utter_message(text=response)

        return []


class ActionRecommendMedia(Action):
    """
    The ActionRecommendMedia class (extends the Action Class from Rasa SDK)
    is used to provide media recommendations(movie or tv shows) based on the genre
    the user asked for.

    Atributes:
        get_media_sugestions (GetMediaSugestions): An instance of the GetMediaSugestions class, which is used to fetch media recommendations.
    """

    def __init__(self) -> None:
        """ The __init__ method initialize the  attribute of the class."""

        self.get_media_sugestions = GetMediaSugestions.get_instance()

    def name(self) -> Text:
        """The name method returns the name of the action.
        
        Returns:
            Text: The name of the action which is used to identify it in the Rasa domain file.
        """

        return "action_recommend_media"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """      
        The run method executes the action's main functionality.
        
        Retrieves media recommendations based on the user's selected genre and media type
        (movie or TV series), then formats and sends the response.

        10 results are shown to the user, they are fected from the IMDB's data sets and
        some information like synopsis from the TMDB's API. The results are fetched using the
        get_media_sugestions atribute of this class.
        
        Args:
            dispatcher: Rasa dispatcher for sending messages
            tracker: Rasa tracker for current conversation state
            domain: Rasa domain configuration
            
        Returns:
            List[Dict[Text, Any]]: An empty list since no slots are set.
        """
        is_movie = tracker.get_slot("is_movie")
        genre = tracker.get_slot("media_genre")

        if not genre:
            dispatcher.utter_message(text="Sorry, I couldn't understand the genre you wanted.\nCould you please repeat it?")
            return []
        
        # The genre is capitalized to match the expected format in the IMDB's data sets
        genre = genre.capitalize()

        results = self.get_media_sugestions.get_suggestions(genre, is_movie)

        if not results:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any {genre} {'movies' if is_movie else 'TV series'}.")
            return []
        
        divisory_line = f"{'=' * 100}\n"
              
        user_name = tracker.get_slot("user_name")
        
        response = f"{user_name}, here are the best {genre.lower()} {'movies' if is_movie else 'TV series'} I found for you 😁:\n" if user_name else f"Here are the best {genre.lower()} {'movies' if is_movie else 'TV series'} I found for you 😁:\n"

        response += divisory_line

        MAX_STARS_IMDB = 10.0
     
        for i in range(len(results)):
            result = results[i]

            response += (
                f"{i + 1}🎬 *{result['title']}* ({result['year']})\n"
                f"🍿 Rating {utils.get_rating_stars(result['imdb_rating'], MAX_STARS_IMDB)}\n"
                f"📺 Available on: {', '.join(result.get('platforms', ['Not available in any streaming service']))}\n"
                f"📝 *Synopsis*: {result.get('overview', 'No synopsis available')}\n"
                f"🖼️ Poster: {result.get('poster_url', 'Not available')}\n"
                f"{divisory_line}"
            )
  
        dispatcher.utter_message(text=response)

        return []