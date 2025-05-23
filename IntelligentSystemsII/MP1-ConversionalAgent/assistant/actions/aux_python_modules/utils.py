import math

def get_rating_stars(rating, max_stars) -> str:
    """
    The get_rating_starts function converts a numerical rating into a visual representation using stars, 
    with an optional half-star for decimal ratings, and includes a reference to the 
    maximum possible rating (e.g., "8.5/10"). 
    If the rating is unavailable, it returns a question mark.

    Args:
        rating (float): The numerical rating to be converted.
        max_stars (int): The maximum possible rating represented by stars.

    Returns:
        str: A string of stars visually representing the rating.
    """
    
    if math.isnan(rating) or rating is None:
        return '❓'
    
    star_rating = '⭐' * int(rating)

    if rating % 1 >= 0.5:
        star_rating += '½'

    star_rating += f" ({rating}/{max_stars})"

    return star_rating