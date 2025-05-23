import spacy

class RetrieveLocations:
    """
    The RetrieveLocations class is a Singleton for extracting location information from text using spaCy NER.
    
    This class implements the singleton pattern to ensure the spacy model is loaded only once.
    
    Attributes:
        _instance: Class attribute holding the singleton instance
        nlp: spaCy language model instance for natural language processing
    """
    
    _instance = None  
    
    @staticmethod
    def get_instance():
        """
        The get_instance Static method is used to get the singleton instance.
        
        Returns:
            RetrieveLocations: The singleton instance of the class
            
        Note:
            Creates a new instance if one doesn't exist.
        """
        if RetrieveLocations._instance is None:
            RetrieveLocations()

        return RetrieveLocations._instance
    
    def __init__(self):
        """
        The __init__ method initializes the singleton instance and loads the spaCy model.
        
        Raises:
            Exception: If attempting to create multiple instances
        """
        if RetrieveLocations._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            RetrieveLocations._instance = self

        self.nlp = spacy.load("en_core_web_lg")

    def get_location(self, user_message: str) -> str:
        """
        The get_location method extracts the first location from the user message using Named Entity Recognition (NER).
 
        Args:
            user_message: Input text to analyze for locations
            
        Returns:
            str: The first detected location, or None if no locations found
            
        Note:
            Recognizes entities with labels "GPE" (Geo-Political Entity) and "LOC" (Location)
            It also only returns the first location found in the text, becuase in the context of this project,
            the users must only provide one location in their interaction with the assistant.
        """
        
        doc = self.nlp(user_message)
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]

        if locations:
            return locations[0]
        
        return None