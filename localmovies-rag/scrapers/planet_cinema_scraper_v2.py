import time
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Suppress logging
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

class PlanetCinemaScraperV2:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.beer_sheva_url = "https://www.planetcinema.co.il/cinemas/beersheva/1074"
        
    def setup_driver(self):
        """Setup Chrome driver with optimized settings"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Performance and stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Suppress console output
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        
        # User agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Chrome driver setup successful")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            raise
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")
    
    def get_movies_data(self, days_ahead: int = 7) -> List[Dict]:
        """Get movies data for the specified number of days ahead"""
        if not self.driver:
            self.setup_driver()
        
        all_movies = []
        
        try:
            # Navigate to the Beer Sheva cinema page
            self.driver.get(self.beer_sheva_url)
            time.sleep(3)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Get movies for each date
            for i in range(days_ahead):
                date = datetime.now() + timedelta(days=i)
                print(f"\n=== Getting movies for {date.strftime('%Y-%m-%d')} ===")
                
                movies_for_date = self._get_movies_for_date(date)
                all_movies.extend(movies_for_date)
            
            # Check for missing movies
            print("\n=== Checking for missing movies ===")
            discovered_movies = {movie['title'] for movie in all_movies}
            missing_movies = self._check_for_missing_movies(discovered_movies, days_ahead)
            all_movies.extend(missing_movies)
            
            # Deduplicate movies
            all_movies = self._deduplicate_movies(all_movies)
            
            # Clean and validate the data for RAG compatibility
            all_movies = self._clean_movie_data(all_movies)
            
            print(f"\nTotal unique movies found: {len(all_movies)}")
            
            return all_movies
            
        except Exception as e:
            print(f"Error getting movies data: {e}")
            return []
    
    def _get_movies_for_date(self, date: datetime) -> List[Dict]:
        """Get movies for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        url = f"{self.beer_sheva_url}#/buy-tickets-by-cinema?in-cinema=1074&at={date_str}&view-mode=list"
        
        print(f"Navigating to: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Select the date if needed
            self._select_date(date_str)
            
            # Wait for content to load
            time.sleep(5)
            
            # Extract movies from the page
            movies = self._extract_movies_from_page_v2(date)
            
            return movies
            
        except Exception as e:
            print(f"Error getting movies for date {date_str}: {e}")
            return []
    
    def _select_date(self, date_str: str):
        """Select the specific date on the page"""
        try:
            # Try to find and click date selector
            date_selectors = [
                f'[data-date="{date_str}"]',
                f'[data-value="{date_str}"]',
                f'button[data-date="{date_str}"]',
                f'a[data-date="{date_str}"]',
                f'[title*="{date_str}"]',
                f'[aria-label*="{date_str}"]'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    date_element.click()
                    print(f"Selected date: {date_str}")
                    time.sleep(2)
                    return
                except TimeoutException:
                    continue
            
            print(f"Could not find date selector for {date_str}, continuing...")
            
        except Exception as e:
            print(f"Error selecting date {date_str}: {e}")
    
    def _extract_movies_from_page_v2(self, date: datetime) -> List[Dict]:
        """Improved movie extraction that focuses on finding all movies"""
        movies = []
        
        # Wait for page to load
        time.sleep(3)
        
        # First, try to find all movie title elements
        print("Looking for movie titles...")
        movie_titles = self._find_all_movie_titles()
        
        if not movie_titles:
            print("No movie titles found, trying alternative approach...")
            # Fallback: try to find any elements with movie-like content
            movie_titles = self._find_movie_like_elements()
        
        print(f"Found {len(movie_titles)} potential movie elements")
        
        # Extract movie data for each title
        for i, title_element in enumerate(movie_titles):
            try:
                print(f"Processing movie {i+1}/{len(movie_titles)}: {title_element.text[:50]}...")
                
                movie_data = self._extract_movie_from_title_element(title_element, date)
                if movie_data:
                    print(f"  ✅ Extracted: {movie_data['title']}")
                    movies.append(movie_data)
                else:
                    print(f"  ❌ Failed to extract movie data")
                    
            except Exception as e:
                print(f"Error processing movie {i+1}: {e}")
                continue
        
        return movies
    
    def _find_movie_like_elements(self) -> List:
        """Fallback method to find elements that might contain movie titles"""
        all_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div, span, p, h1, h2, h3, h4, h5, h6')
        
        movie_like_elements = []
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 2 and len(text) < 100:
                # Check if it looks like a movie title
                if self._is_likely_movie_title(text) and not self._is_navigation_element(text):
                    movie_like_elements.append(element)
        
        return movie_like_elements
    
    def _extract_movie_from_title_element(self, title_element, date: datetime) -> Optional[Dict]:
        """Extract movie data from a title element"""
        try:
            # Get the text content
            title_text = title_element.text.strip()
            
            # Skip if it's not a valid movie title
            if not self._is_likely_movie_title(title_text):
                return None
            
            # Clean the title - remove genre descriptions and extra info
            clean_title = self._clean_movie_title(title_text)
            
            if not clean_title:
                return None
            
            # Find showtimes for this movie
            showtimes = self._find_showtimes_for_movie(title_element)
            
            # Only include if we have valid showtimes
            if not showtimes:
                return None
            
            movie_data = {
                'title': clean_title,
                'date': date.strftime('%Y-%m-%d'),
                'showtimes': showtimes
            }
            
            # Try to extract additional info
            try:
                # Look for genre/duration info in nearby elements
                parent = title_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'movie') or contains(@class, 'qb-movie')]")
                genre_elements = parent.find_elements(By.XPATH, ".//*[contains(text(), 'דקות') or contains(text(), '|')]")
                
                for element in genre_elements:
                    text = element.text.strip()
                    if '|' in text and 'דקות' in text:
                        movie_data['genre_info'] = text
                        break
                        
            except Exception:
                pass  # Genre info is optional
            
            return movie_data
            
        except Exception as e:
            print(f"  ❌ Failed to extract movie data: {e}")
            return None
    
    def _clean_movie_title(self, title_text: str) -> str:
        """Clean movie title by removing genre descriptions and extra info"""
        # Remove common genre patterns
        genre_patterns = [
            r'\s*\|\s*\d+\s*דקות.*$',  # "| 120 דקות"
            r'\s*,\s*[^,]*\s*\|\s*\d+\s*דקות.*$',  # "דרמה, פעולה | 120 דקות"
            r'\s*\([^)]*\)\s*$',  # "(כתוביות עברית)"
            r'\s*·\s*[^·]*$',  # "· כתוביות עברית"
            r'\s*-\s*[^-]*$',  # "- כתוביות עברית"
        ]
        
        clean_title = title_text
        for pattern in genre_patterns:
            clean_title = re.sub(pattern, '', clean_title)
        
        # Remove hall types and formats from title
        hall_patterns = [
            r'\s*(2D|3D|4DX|IMAX|VIP|SCREENX)\s*$',
            r'^\s*(2D|3D|4DX|IMAX|VIP|SCREENX)\s*',
            r'\s*hall_\d+\s*$',
            r'^\s*hall_\d+\s*'
        ]
        
        for pattern in hall_patterns:
            clean_title = re.sub(pattern, '', clean_title)
        
        # Clean up extra whitespace
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        
        # Skip if title is too short after cleaning
        if len(clean_title) < 2:
            return ""
        
        # Skip if it's just a hall type or format
        if re.match(r'^(2D|3D|4DX|IMAX|VIP|SCREENX|hall_\d+)$', clean_title):
            return ""
        
        return clean_title
    
    def _find_showtimes_for_movie(self, title_element) -> Dict[str, List[str]]:
        """Find showtimes associated with a specific movie, grouped by hall/type"""
        try:
            # Find the movie container
            movie_container = title_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'qb-movie')]")
            # Find all time buttons within this movie container
            time_buttons = movie_container.find_elements(By.CSS_SELECTOR, 'a.btn.btn-primary.btn-lg')
            showtimes_by_hall = {}
            for btn in time_buttons:
                time_text = btn.text.strip()
                if not self._is_valid_time(time_text):
                    continue
                # Find hall/type from nearby elements
                hall_type = '2D'  # Default
                try:
                    # Look for hall/type in the same row or above
                    parent_row = btn.find_element(By.XPATH, './ancestor::div[contains(@class, "type-row")]')
                    hall_spans = parent_row.find_elements(By.CSS_SELECTOR, '.qb-screening-attributes span')
                    for span in hall_spans:
                        hall_candidate = span.text.strip().upper()
                        if hall_candidate in ['2D', '3D', '4DX', 'IMAX', 'VIP', 'SCREENX']:
                            hall_type = hall_candidate
                            break
                except Exception:
                    pass
                if hall_type not in showtimes_by_hall:
                    showtimes_by_hall[hall_type] = []
                if time_text not in showtimes_by_hall[hall_type]:
                    showtimes_by_hall[hall_type].append(time_text)
            # Sort times within each hall
            for hall in showtimes_by_hall:
                showtimes_by_hall[hall].sort()
            return showtimes_by_hall
        except Exception as e:
            print(f"Error finding showtimes for movie (by hall): {e}")
            return {}
    
    def _check_for_missing_movies(self, discovered_movies: set, days_ahead: int) -> List[Dict]:
        """Check for specific movies that might not appear on main pages"""
        missing_movies = []
        start_date = datetime.now()
        
        # List of movies that we know exist but might not appear on main pages
        known_missing_movies = [
            {
                'title': '28 שנים אחרי',
                'url': 'https://www.planetcinema.co.il/films/28-years-later/7045s2r',
                'movie_id': '7045s2r'
            },
            {
                'title': 'הדרקון הראשון שלי',
                'url': 'https://www.planetcinema.co.il/films/how-to-train-your-dragon/6959s2r',
                'movie_id': '6959s2r'
            }
        ]
        
        # Only check movies that weren't discovered on main pages
        for movie_info in known_missing_movies:
            if movie_info['title'] not in discovered_movies:
                print(f"Checking missing movie: {movie_info['title']}")
                
                for day in range(days_ahead):
                    current_date = start_date + timedelta(days=day)
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    try:
                        movie_data = self._get_movie_data_for_date(movie_info, date_str)
                        if movie_data:
                            missing_movies.append(movie_data)
                            print(f"  ✅ Found {len(movie_data['showtimes'])} showtimes for {date_str}")
                        else:
                            print(f"  ❌ No showtimes for {date_str}")
                            
                    except Exception as e:
                        print(f"  Error checking {movie_info['title']} for {date_str}: {e}")
                        continue
            else:
                print(f"Skipping {movie_info['title']} - already found on main pages")
        
        return missing_movies
    
    def _get_movie_data_for_date(self, movie_info: Dict, date_str: str) -> Optional[Dict]:
        """Get movie data for a specific date"""
        if not movie_info.get('url'):
            return None
        
        try:
            # Construct URL for this specific movie and date
            if movie_info.get('movie_id'):
                url = f"{movie_info['url']}#/buy-tickets-by-film?in-cinema=1074&at={date_str}&for-movie={movie_info['movie_id']}&view-mode=list"
            else:
                url = f"{movie_info['url']}#/buy-tickets-by-film?in-cinema=1074&at={date_str}&view-mode=list"
            
            self.driver.get(url)
            time.sleep(3)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Check if there are showtimes for this movie on this date
            showtimes = self._find_showtimes_for_specific_movie()
            
            if showtimes:
                return {
                    'title': movie_info['title'],
                    'date': date_str,
                    'showtimes': showtimes,
                    'cinema': 'Planet Cinema Beer Sheva',
                    'source': 'specific_page'
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting movie data for {movie_info['title']} on {date_str}: {e}")
            return None
    
    def _find_showtimes_for_specific_movie(self) -> List[str]:
        """Find showtimes for a specific movie page"""
        showtimes = []
        
        try:
            # Look for showtime buttons on the specific movie page
            time_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn.btn-primary.btn-lg')
            
            for button in time_buttons:
                time_text = button.text.strip()
                if self._is_valid_time(time_text):
                    showtimes.append(time_text)
            
            # Also try alternative selectors
            if not showtimes:
                alternative_selectors = [
                    '.showtime-button',
                    '.time-slot',
                    '.booking-time',
                    'button[data-time]',
                    'a[data-time]'
                ]
                
                for selector in alternative_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            time_text = element.text.strip()
                            if self._is_valid_time(time_text):
                                showtimes.append(time_text)
                    except:
                        continue
            
        except Exception as e:
            print(f"Error finding showtimes for specific movie: {e}")
        
        return showtimes
    
    def _find_all_movie_titles(self) -> List:
        """Find all movie title elements on the page using qb-movie containers only"""
        title_elements = []
        try:
            # Find all movie containers
            movie_containers = self.driver.find_elements(By.CSS_SELECTOR, '.qb-movie')
            for container in movie_containers:
                # Find the title element inside the container
                try:
                    title_elem = container.find_element(By.CSS_SELECTOR, '.qb-movie-name')
                    title_elements.append(title_elem)
                except Exception:
                    continue
        except Exception as e:
            print(f"Error finding movie containers: {e}")
        return title_elements
    
    def _is_valid_time(self, time_text: str) -> bool:
        """Check if a string represents a valid time"""
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
        """Check if a title is a navigation element"""
        navigation_keywords = [
            'החוויות', 'מבצעים', 'הטבות', 'לקוחות', 'עסקיים', 'ילדים',
            'מזנון', 'קולנוע', 'IMAX', '4DX', 'VIP', 'STUDENT',
            'כנסים', 'אירועים', 'יום הולדת', 'הקרנת חצות',
            'BLOG', 'עקבו', 'דברו', 'קישורים', 'מידע', 'להורדת',
            'אנדרואיד', 'iOS', 'פייסבוק', 'אינסטגרם', 'טיקטוק',
            'צרו קשר', 'שירות לקוחות', 'פרסום', 'פורום פילם',
            'תנאים', 'הגבלות', 'אודות', 'פלאנט', 'מדיניות',
            'פרטיות', 'עוגיות', 'שאלות', 'תשובות', 'נגישות',
            'ניהול', 'הזמנה', 'דרושים', 'כל הזכויות', 'שמורות',
            'העמוד נטען', 'סגור', 'N/A', 'שתפו', 'התחברו',
            'הירשמו', 'התחבר', 'פייסבוק', 'טוויטר', 'מייל',
            'מתחבר', 'המתינו', 'מעבדת', 'בקשתכם'
        ]
        
        title_lower = title.lower()
        for keyword in navigation_keywords:
            if keyword.lower() in title_lower:
                return True
        
        return False
    
    def _is_likely_movie_title(self, title: str) -> bool:
        """Check if a string is likely to be a movie title"""
        if not title or len(title) < 2:
            return False
        
        # Skip if it's too short or too long
        if len(title) < 3 or len(title) > 100:
            return False
        
        # Skip navigation elements
        if self._is_navigation_element(title):
            return False
        
        # Skip language/format indicators
        language_indicators = [
            'עברית', 'אנגלית', 'צרפתית', 'קוריאנית', 'יפנית', 'סינית',
            'כתוביות', 'מדובב', 'דיבוב', 'תרגום',
            '·', '(', ')', '[', ']'
        ]
        
        for indicator in language_indicators:
            if indicator in title:
                return False
        
        # Skip if it's just a language code
        if title.strip() in ['עברית', 'אנגלית', 'צרפתית', 'קוריאנית']:
            return False
        
        # Skip if it contains only special characters
        if re.match(r'^[^\w\sא-ת]+$', title):
            return False
        
        # Skip navigation and UI elements
        navigation_ui = [
            'בחרו סרט', 'הזמינו כרטיסים', 'מכירה מוקדמת', 'בחר סרט',
            'בחרו סרט', 'הזמן כרטיסים', 'מכירה', 'מוקדמת',
            'hall_1', 'hall_2', 'hall_3', 'hall_4',
            '2D', '3D', '4DX', 'IMAX', 'VIP', 'SCREENX',
            'כרטיסים', 'הזמנה', 'מכירה', 'מוקדמת'
        ]
        
        title_lower = title.lower()
        for nav in navigation_ui:
            if nav.lower() in title_lower:
                return False
        
        # Skip if it's just a hall type or format
        if re.match(r'^(2D|3D|4DX|IMAX|VIP|SCREENX|hall_\d+)$', title.strip()):
            return False
        
        # Allow movie titles starting with numbers
        if title[0].isdigit():
            return True
        
        # Known movies that should be included
        known_movies = [
            '28 שנים אחרי',
            'הדרקון הראשון שלי',
            'עולם היורה',
            'להציל את דינו',
            'כלה על ההדק',
            'אליאו'
        ]
        
        for movie in known_movies:
            if movie in title:
                return True
        
        # Check if it looks like a movie title (has Hebrew characters, reasonable length)
        hebrew_chars = sum(1 for c in title if '\u0590' <= c <= '\u05FF')
        if hebrew_chars > 0 and len(title) >= 3:
            return True
        
        return False
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if it appears"""
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
        """Remove duplicate movies based on title and date, merging showtimes dicts by hall/type"""
        seen = set()
        unique_movies = []
        
        for movie in movies:
            key = (movie['title'], movie['date'])
            
            if key not in seen:
                seen.add(key)
                unique_movies.append(movie)
            else:
                # Merge showtimes dicts by hall/type
                existing_movie = next(m for m in unique_movies if (m['title'], m['date']) == key)
                
                # Ensure both movies have dict showtimes
                existing_showtimes = existing_movie.get('showtimes', {})
                new_showtimes = movie.get('showtimes', {})
                
                # Convert lists to dicts if needed
                if isinstance(existing_showtimes, list):
                    existing_showtimes = {'2D': existing_showtimes}
                if isinstance(new_showtimes, list):
                    new_showtimes = {'2D': new_showtimes}
                
                # Merge showtimes
                for hall, times in new_showtimes.items():
                    if isinstance(times, list):
                        if hall in existing_showtimes:
                            # Merge and deduplicate times
                            merged = set(existing_showtimes[hall]) | set(times)
                            existing_showtimes[hall] = sorted(list(merged))
                        else:
                            existing_showtimes[hall] = sorted(list(set(times)))
                
                existing_movie['showtimes'] = existing_showtimes
        
        return unique_movies
    
    def save_to_json(self, movies: List[Dict], filename: str = None):
        """Save scraped data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"planet_cinema_movies_v2_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(movies)} movies to {filename}")
    
    def print_summary(self, movies: List[Dict]):
        """Print a summary of scraped data"""
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
    
    def _clean_movie_data(self, movies: List[Dict]) -> List[Dict]:
        """Clean and validate movie data for RAG compatibility"""
        cleaned_movies = []
        
        for movie in movies:
            # Skip movies with invalid titles
            if not movie.get('title') or len(movie['title']) < 2:
                continue
            
            # Skip movies with empty showtimes
            if not movie.get('showtimes'):
                continue
            
            # Handle different showtimes formats
            cleaned_showtimes = {}
            showtimes = movie['showtimes']
            
            # If showtimes is a list, convert to dict with default hall
            if isinstance(showtimes, list):
                valid_times = [time for time in showtimes if self._is_valid_time(time)]
                if valid_times:
                    cleaned_showtimes['2D'] = valid_times
            # If showtimes is a dict, clean each hall
            elif isinstance(showtimes, dict):
                for hall, times in showtimes.items():
                    if times and len(times) > 0:
                        # Filter out invalid times
                        valid_times = [time for time in times if self._is_valid_time(time)]
                        if valid_times:
                            cleaned_showtimes[hall] = valid_times
            else:
                # Skip if showtimes is neither list nor dict
                continue
            
            # Skip if no valid showtimes remain
            if not cleaned_showtimes:
                continue
            
            # Create cleaned movie data
            cleaned_movie = {
                'title': movie['title'],
                'date': movie['date'],
                'showtimes': cleaned_showtimes,
                'cinema': 'Planet Cinema Beer Sheva',
                'source_url': self.beer_sheva_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Add optional fields if they exist
            if 'genre_info' in movie:
                cleaned_movie['genre_info'] = movie['genre_info']
            
            cleaned_movies.append(cleaned_movie)
        
        return cleaned_movies

# Test the scraper
if __name__ == "__main__":
    scraper = PlanetCinemaScraperV2(headless=False)  # Set to False to see the browser
    
    try:
        print("Starting Planet Cinema Beer Sheva scraper (V2)...")
        movies = scraper.get_movies_data(days_ahead=3)
        
        scraper.print_summary(movies)
        scraper.save_to_json(movies)
        
    finally:
        scraper.close_driver() 