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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class PlanetCinemaScraper:
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.planetcinema.co.il"
        self.beer_sheva_url = "https://www.planetcinema.co.il/cinemas/beersheva/1074"
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--log-level=3")  # Suppress Chrome logs
        
        try:
            # Try to use webdriver_manager to automatically download ChromeDriver
            service = Service(ChromeDriverManager().install(), log_path='NUL')  # Suppress ChromeDriver logs
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Warning: Could not use webdriver_manager: {e}")
            print("Trying to use system ChromeDriver...")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                print(f"Error setting up ChromeDriver: {e2}")
                print("Please make sure ChromeDriver is installed and in your PATH")
                raise
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def get_movies_data(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get all movies showing in Planet Cinema Beer Sheva for the next N days
        """
        if not self.driver:
            self.setup_driver()
        
        try:
            movies_data = []
            current_date = datetime.now()
            
            print(f"Starting to scrape {days_ahead} days from {current_date.strftime('%Y-%m-%d')}")
            
            for i in range(days_ahead):
                target_date = current_date + timedelta(days=i)
                date_str = target_date.strftime("%Y-%m-%d")
                
                print(f"\n=== Scraping movies for date: {date_str} (day {i+1}/{days_ahead}) ===")
                
                try:
                    daily_movies = self._get_movies_for_date(target_date)
                    print(f"Found {len(daily_movies)} movies for {date_str}")
                    movies_data.extend(daily_movies)
                    
                    # Small delay to be respectful to the server
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error scraping for date {date_str}: {e}")
                    continue
            
            print(f"\nTotal movies collected: {len(movies_data)}")
            # Remove duplicates and organize data
            final_movies = self._deduplicate_movies(movies_data)
            print(f"After deduplication: {len(final_movies)} unique movies")
            return final_movies
            
        finally:
            self.close_driver()
    
    def _get_movies_for_date(self, date: datetime) -> List[Dict]:
        """
        Get movies showing on a specific date
        """
        date_str = date.strftime("%Y-%m-%d")
        
        # Use the proper URL format for specific dates
        date_url = f"{self.beer_sheva_url}#/buy-tickets-by-cinema?in-cinema=1074&at={date_str}&view-mode=list"
        print(f"Navigating to: {date_url}")
        self.driver.get(date_url)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Handle cookie consent popup if it appears
        self._handle_cookie_consent()
        
        # Wait for content to load (the page might need more time to render the movie list)
        time.sleep(10)
        
        # Try to scroll down to trigger more content loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Scroll back up
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Extract movies from the rendered page
        return self._extract_movies_from_page(date)
    
    def _select_date(self, date_str: str):
        """Try to select a specific date on the page"""
        try:
            # Look for date picker or calendar elements
            date_selectors = [
                'input[type="date"]',
                '.date-picker',
                '.calendar',
                '[data-date]',
                '.date-selector'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    date_element.clear()
                    date_element.send_keys(date_str)
                    print(f"Selected date: {date_str}")
                    return
                except TimeoutException:
                    continue
            
            # If no date picker found, try clicking on date elements
            date_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-date], .date-item, .calendar-day')
            for element in date_elements:
                if date_str in element.get_attribute('data-date') or date_str in element.text:
                    element.click()
                    print(f"Clicked on date: {date_str}")
                    return
                    
        except Exception as e:
            print(f"Date selection failed: {e}")
    
    def _extract_movies_from_page(self, date: datetime) -> List[Dict]:
        """
        Extract movie data from the rendered page
        """
        movies = []
        
        # Wait for movie content to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.movie, .film, [data-movie], .movie-card'))
            )
        except TimeoutException:
            print("No movie elements found, trying alternative selectors...")
        
        # Try multiple selectors for movie containers
        movie_selectors = [
            '.movie',
            '.film',
            '.movie-card',
            '.film-card',
            '[data-movie]',
            '.movie-item',
            '.film-item',
            '.movie-container',
            '.schedule-item',
            '.showtime-item',
            '.card',
            '.item',
            '.element',
            '[class*="movie"]',
            '[class*="film"]',
            '[class*="show"]',
            '[class*="time"]',
            'div', 'article', 'section'
        ]
        
        movie_elements = []
        for selector in movie_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    movie_elements = elements
                    print(f"Found {len(elements)} movie elements with selector: {selector}")
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue
        
        if not movie_elements:
            # Try to find any elements that might contain movie information
            print("No specific movie elements found, searching for any content...")
            movie_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div, article, section, span, p, h1, h2, h3, h4, h5, h6')
            
            # Filter elements that have text content
            movie_elements = [elem for elem in movie_elements if elem.text.strip()]
            print(f"Found {len(movie_elements)} elements with text content")
        
        # Also try to find movie titles directly
        try:
            movie_title_elements = self.driver.find_elements(By.CSS_SELECTOR, '.qb-movie-name')
            if movie_title_elements:
                print(f"Found {len(movie_title_elements)} movie title elements with .qb-movie-name")
                # Add these to the movie elements list
                movie_elements.extend(movie_title_elements)
        except Exception as e:
            print(f"Error finding .qb-movie-name elements: {e}")
        
        for i, element in enumerate(movie_elements):
            try:
                print(f"Processing element {i+1}/{len(movie_elements)}")
                element_text = element.text.strip()[:100] if element.text else "No text"
                print(f"  Element text: {element_text}")
                
                movie_data = self._extract_movie_from_element(element, date)
                if movie_data:
                    print(f"  ✅ Found movie: {movie_data['title']}")
                    movies.append(movie_data)
                else:
                    print(f"  ❌ No movie data extracted")
            except Exception as e:
                print(f"Error extracting movie from element: {e}")
                continue
        
        return movies
    
    def _extract_movie_from_element(self, element, date: datetime) -> Optional[Dict]:
        """
        Extract movie information from a single element
        """
        # Get the element's text content
        element_text = element.text.strip()
        
        # Try to find movie title
        title = self._extract_title_from_element(element)
        if not title:
            return None
        
        # Filter out navigation elements and non-movie content
        if self._is_navigation_element(title):
            return None
        
        # Try to find showtimes
        showtimes = self._extract_showtimes_from_element(element)
        
        # Include the movie even if no showtimes found, as long as it's a valid title
        if not self._is_likely_movie_title(title):
            return None
        
        # Try to find additional info
        additional_info = self._extract_additional_info_from_element(element)
        
        return {
            'title': title,
            'date': date.strftime("%Y-%m-%d"),
            'showtimes': showtimes,
            'cinema': 'Planet Cinema Beer Sheva',
            'source_url': self.beer_sheva_url,
            'scraped_at': datetime.now().isoformat(),
            **additional_info
        }
    
    def _extract_title_from_element(self, element) -> Optional[str]:
        """
        Extract movie title from element
        """
        # Try multiple approaches to find the title
        title_selectors = [
            '.qb-movie-name',  # Found in the HTML - this is the correct selector
            '.movie-title',
            '.film-title',
            '.title',
            'h1', 'h2', 'h3', 'h4', 'h5',
            '[data-title]',
            '[data-movie-title]',
            '.movie-name',
            '.film-name'
        ]
        
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title and len(title) > 2 and len(title) < 100:
                    return title
            except NoSuchElementException:
                continue
        
        # If no specific selector works, try to get text from the element itself
        text = element.text.strip()
        if text and len(text) < 200:  # Reasonable title length
            # Try to extract just the first line as title
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                potential_title = lines[0]
                if len(potential_title) > 2 and len(potential_title) < 100:
                    # Check if it's not a navigation element
                    if not self._is_navigation_element(potential_title):
                        return potential_title
        
        return None
    
    def _extract_showtimes_from_element(self, element) -> List[str]:
        """
        Extract showtimes from element
        """
        showtimes = []
        
        # Try element-specific selectors first
        time_selectors = [
            '.btn.btn-primary.btn-lg',  # Found in the HTML - showtime buttons
            '.showtime',
            '.time',
            '.hour',
            '[data-time]',
            '.movie-time',
            '.film-time',
            '.screening-time'
        ]
        
        for selector in time_selectors:
            try:
                time_elements = element.find_elements(By.CSS_SELECTOR, selector)
                for time_elem in time_elements:
                    time_text = time_elem.text.strip()
                    if self._is_valid_time(time_text):
                        showtimes.append(time_text)
            except Exception:
                continue
        
        # If no showtimes found in element, try to find nearby showtimes
        if not showtimes:
            try:
                # Look for showtime buttons that are siblings or children of the movie element
                parent = element.find_element(By.XPATH, "..")
                time_elements = parent.find_elements(By.CSS_SELECTOR, '.btn.btn-primary.btn-lg')
                for time_elem in time_elements:
                    time_text = time_elem.text.strip()
                    if self._is_valid_time(time_text):
                        showtimes.append(time_text)
            except Exception:
                pass
            
            for selector in time_selectors:
                try:
                    time_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for time_elem in time_elements:
                        time_text = time_elem.text.strip()
                        if self._is_valid_time(time_text):
                            showtimes.append(time_text)
                except Exception:
                    continue
        
        # If no specific time elements found, try to extract from text
        if not showtimes:
            element_text = element.text
            # Look for time patterns in the text
            time_patterns = [
                r'\b\d{1,2}:\d{2}\b',  # 14:30, 9:15
                r'\b\d{1,2}:\d{2}\s*(AM|PM)\b',  # 2:30 PM, 9:15 AM
                r'\b\d{1,2}:\d{2}\s*(am|pm)\b',  # 2:30 pm, 9:15 am
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, element_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        time_str = match[0] + ' ' + match[1] if match[1] else match[0]
                    else:
                        time_str = match
                    if self._is_valid_time(time_str):
                        showtimes.append(time_str)
        
        return list(set(showtimes))  # Remove duplicates
    
    def _extract_additional_info_from_element(self, element) -> Dict:
        """
        Extract additional movie information
        """
        info = {}
        
        # Try to find language/subtitles
        language_selectors = ['.language', '.subtitle', '[data-language]', '.dubbing']
        for selector in language_selectors:
            try:
                lang_elem = element.find_element(By.CSS_SELECTOR, selector)
                info['language'] = lang_elem.text.strip()
                break
            except NoSuchElementException:
                continue
        
        # Try to find hall/auditorium
        hall_selectors = ['.hall', '.auditorium', '[data-hall]', '.screen']
        for selector in hall_selectors:
            try:
                hall_elem = element.find_element(By.CSS_SELECTOR, selector)
                info['hall'] = hall_elem.text.strip()
                break
            except NoSuchElementException:
                continue
        
        # Try to find price
        price_selectors = ['.price', '.cost', '[data-price]', '.ticket-price']
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                info['price'] = price_elem.text.strip()
                break
            except NoSuchElementException:
                continue
        
        return info
    
    def _is_valid_time(self, time_text: str) -> bool:
        """
        Check if a string represents a valid time
        """
        if not time_text:
            return False
            
        # Common time patterns
        time_patterns = [
            r'^\d{1,2}:\d{2}$',  # 14:30, 9:15
            r'^\d{1,2}:\d{2}\s*(AM|PM)$',  # 2:30 PM, 9:15 AM
            r'^\d{1,2}:\d{2}\s*(am|pm)$',  # 2:30 pm, 9:15 am
        ]
        
        for pattern in time_patterns:
            if re.match(pattern, time_text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_navigation_element(self, title: str) -> bool:
        """
        Check if a title is a navigation element or non-movie content
        """
        navigation_keywords = [
            'דף הבית', 'מה בקולנוע', 'פלאנט באר שבע', 'סרטים', 'מידע כללי',
            'הוראות הגעה', 'שירותים', 'אירועים', 'בחרו', 'בחרו סוג',
            'בחרו סרט', 'היום', 'מחר', 'חמישי', 'שישי', 'שבת', 'ראשון',
            'שני', 'שלישי', 'רביעי', 'VIP', 'BLOG', 'עקבו אחרינו',
            'דברו איתנו', 'קישורים', 'מידע נוסף', 'להורדת האפליקציה',
            'כל הזכויות שמורות', 'נגישות', 'קרא עוד', 'סרטים נוספים',
            'הזמינו כרטיסים', 'לוח הקרנות', 'מה התפריט', 'כנסים ואירועים',
            'יום הולדת', 'הקרנה פרטית', 'טיולים וימי כיף', 'מבצעים',
            'הטבות', 'לקוחות עסקיים', 'ילדים', 'מזנון הקולנוע',
            '2d', '3d', '4d', 'imax', 'screenx', '4dx', 'vip',
            'הגדרות', 'settings', 'cookie', 'cookies',
            'בואו לחגוג', 'סופ\"ש אימה', 'יום הקולנוע',
            '2dscreenx', '4dx2d', 'imax2d'
        ]
        
        title_lower = title.lower()
        for keyword in navigation_keywords:
            if keyword.lower() in title_lower:
                return True
        
        return False
    
    def _is_likely_movie_title(self, title: str) -> bool:
        """
        Check if a title is likely to be a movie title
        """
        # Skip navigation elements
        if self._is_navigation_element(title):
            return False
            
        # Movie titles typically don't contain these patterns
        non_movie_patterns = [
            r'\d{1,2}:\d{2}',  # Time patterns
            r'\d+ דקות',  # Duration patterns
            r'\|',  # Separator patterns
            r'©',  # Copyright symbols
            r'⚡',  # Special characters
            r'https?://',  # URLs
            r'@',  # Email symbols
        ]
        
        for pattern in non_movie_patterns:
            if re.search(pattern, title):
                return False
        
        # Movie titles are typically between 2 and 100 characters (increased limit for Hebrew titles)
        if len(title) < 2 or len(title) > 100:
            return False
        
        # Movie titles don't typically end with common navigation words
        navigation_endings = ['עוד', 'יותר', 'חדש', 'מיוחד', 'חופשי']
        for ending in navigation_endings:
            if title.endswith(ending):
                return False
        
        return True
    
    def _handle_cookie_consent(self):
        """
        Handle cookie consent popup if it appears
        """
        try:
            # Common selectors for cookie consent buttons
            cookie_selectors = [
                'button[data-testid="cookie-accept"]',
                'button[data-testid="accept-cookies"]',
                '.cookie-accept',
                '.accept-cookies',
                '.cookie-consent button',
                '.cookie-banner button',
                '[data-cookie-accept]',
                'button:contains("Accept")',
                'button:contains("אישור")',
                'button:contains("קבל")',
                'button:contains("OK")',
                'button:contains("כן")',
                '.btn-accept',
                '.btn-cookie-accept'
            ]
            
            for selector in cookie_selectors:
                try:
                    # Wait for cookie button to appear
                    cookie_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print("Found cookie consent button, clicking...")
                    cookie_button.click()
                    time.sleep(1)
                    return
                except TimeoutException:
                    continue
            
            # Try to find by text content
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    button_text = button.text.lower()
                    if any(keyword in button_text for keyword in ['accept', 'אישור', 'קבל', 'ok', 'כן', 'agree']):
                        print(f"Found cookie button with text: {button.text}")
                        button.click()
                        time.sleep(1)
                        return
            except Exception as e:
                print(f"Error finding cookie button by text: {e}")
                
        except Exception as e:
            print(f"Cookie consent handling failed: {e}")
            # Continue anyway, the page might work without accepting cookies
    
    def _deduplicate_movies(self, movies: List[Dict]) -> List[Dict]:
        """
        Remove duplicate movies and merge showtimes
        """
        movie_dict = {}
        
        for movie in movies:
            title = movie['title'].lower().strip()
            date = movie['date']
            
            # Create unique key with title and date
            key = f"{title}_{date}"
            
            if key in movie_dict:
                # Merge showtimes for same movie on same date
                existing_movie = movie_dict[key]
                existing_movie['showtimes'].extend(movie['showtimes'])
                # Remove duplicates from showtimes
                existing_movie['showtimes'] = list(set(existing_movie['showtimes']))
            else:
                movie_dict[key] = movie
        
        return list(movie_dict.values())
    
    def save_to_json(self, movies: List[Dict], filename: str = None):
        """
        Save scraped data to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"planet_cinema_movies_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(movies)} movies to {filename}")
    
    def print_summary(self, movies: List[Dict]):
        """
        Print a summary of scraped data
        """
        print(f"\n=== Planet Cinema Beer Sheva - Movie Summary ===")
        print(f"Total movies found: {len(movies)}")
        print(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nMovies:")
        
        for movie in movies:
            print(f"- {movie['title']}")
            print(f"  Date: {movie['date']}")
            print(f"  Showtimes: {', '.join(movie['showtimes'])}")
            if 'language' in movie:
                print(f"  Language: {movie['language']}")
            if 'hall' in movie:
                print(f"  Hall: {movie['hall']}")
            if 'price' in movie:
                print(f"  Price: {movie['price']}")
            print()

# Test the scraper
if __name__ == "__main__":
    scraper = PlanetCinemaScraper(headless=False)  # Set to False to see the browser
    
    print("Starting Planet Cinema Beer Sheva scraper...")
    movies = scraper.get_movies_data(days_ahead=3)
    
    scraper.print_summary(movies)
    scraper.save_to_json(movies) 