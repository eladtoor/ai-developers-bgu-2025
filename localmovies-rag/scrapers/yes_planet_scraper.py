import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class YesPlanetScraper:
    def __init__(self):
        self.base_url = "https://www.yesplanet.co.il"
        self.beer_sheva_url = "https://www.planetcinema.co.il/cinemas/beersheva/1074"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_movies_data(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get all movies showing in Yes Planet Beer Sheva for the next N days
        """
        movies_data = []
        
        # Get current date and iterate through the next N days
        current_date = datetime.now()
        
        for i in range(days_ahead):
            target_date = current_date + timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            print(f"Scraping movies for date: {date_str}")
            
            try:
                # Get movies for this specific date
                daily_movies = self._get_movies_for_date(target_date)
                movies_data.extend(daily_movies)
                
                # Small delay to be respectful to the server
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping for date {date_str}: {e}")
                continue
        
        # Remove duplicates and organize data
        return self._deduplicate_movies(movies_data)
    
    def _get_movies_for_date(self, date: datetime) -> List[Dict]:
        """
        Get movies showing on a specific date
        """
        # Yes Planet uses a specific URL structure for dates
        date_str = date.strftime("%Y-%m-%d")
        
        # Try different URL patterns that Yes Planet might use
        possible_urls = [
            f"{self.beer_sheva_url}?date={date_str}",
            f"{self.beer_sheva_url}/movies?date={date_str}",
            f"{self.base_url}/movies/beer-sheva?date={date_str}"
        ]
        
        for url in possible_urls:
            try:
                movies = self._scrape_movies_from_url(url, date)
                if movies:
                    return movies
            except Exception as e:
                print(f"Failed to scrape from {url}: {e}")
                continue
        
        # If all URLs fail, try the main page
        return self._scrape_movies_from_main_page(date)
    
    def _scrape_movies_from_url(self, url: str, date: datetime) -> List[Dict]:
        """
        Scrape movies from a specific URL
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_movies_from_soup(soup, date)
            
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return []
    
    def _scrape_movies_from_main_page(self, date: datetime) -> List[Dict]:
        """
        Scrape movies from the main Yes Planet Beer Sheva page
        """
        try:
            response = self.session.get(self.beer_sheva_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_movies_from_soup(soup, date)
            
        except requests.RequestException as e:
            print(f"Request failed for main page: {e}")
            return []
    
    def _extract_movies_from_soup(self, soup: BeautifulSoup, date: datetime) -> List[Dict]:
        """
        Extract movie data from BeautifulSoup object
        """
        movies = []
        
        # Common selectors for movie elements on Yes Planet
        movie_selectors = [
            '.movie-item',
            '.movie-card',
            '.film-item',
            '.movie',
            '[data-movie]',
            '.movie-container'
        ]
        
        movie_elements = []
        for selector in movie_selectors:
            movie_elements = soup.select(selector)
            if movie_elements:
                break
        
        if not movie_elements:
            # Try alternative approach - look for movie titles
            movie_elements = soup.find_all(['h1', 'h2', 'h3', 'h4'], 
                                         string=re.compile(r'.*', re.IGNORECASE))
        
        for element in movie_elements:
            try:
                movie_data = self._extract_movie_from_element(element, date)
                if movie_data:
                    movies.append(movie_data)
            except Exception as e:
                print(f"Error extracting movie from element: {e}")
                continue
        
        return movies
    
    def _extract_movie_from_element(self, element, date: datetime) -> Optional[Dict]:
        """
        Extract movie information from a single element
        """
        # Try to find movie title
        title = self._extract_title(element)
        if not title:
            return None
        
        # Try to find showtimes
        showtimes = self._extract_showtimes(element, date)
        
        # Try to find additional info
        additional_info = self._extract_additional_info(element)
        
        return {
            'title': title,
            'date': date.strftime("%Y-%m-%d"),
            'showtimes': showtimes,
            'cinema': 'Yes Planet Beer Sheva',
            'source_url': self.beer_sheva_url,
            'scraped_at': datetime.now().isoformat(),
            **additional_info
        }
    
    def _extract_title(self, element) -> Optional[str]:
        """
        Extract movie title from element
        """
        # Try multiple approaches to find the title
        title_selectors = [
            '.movie-title',
            '.title',
            'h1', 'h2', 'h3', 'h4',
            '[data-title]',
            '.film-title'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 2:
                    return title
        
        # If no specific selector works, try to get text from the element itself
        text = element.get_text(strip=True)
        if text and len(text) < 100:  # Reasonable title length
            return text
        
        return None
    
    def _extract_showtimes(self, element, date: datetime) -> List[str]:
        """
        Extract showtimes from element
        """
        showtimes = []
        
        # Common selectors for showtimes
        time_selectors = [
            '.showtime',
            '.time',
            '.hour',
            '[data-time]',
            '.movie-time'
        ]
        
        for selector in time_selectors:
            time_elements = element.select(selector)
            for time_elem in time_elements:
                time_text = time_elem.get_text(strip=True)
                if self._is_valid_time(time_text):
                    showtimes.append(time_text)
        
        return showtimes
    
    def _extract_additional_info(self, element) -> Dict:
        """
        Extract additional movie information
        """
        info = {}
        
        # Try to find language/subtitles
        language_selectors = ['.language', '.subtitle', '[data-language]']
        for selector in language_selectors:
            lang_elem = element.select_one(selector)
            if lang_elem:
                info['language'] = lang_elem.get_text(strip=True)
                break
        
        # Try to find hall/auditorium
        hall_selectors = ['.hall', '.auditorium', '[data-hall]']
        for selector in hall_selectors:
            hall_elem = element.select_one(selector)
            if hall_elem:
                info['hall'] = hall_elem.get_text(strip=True)
                break
        
        # Try to find price
        price_selectors = ['.price', '.cost', '[data-price]']
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                info['price'] = price_elem.get_text(strip=True)
                break
        
        return info
    
    def _is_valid_time(self, time_text: str) -> bool:
        """
        Check if a string represents a valid time
        """
        # Common time patterns
        time_patterns = [
            r'\d{1,2}:\d{2}',  # 14:30, 9:15
            r'\d{1,2}:\d{2}\s*(AM|PM)',  # 2:30 PM, 9:15 AM
            r'\d{1,2}:\d{2}\s*(am|pm)',  # 2:30 pm, 9:15 am
        ]
        
        for pattern in time_patterns:
            if re.match(pattern, time_text, re.IGNORECASE):
                return True
        
        return False
    
    def _deduplicate_movies(self, movies: List[Dict]) -> List[Dict]:
        """
        Remove duplicate movies and merge showtimes
        """
        movie_dict = {}
        
        for movie in movies:
            title = movie['title'].lower().strip()
            
            if title in movie_dict:
                # Merge showtimes
                existing_movie = movie_dict[title]
                existing_movie['showtimes'].extend(movie['showtimes'])
                # Remove duplicates from showtimes
                existing_movie['showtimes'] = list(set(existing_movie['showtimes']))
            else:
                movie_dict[title] = movie
        
        return list(movie_dict.values())
    
    def save_to_json(self, movies: List[Dict], filename: str = None):
        """
        Save scraped data to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yes_planet_movies_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(movies)} movies to {filename}")
    
    def print_summary(self, movies: List[Dict]):
        """
        Print a summary of scraped data
        """
        print(f"\n=== Yes Planet Beer Sheva - Movie Summary ===")
        print(f"Total movies found: {len(movies)}")
        print(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nMovies:")
        
        for movie in movies:
            print(f"- {movie['title']}")
            print(f"  Dates: {movie['date']}")
            print(f"  Showtimes: {', '.join(movie['showtimes'])}")
            if 'language' in movie:
                print(f"  Language: {movie['language']}")
            print()

# Test the scraper
if __name__ == "__main__":
    scraper = YesPlanetScraper()
    
    print("Starting Yes Planet Beer Sheva scraper...")
    movies = scraper.get_movies_data(days_ahead=3)
    
    scraper.print_summary(movies)
    scraper.save_to_json(movies) 