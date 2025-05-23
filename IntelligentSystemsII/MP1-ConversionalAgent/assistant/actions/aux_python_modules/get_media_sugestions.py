import pandas as pd
import tmdbsimple as tmdb  
from dotenv import load_dotenv
import os
from typing import Dict, List, Any

class GetMediaSugestions:
    """
    The GetMediaSugestion class is a Singleton that provides media suggestions by combining IMDB and TMDB data.

    This class implements the singleton pattern to ensure that only one instance of the class exists, to
    the data sets being loaded only once, and to the TMDB API key being set only once.
    
    This class handles the retrieval of movie/TV series recommendations based on genre,
    combining rating data from IMDB with additional metadata from TMDB.

    Attributes:
        _instance: Class attribute holding the singleton instance
        basic_IMDB_ds: DataFrame containing basic IMDB dataset
        ratings_IMDB_ds: DataFrame containing IMDB ratings dataset

    """
    _instance = None  # Class variable to store the singleton instance
    
    @staticmethod
    def get_instance():
        """
        The get_instance Static method is used to get the singleton instance of the class.
        
        Returns:
            GetMediaSugestions: The singleton instance of the class.

        Note:
            Creates a new instance if one doesn't exist.
        """
        if GetMediaSugestions._instance is None:
            GetMediaSugestions()

        return GetMediaSugestions._instance
    
    def __init__(self):
        """
        The __init__ method initializes the singleton instance and loads the IMDB datasets
        (class atributes) and the TMDB API key is set by loading the environment variable.
        
        Raises:
            Exception: If an attempt is made to create a second instance.
        """

        if GetMediaSugestions._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GetMediaSugestions._instance = self
        
        # Load environment variables
        load_dotenv()
        tmdb.API_KEY = os.getenv("TMDB_API_KEY")  

        BASIC_IMDB_DS = os.path.join(os.path.dirname(__file__), "../../../IMDBDDatasets/title.basics.tsv.gz")
        self.basic_IMDB_ds = pd.read_csv(BASIC_IMDB_DS, sep='\t', low_memory=False, na_values='\\N')
        
        RATINGS_IMDB_DS = os.path.join(os.path.dirname(__file__), "../../../IMDBDDatasets/title.ratings.tsv.gz")
        self.ratings_IMDB_ds = pd.read_csv(RATINGS_IMDB_DS, sep='\t')

    def get_tmdb_info(self, title: str, year: int, is_movie: bool) -> Dict[str, Any]:
        """    
        The get_tmd_info method fetches additional media information from TMDB API.
        
        Retrieves synopsis, streaming platforms, and poster URL for a given title.
        
        Args:
            title: The title of the media to search for.
            year: The release year of the media.
            is_movie: Boolean indicating whether the media is a movie (True) or TV series (False).
            
        Returns:
            Dict[str, Any]: Dictionary containing overview, platforms, and poster URL,
                            or None if the request fails.

            None: If no results are found or an error occurs.
        """
        try:
            if is_movie:
                search = tmdb.Search().movie(query=title, year=year)
            else:
                search = tmdb.Search().tv(query=title, first_air_date_year=year)
            
            if not search['results']:
                return None
            
            result = search['results'][0]
            details = tmdb.Movies(result['id']).info() if is_movie else tmdb.TV(result['id']).info()
            
            providers = tmdb.Movies(result['id']).watch_providers() if is_movie else tmdb.TV(result['id']).watch_providers()
            platforms = providers.get('results', {}).get('US', {}).get('flatrate', []) if providers else None
            platform_names = [p['provider_name'] for p in platforms] if platforms else ['Not available in any streaming service']
            
            return {
                'overview': details.get('overview', 'No synopsis available') if details else 'No synopsis available',
                'platforms': platform_names,
                'poster_url': f"https://image.tmdb.org/t/p/w500{result.get('poster_path', '')}"
            }
        except Exception as e:
            print(f"Error while fetching from TMDB: {e}")
            return None

    def get_suggestions(self, genre: str, is_movie: bool) -> List[Dict[str, Any]]:
        """
        The get_suggestions method provides up to 10 random media recommendations based on the specified genre and media type.

        This method filters media by genre, type (movie or TV series), and rating (between 8.0 and 10.0) 
        to ensure high-quality suggestions.
        It combines data from IMDB (for ratings and basic information) with TMDB (for additional metadata) to deliver comprehensive results.

        Args:
            genre (str): The genre to filter by (e.g., 'Comedy', 'Drama').
            is_movie (bool): Indicates whether to search for movies (True) or TV shows (False).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing media suggestions with detailed metadata.
                      Returns None if no matches are found.
        """
        
        title_type = 'movie' if is_movie else 'tvSeries'
        
        MIN_RATING = 8.0
        MAX_RATING = 10.0

        # Filter IMDB dataset, genre, media type and rating
        filtered = self.basic_IMDB_ds[
            (self.basic_IMDB_ds['genres'].str.contains(genre, na=False)) &
            (self.basic_IMDB_ds['titleType'] == title_type)
        ].merge(self.ratings_IMDB_ds, on='tconst', how='left')  
        filtered = filtered[
            (filtered['averageRating'] >= MIN_RATING) & 
            (filtered['averageRating'] <= MAX_RATING) 
        ]
        
        if filtered.empty:
            return None
        
        MAX_SUGGESTIONS = 10

        # Select random suggestions
        suggestions = filtered.sample(n=min(MAX_SUGGESTIONS, len(filtered)))
        
        results = []

        # Joins the IMDB and TMDB data
        for _, row in suggestions.iterrows():
            tmdb_info = self.get_tmdb_info(row['primaryTitle'], row['startYear'], is_movie)

            results.append({
                'title': row['primaryTitle'],
                'year': row['startYear'],
                'genres': row['genres'],
                'imdb_rating': row['averageRating'], 
                'overview': tmdb_info['overview'] if tmdb_info else 'No synopsis available',
                'platforms': tmdb_info['platforms'] if tmdb_info else ["Not available in any streaming service"],
                'poster_url': tmdb_info['poster_url'] if tmdb_info else None
            })
        
        return results