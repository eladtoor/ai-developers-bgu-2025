#!/usr/bin/env python3
"""
Test script for Yes Planet Beer Sheva scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.yes_planet_scraper import YesPlanetScraper
import json

def test_scraper():
    """Test the Yes Planet scraper"""
    print("🚀 Testing Yes Planet Beer Sheva Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = YesPlanetScraper()
    
    try:
        # Test scraping for next 3 days
        print("📅 Scraping movies for the next 3 days...")
        movies = scraper.get_movies_data(days_ahead=3)
        
        if movies:
            print(f"✅ Successfully scraped {len(movies)} movies!")
            scraper.print_summary(movies)
            
            # Save to file
            scraper.save_to_json(movies, "test_yes_planet_movies.json")
            
            # Show detailed data for first movie
            if movies:
                print("\n📋 Sample movie data:")
                print(json.dumps(movies[0], indent=2, ensure_ascii=False))
                
        else:
            print("❌ No movies found. This might indicate:")
            print("   - Website structure has changed")
            print("   - No movies currently showing")
            print("   - Network/access issues")
            print("   - Need to adjust selectors")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

def inspect_website_structure():
    """Inspect the website structure to understand the HTML"""
    print("\n🔍 Inspecting Yes Planet website structure...")
    
    scraper = YesPlanetScraper()
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Get the main page
        response = requests.get(scraper.beer_sheva_url, headers=scraper.session.headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title found'}")
        
        # Look for common movie-related elements
        print("\n🔍 Searching for movie-related elements...")
        
        # Check for common selectors
        selectors_to_check = [
            '.movie', '.film', '.showtime', '.time', '.title',
            '[data-movie]', '[data-film]', '.movie-item', '.film-item'
        ]
        
        for selector in selectors_to_check:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector '{selector}'")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text = elem.get_text(strip=True)[:100]
                    print(f"   {i+1}. {text}...")
            else:
                print(f"❌ No elements found with selector '{selector}'")
        
        # Look for any text that might be movie titles
        print("\n🔍 Looking for potential movie titles...")
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # Look for lines that might be movie titles (capitalized, reasonable length)
        potential_titles = []
        for line in lines:
            if (len(line) > 3 and len(line) < 100 and 
                line[0].isupper() and 
                not line.startswith('http') and
                not line.isdigit()):
                potential_titles.append(line)
        
        print(f"Found {len(potential_titles)} potential title candidates:")
        for title in potential_titles[:10]:  # Show first 10
            print(f"   - {title}")
        
        # Save the HTML for manual inspection
        with open("yes_planet_page.html", "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        print(f"\n💾 Saved HTML to 'yes_planet_page.html' for manual inspection")
        
    except Exception as e:
        print(f"❌ Error inspecting website: {e}")

if __name__ == "__main__":
    print("🎬 Yes Planet Beer Sheva Scraper Test")
    print("=" * 50)
    
    # First, inspect the website structure
    inspect_website_structure()
    
    print("\n" + "=" * 50)
    
    # Then test the scraper
    test_scraper()
    
    print("\n🏁 Test completed!")
    print("\nNext steps:")
    print("1. Check the generated JSON file")
    print("2. Inspect the HTML file to understand the structure")
    print("3. Adjust selectors in the scraper if needed")
    print("4. Run the scraper again to verify improvements") 