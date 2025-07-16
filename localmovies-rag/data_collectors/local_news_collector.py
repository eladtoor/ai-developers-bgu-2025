import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from datetime import datetime
import time
from config import settings

class LocalNewsCollector:
    def __init__(self):
        self.city_name = settings.city_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_local_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for local news articles about movies filmed in Beer Sheva"""
        # This is a simplified implementation
        # In a real scenario, you'd use news APIs or web scraping
        
        # Example news sources for Beer Sheva
        news_sources = [
            "https://www.ynet.co.il",
            "https://www.maariv.co.il",
            "https://www.israelhayom.co.il",
            "https://www.ynet.co.il/local/beer-sheva"
        ]
        
        articles = []
        
        for source in news_sources:
            try:
                articles.extend(self._scrape_news_source(source, query, max_results // len(news_sources)))
            except Exception as e:
                print(f"Error scraping {source}: {e}")
                continue
        
        return articles
    
    def _scrape_news_source(self, url: str, query: str, max_results: int) -> List[Dict]:
        """Scrape a specific news source for articles"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # This is a generic approach - you'd need to customize for each site
            article_links = soup.find_all('a', href=True)
            
            for link in article_links[:max_results]:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if self._is_relevant_article(title, query):
                    article_data = {
                        'title': title,
                        'url': href if href.startswith('http') else f"{url.rstrip('/')}/{href.lstrip('/')}",
                        'source': url,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'content': self._extract_article_content(href)
                    }
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def _is_relevant_article(self, title: str, query: str) -> bool:
        """Check if an article is relevant to the search query"""
        keywords = query.lower().split()
        title_lower = title.lower()
        
        # Check for movie-related keywords
        movie_keywords = ['film', 'movie', 'cinema', 'actor', 'actress', 'director', 'filming', 'shot']
        location_keywords = [self.city_name.lower(), 'beer sheva', 'באר שבע']
        
        has_movie_keyword = any(keyword in title_lower for keyword in movie_keywords)
        has_location_keyword = any(keyword in title_lower for keyword in location_keywords)
        
        return has_movie_keyword and has_location_keyword
    
    def _extract_article_content(self, url: str) -> str:
        """Extract the main content from an article URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find the main article content
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                'main',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text(strip=True)
            
            return content[:2000]  # Limit content length
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return ""
    
    def search_movie_filming_news(self, movie_title: str) -> List[Dict]:
        """Search for news about a specific movie being filmed in Beer Sheva"""
        query = f"{movie_title} {self.city_name} filming"
        return self.search_local_news(query)
    
    def get_recent_filming_news(self, days_back: int = 30) -> List[Dict]:
        """Get recent news about movies filmed in Beer Sheva"""
        query = f"filming {self.city_name} movie film"
        return self.search_local_news(query)
    
    def format_news_data(self, article_data: Dict) -> Dict:
        """Format news data for the RAG system"""
        return {
            'title': article_data.get('title', ''),
            'url': article_data.get('url', ''),
            'source': article_data.get('source', ''),
            'date': article_data.get('date', ''),
            'content': article_data.get('content', ''),
            'type': 'local_news',
            'location': self.city_name
        }

class MockLocalNewsCollector(LocalNewsCollector):
    """Mock collector for testing when web scraping is not available"""
    
    def search_local_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Mock local news search"""
        return [
            {
                'title': f'New Movie Filmed in {self.city_name} - "The Desert Chronicles"',
                'url': f'https://example.com/news/movie-filmed-{self.city_name.lower().replace(" ", "-")}',
                'source': 'Local News',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'content': f'A new Hollywood production has chosen {self.city_name} as its filming location. The movie, titled "The Desert Chronicles", will feature several scenes shot in the city\'s historic Old City and the Ben-Gurion University campus. Local residents are excited about the economic benefits this will bring to the city.',
                'type': 'local_news',
                'location': self.city_name
            },
            {
                'title': f'{self.city_name} Becomes Popular Filming Destination',
                'url': f'https://example.com/news/{self.city_name.lower().replace(" ", "-")}-filming-destination',
                'source': 'Local News',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'content': f'{self.city_name} has seen a surge in film productions over the past year. The city\'s unique desert landscape and modern infrastructure make it an attractive location for both local and international filmmakers. The municipality has established a film office to support these productions.',
                'type': 'local_news',
                'location': self.city_name
            }
        ] 