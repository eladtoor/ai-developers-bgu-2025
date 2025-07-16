#!/usr/bin/env python3
"""
Test script for Planet Cinema Beer Sheva scraper using Selenium
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.planet_cinema_scraper import PlanetCinemaScraper
import json

def test_planet_scraper():
    """Test the Planet Cinema scraper"""
    print("🚀 Testing Planet Cinema Beer Sheva Scraper")
    print("=" * 60)
    
    try:
        # Initialize scraper with headless=True to avoid popup issues
        print("🔧 Initializing scraper...")
        scraper = PlanetCinemaScraper(headless=True)  # Set to False to see the browser
        
        # Test scraping for next 3 days
        print("📅 Scraping movies for the next 3 days...")
        movies = scraper.get_movies_data(days_ahead=3)
        
        if movies:
            print(f"✅ Successfully scraped {len(movies)} movies!")
            scraper.print_summary(movies)
            
            # Save to file
            scraper.save_to_json(movies, "test_planet_cinema_movies.json")
            
            # Show detailed data for first movie
            if movies:
                print("\n📋 Sample movie data:")
                print(json.dumps(movies[0], indent=2, ensure_ascii=False))
                
        else:
            print("❌ No movies found. This might indicate:")
            print("   - Website structure has changed")
            print("   - No movies currently showing")
            print("   - JavaScript content not loading properly")
            print("   - Need to adjust selectors")
            print("   - Need to wait longer for content to load")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

def test_with_different_settings():
    """Test with different scraper settings"""
    print("\n🧪 Testing with different settings...")
    
    try:
        # Test with headless mode
        print("Testing headless mode...")
        scraper = PlanetCinemaScraper(headless=True)
        movies = scraper.get_movies_data(days_ahead=1)
        
        if movies:
            print(f"✅ Headless mode found {len(movies)} movies")
        else:
            print("❌ Headless mode found no movies")
            
    except Exception as e:
        print(f"❌ Error in headless mode: {e}")

def main():
    """Main test function"""
    print("🎬 Planet Cinema Beer Sheva Scraper Test")
    print("=" * 60)
    
    # Test the main scraper
    test_planet_scraper()
    
    # Test with different settings
    test_with_different_settings()
    
    print("\n🏁 Test completed!")
    print("\nNext steps:")
    print("1. Check the generated JSON file")
    print("2. If no movies found, try running with headless=False to see the browser")
    print("3. Adjust selectors in planet_cinema_scraper.py if needed")
    print("4. Check if the website requires additional waiting time")
    print("5. Verify that Chrome/ChromeDriver is properly installed")

if __name__ == "__main__":
    main() 