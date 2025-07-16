#!/usr/bin/env python3
"""
Setup and test script for the Yes Planet scraper
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def run_test():
    """Run the scraper test"""
    print("\n🧪 Running Planet Cinema scraper test...")
    
    try:
        subprocess.check_call([sys.executable, "test_planet_scraper.py"])
        print("✅ Test completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running test: {e}")
        return False
    
    return True

def main():
    """Main setup and test function"""
    print("🎬 Yes Planet Beer Sheva Scraper - Setup & Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Please run this script from the localmovies-rag directory.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Exiting.")
        return
    
    # Run test
    if not run_test():
        print("❌ Test failed. Check the output above for errors.")
        return
    
    print("\n🎉 Setup and test completed successfully!")
    print("\n📁 Generated files:")
    print("   - test_planet_cinema_movies.json (scraped movie data)")
    
    print("\n🔧 Next steps:")
    print("1. Check the JSON file to see what data was scraped")
    print("2. If no movies found, try running with headless=False to see the browser")
    print("3. Adjust selectors in planet_cinema_scraper.py if needed")
    print("4. Run test_planet_scraper.py again to verify improvements")
    print("5. Make sure Chrome/ChromeDriver is properly installed")

if __name__ == "__main__":
    main() 