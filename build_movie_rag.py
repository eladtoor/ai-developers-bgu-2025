import os
import json
from datetime import datetime
from movie_rag_system import MovieRAGSystem
from cinema_scraper import CinemaScraper

def build_complete_movie_rag():
    """Build the complete movie RAG system"""
    print("🎬 Building Movie RAG System for Beer Sheva")
    print("=" * 50)
    
    # Initialize components
    rag_system = MovieRAGSystem()
    scraper = CinemaScraper()
    
    # Step 1: Scrape current movies from cinemas
    print("\n📽️ Step 1: Scraping current movies from cinemas...")
    scraped_movies = scraper.scrape_all_cinemas()
    
    if not scraped_movies:
        print("❌ No movies found. Using sample data for demonstration...")
        scraped_movies = [
            {
                "title": "The Super Mario Bros. Movie",
                "clean_title": "The Super Mario Bros. Movie",
                "cinema": "Yes Planet",
                "showtimes": ["19:00", "21:30"],
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Guardians of the Galaxy Vol. 3",
                "clean_title": "Guardians of the Galaxy Vol. 3",
                "cinema": "Cinema City",
                "showtimes": ["18:30", "21:00"],
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    # Step 2: Enrich with IMDB data
    print(f"\n🎯 Step 2: Enriching {len(scraped_movies)} movies with IMDB data...")
    enriched_movies = []
    
    for movie in scraped_movies:
        print(f"  Fetching data for: {movie['clean_title']}")
        
        # Get IMDB data
        imdb_data = rag_system.fetch_imdb_data(movie['clean_title'])
        
        if imdb_data:
            # Merge scraped data with IMDB data
            enriched_movie = {**movie, **imdb_data}
            enriched_movies.append(enriched_movie)
            print(f"    ✅ Found: {imdb_data.get('title')} ({imdb_data.get('year')}) - Rating: {imdb_data.get('rating')}")
        else:
            # Keep movie even without IMDB data
            enriched_movies.append(movie)
            print(f"    ⚠️  No IMDB data found for: {movie['clean_title']}")
        
        # Be respectful to APIs - add delay
        import time
        time.sleep(1)
    
    # Step 3: Create documents for vectorization
    print(f"\n📄 Step 3: Creating documents for {len(enriched_movies)} movies...")
    documents = rag_system.create_movie_documents(enriched_movies)
    
    # Step 4: Build vector database
    print(f"\n🗄️ Step 4: Building vector database...")
    rag_system.build_vector_database(documents)
    
    # Step 5: Save enriched data for future use
    print(f"\n💾 Step 5: Saving enriched data...")
    with open('enriched_movies.json', 'w', encoding='utf-8') as f:
        json.dump(enriched_movies, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Movie RAG System built successfully!")
    print(f"   - Movies processed: {len(enriched_movies)}")
    print(f"   - Vector database: ./movie_vector_db/")
    print(f"   - Enriched data: enriched_movies.json")
    
    return rag_system

def test_movie_queries(rag_system):
    """Test various movie queries"""
    print("\n🧪 Testing Movie Queries")
    print("=" * 30)
    
    test_questions = [
        "What is the highest rated comedy movie?",
        "What movies are showing at Yes Planet?",
        "What are the showtimes for action movies?",
        "Which cinema has the best rated movies?",
        "What movies are showing today?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print(f"🤖 Answer: {rag_system.query_movies(question)}")
        print("-" * 50)

def main():
    """Main function to build and test the RAG system"""
    try:
        # Build the RAG system
        rag_system = build_complete_movie_rag()
        
        # Test queries
        test_movie_queries(rag_system)
        
        # Interactive mode
        print("\n🎮 Interactive Mode - Ask questions about movies!")
        print("Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            question = input("\n❓ Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if question:
                answer = rag_system.query_movies(question)
                print(f"🤖 {answer}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 