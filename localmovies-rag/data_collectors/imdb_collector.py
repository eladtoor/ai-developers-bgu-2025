import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import time
from config import settings

class IMDBCollector:
    def __init__(self):
        self.api_key = settings.omdb_api_key
        self.base_url = "http://www.omdbapi.com/"
        
    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Search for a movie by title and optionally year"""
        params = {
            'apikey': self.api_key,
            't': title,
            'plot': 'full'  # Get full plot
        }
        if year:
            params['y'] = year
            
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'True':
                return data
            else:
                print(f"Movie not found: {title}")
                return None
                
        except requests.RequestException as e:
            print(f"Error fetching movie {title}: {e}")
            return None
    
    def get_movie_by_id(self, imdb_id: str) -> Optional[Dict]:
        """Get movie details by IMDB ID"""
        params = {
            'apikey': self.api_key,
            'i': imdb_id,
            'plot': 'full'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'True':
                return data
            else:
                print(f"Movie not found: {imdb_id}")
                return None
                
        except requests.RequestException as e:
            print(f"Error fetching movie {imdb_id}: {e}")
            return None
    
    def search_movies_by_location(self, location: str) -> List[Dict]:
        """Search for movies filmed in a specific location"""
        # This is a simplified approach - in reality, you'd need a more comprehensive
        # database of filming locations. For now, we'll search for movies that might
        # have been filmed in Beer Sheva based on common patterns
        
        # Common search terms for Beer Sheva movies
        search_terms = [
            f"{location}",
            f"filmed in {location}",
            f"shot in {location}",
            f"{location} location"
        ]
        
        movies = []
        # This is a placeholder - you'd need to implement actual location-based search
        # using a database like IMDB's filming locations or Wikipedia
        
        return movies
    
    def get_movie_ratings(self, movie_data: Dict) -> Dict:
        """Extract ratings from movie data"""
        ratings = {}
        if 'Ratings' in movie_data:
            for rating in movie_data['Ratings']:
                source = rating.get('Source', '')
                value = rating.get('Value', '')
                ratings[source] = value
        
        # Add IMDB rating if available
        if 'imdbRating' in movie_data:
            ratings['IMDB'] = movie_data['imdbRating']
            
        return ratings
    
    def format_movie_data(self, movie_data: Dict) -> Dict:
        """Format movie data for the RAG system"""
        return {
            'title': movie_data.get('Title', ''),
            'year': movie_data.get('Year', ''),
            'imdb_id': movie_data.get('imdbID', ''),
            'plot': movie_data.get('Plot', ''),
            'director': movie_data.get('Director', ''),
            'actors': movie_data.get('Actors', ''),
            'genre': movie_data.get('Genre', ''),
            'ratings': self.get_movie_ratings(movie_data),
            'runtime': movie_data.get('Runtime', ''),
            'language': movie_data.get('Language', ''),
            'country': movie_data.get('Country', ''),
            'awards': movie_data.get('Awards', ''),
            'poster': movie_data.get('Poster', ''),
            'metascore': movie_data.get('Metascore', ''),
            'box_office': movie_data.get('BoxOffice', ''),
            'production': movie_data.get('Production', ''),
            'website': movie_data.get('Website', ''),
            'response': movie_data.get('Response', ''),
            'error': movie_data.get('Error', '')
        } 