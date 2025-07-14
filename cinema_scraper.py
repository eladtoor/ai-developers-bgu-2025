import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

class CinemaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_yes_planet(self):
        """Scrape movies from Yes Planet Beer Sheva"""
        movies = []
        
        try:
            # Yes Planet Beer Sheva URL (you'll need to find the actual URL)
            url = "https://www.yesplanet.co.il/15/אולמות-קולנוע/באר-שבע"
            
            # For dynamic content, use Selenium
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "movie-item"))  # Adjust selector
            )
            
            # Find movie elements
            movie_elements = driver.find_elements(By.CLASS_NAME, "movie-item")  # Adjust selector
            
            for element in movie_elements:
                try:
                    title = element.find_element(By.CLASS_NAME, "movie-title").text  # Adjust selector
                    
                    # Extract showtimes
                    showtime_elements = element.find_elements(By.CLASS_NAME, "showtime")  # Adjust selector
                    showtimes = [time.text for time in showtime_elements]
                    
                    movies.append({
                        "title": title,
                        "cinema": "Yes Planet",
                        "showtimes": showtimes,
                        "date": time.strftime("%Y-%m-%d")
                    })
                    
                except Exception as e:
                    print(f"Error parsing movie element: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            print(f"Error scraping Yes Planet: {e}")
        
        return movies
    
    def scrape_cinema_city(self):
        """Scrape movies from Cinema City Beer Sheva"""
        movies = []
        
        try:
            # Cinema City Beer Sheva URL (you'll need to find the actual URL)
            url = "https://www.cinema-city.co.il/cinemas/beer-sheva"
            
            # Similar Selenium setup for Cinema City
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "movie"))  # Adjust selector
            )
            
            # Find movie elements
            movie_elements = driver.find_elements(By.CLASS_NAME, "movie")  # Adjust selector
            
            for element in movie_elements:
                try:
                    title = element.find_element(By.CLASS_NAME, "title").text  # Adjust selector
                    
                    # Extract showtimes
                    showtime_elements = element.find_elements(By.CLASS_NAME, "time")  # Adjust selector
                    showtimes = [time.text for time in showtime_elements]
                    
                    movies.append({
                        "title": title,
                        "cinema": "Cinema City",
                        "showtimes": showtimes,
                        "date": time.strftime("%Y-%m-%d")
                    })
                    
                except Exception as e:
                    print(f"Error parsing movie element: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            print(f"Error scraping Cinema City: {e}")
        
        return movies
    
    def clean_movie_title(self, title):
        """Clean movie title for better API matching"""
        # Remove common suffixes
        title = re.sub(r'\s*\([^)]*\)', '', title)  # Remove parentheses content
        title = re.sub(r'\s*\[[^\]]*\]', '', title)  # Remove bracket content
        title = title.strip()
        
        # Remove common movie suffixes
        suffixes_to_remove = [
            ' (Hebrew Subtitles)',
            ' (English Subtitles)',
            ' (Hebrew Dubbed)',
            ' (English Dubbed)',
            ' 3D',
            ' IMAX',
            ' VIP'
        ]
        
        for suffix in suffixes_to_remove:
            title = title.replace(suffix, '')
        
        return title.strip()
    
    def scrape_all_cinemas(self):
        """Scrape all cinema websites and return combined data"""
        print("Scraping Yes Planet...")
        yes_planet_movies = self.scrape_yes_planet()
        
        print("Scraping Cinema City...")
        cinema_city_movies = self.scrape_cinema_city()
        
        # Clean titles for better API matching
        for movie in yes_planet_movies + cinema_city_movies:
            movie['clean_title'] = self.clean_movie_title(movie['title'])
        
        all_movies = yes_planet_movies + cinema_city_movies
        
        print(f"Total movies found: {len(all_movies)}")
        return all_movies

# Example usage
if __name__ == "__main__":
    scraper = CinemaScraper()
    movies = scraper.scrape_all_cinemas()
    
    for movie in movies:
        print(f"Title: {movie['title']}")
        print(f"Clean Title: {movie['clean_title']}")
        print(f"Cinema: {movie['cinema']}")
        print(f"Showtimes: {movie['showtimes']}")
        print("-" * 50) 