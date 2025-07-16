import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from config import settings

class CinemaCollector:
    def __init__(self):
        self.yes_planet_api_key = settings.yes_planet_api_key
        self.cinema_city_api_key = settings.cinema_city_api_key
        
    def get_yes_planet_showtimes(self, date: Optional[str] = None) -> List[Dict]:
        """Get showtimes from Yes Planet Beer Sheva"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        # Yes Planet API endpoint (you'll need to get the actual endpoint)
        url = "https://api.yesplanet.co.il/v1/cinemas/beer-sheva/movies"
        
        headers = {
            'Authorization': f'Bearer {self.yes_planet_api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'date': date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Yes Planet showtimes: {e}")
            return []
    
    def get_cinema_city_showtimes(self, date: Optional[str] = None) -> List[Dict]:
        """Get showtimes from Cinema City Beer Sheva"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        # Cinema City API endpoint (you'll need to get the actual endpoint)
        url = "https://api.cinema-city.co.il/v1/cinemas/beer-sheva/movies"
        
        headers = {
            'Authorization': f'Bearer {self.cinema_city_api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'date': date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Cinema City showtimes: {e}")
            return []
    
    def get_all_showtimes(self, date: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Get showtimes from both cinemas"""
        return {
            'yes_planet': self.get_yes_planet_showtimes(date),
            'cinema_city': self.get_cinema_city_showtimes(date)
        }
    
    def search_movie_showtimes(self, movie_title: str, date: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Search for specific movie showtimes across both cinemas"""
        all_showtimes = self.get_all_showtimes(date)
        
        results = {}
        for cinema, showtimes in all_showtimes.items():
            movie_showtimes = []
            for showtime in showtimes:
                if movie_title.lower() in showtime.get('title', '').lower():
                    movie_showtimes.append(showtime)
            results[cinema] = movie_showtimes
            
        return results
    
    def format_showtime_data(self, showtime_data: Dict) -> Dict:
        """Format showtime data for the RAG system"""
        return {
            'cinema': showtime_data.get('cinema', ''),
            'movie_title': showtime_data.get('title', ''),
            'date': showtime_data.get('date', ''),
            'time': showtime_data.get('time', ''),
            'hall': showtime_data.get('hall', ''),
            'language': showtime_data.get('language', ''),
            'subtitles': showtime_data.get('subtitles', ''),
            'price': showtime_data.get('price', ''),
            'available_seats': showtime_data.get('available_seats', ''),
            'booking_url': showtime_data.get('booking_url', '')
        }

class MockCinemaCollector(CinemaCollector):
    """Mock collector for testing when APIs are not available"""
    
    def get_yes_planet_showtimes(self, date: Optional[str] = None) -> List[Dict]:
        """Mock Yes Planet showtimes"""
        return [
            {
                'cinema': 'Yes Planet Beer Sheva',
                'title': 'The Matrix',
                'date': date or datetime.now().strftime("%Y-%m-%d"),
                'time': '20:00',
                'hall': 'Hall 1',
                'language': 'English',
                'subtitles': 'Hebrew',
                'price': '45 NIS',
                'available_seats': 50,
                'booking_url': 'https://yesplanet.co.il/booking'
            },
            {
                'cinema': 'Yes Planet Beer Sheva',
                'title': 'Inception',
                'date': date or datetime.now().strftime("%Y-%m-%d"),
                'time': '22:30',
                'hall': 'Hall 2',
                'language': 'English',
                'subtitles': 'Hebrew',
                'price': '45 NIS',
                'available_seats': 30,
                'booking_url': 'https://yesplanet.co.il/booking'
            }
        ]
    
    def get_cinema_city_showtimes(self, date: Optional[str] = None) -> List[Dict]:
        """Mock Cinema City showtimes"""
        return [
            {
                'cinema': 'Cinema City Beer Sheva',
                'title': 'The Dark Knight',
                'date': date or datetime.now().strftime("%Y-%m-%d"),
                'time': '19:30',
                'hall': 'Hall A',
                'language': 'English',
                'subtitles': 'Hebrew',
                'price': '42 NIS',
                'available_seats': 45,
                'booking_url': 'https://cinema-city.co.il/booking'
            },
            {
                'cinema': 'Cinema City Beer Sheva',
                'title': 'Interstellar',
                'date': date or datetime.now().strftime("%Y-%m-%d"),
                'time': '21:00',
                'hall': 'Hall B',
                'language': 'English',
                'subtitles': 'Hebrew',
                'price': '42 NIS',
                'available_seats': 35,
                'booking_url': 'https://cinema-city.co.il/booking'
            }
        ] 