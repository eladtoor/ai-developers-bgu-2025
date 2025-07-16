#!/usr/bin/env python3
"""
Test script to open Planet Cinema in visible browser for inspection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.planet_cinema_scraper import PlanetCinemaScraper
import time

def test_visible_browser():
    """Open the website in visible browser for manual inspection"""
    print("🔍 Opening Planet Cinema in visible browser...")
    
    try:
        # Initialize scraper with visible browser
        scraper = PlanetCinemaScraper(headless=False)
        scraper.setup_driver()
        
        # Navigate to the page
        url = "https://www.planetcinema.co.il/cinemas/beersheva/1074#/buy-tickets-by-cinema?in-cinema=1074&at=2025-07-03&view-mode=list"
        print(f"Navigating to: {url}")
        scraper.driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(15)
        
        # Handle cookie consent
        scraper._handle_cookie_consent()
        
        # Wait more for content to load
        time.sleep(10)
        
        print("\n=== Manual Inspection ===")
        print("Please manually inspect the page to see:")
        print("1. If the page loads correctly")
        print("2. If there are any popups or overlays")
        print("3. If the movie content is visible")
        print("4. What the actual HTML structure looks like")
        print("5. If you can see the movies 'הדרקון הראשון שלי' and '28 שנים אחרי'")
        
        # Keep browser open for manual inspection
        input("\nPress Enter when you're done inspecting...")
        
        # Try to get page source and save it
        print("Saving page source...")
        page_source = scraper.driver.page_source
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("Page source saved to debug_page_source.html")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'scraper' in locals():
            scraper.close_driver()

if __name__ == "__main__":
    test_visible_browser() 