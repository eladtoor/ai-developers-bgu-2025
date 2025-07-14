import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
import json
from datetime import datetime
import time

load_dotenv()

class MovieRAGSystem:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_db = None
        self.movies_data = []
        
    def fetch_imdb_data(self, movie_title):
        """Fetch movie data from IMDB API (using OMDB API as alternative)"""
        try:
            # Using OMDB API (free alternative to IMDB API)
            omdb_api_key = os.getenv("OMDB_API_KEY")  # You'll need to get this
            url = f"http://www.omdbapi.com/?t={movie_title}&apikey={omdb_api_key}"
            response = requests.get(url)
            data = response.json()
            
            if data.get("Response") == "True":
                return {
                    "title": data.get("Title"),
                    "year": data.get("Year"),
                    "rating": data.get("imdbRating"),
                    "genre": data.get("Genre"),
                    "plot": data.get("Plot"),
                    "director": data.get("Director"),
                    "actors": data.get("Actors"),
                    "runtime": data.get("Runtime"),
                    "metascore": data.get("Metascore")
                }
        except Exception as e:
            print(f"Error fetching IMDB data for {movie_title}: {e}")
        return None
    
    def scrape_cinema_websites(self):
        """Scrape movie data from local cinemas"""
        # This is a placeholder - you'll need to implement actual scraping
        # Using Selenium or BeautifulSoup for dynamic content
        
        # Example structure for scraped data
        scraped_movies = [
            {
                "title": "Movie Title",
                "cinema": "Yes Planet",
                "showtimes": ["19:00", "21:30"],
                "date": "2024-01-15"
            }
        ]
        
        return scraped_movies
    
    def create_movie_documents(self, movies_data):
        """Convert movie data to LangChain documents for vectorization"""
        documents = []
        
        for movie in movies_data:
            # Create rich text representation
            movie_text = f"""
            Title: {movie.get('title', 'Unknown')}
            Year: {movie.get('year', 'Unknown')}
            Genre: {movie.get('genre', 'Unknown')}
            Rating: {movie.get('rating', 'Unknown')}
            Director: {movie.get('director', 'Unknown')}
            Actors: {movie.get('actors', 'Unknown')}
            Plot: {movie.get('plot', 'No description available')}
            Runtime: {movie.get('runtime', 'Unknown')}
            Metascore: {movie.get('metascore', 'Unknown')}
            Cinema: {movie.get('cinema', 'Unknown')}
            Showtimes: {', '.join(movie.get('showtimes', []))}
            """
            
            # Create metadata
            metadata = {
                "title": movie.get('title', ''),
                "genre": movie.get('genre', ''),
                "rating": movie.get('rating', ''),
                "year": movie.get('year', ''),
                "cinema": movie.get('cinema', ''),
                "source": "movie_database"
            }
            
            documents.append(Document(page_content=movie_text, metadata=metadata))
        
        return documents
    
    def build_vector_database(self, documents):
        """Create and populate vector database"""
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector database
        self.vector_db = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory="./movie_vector_db"
        )
        
        print(f"Vector database created with {len(split_docs)} chunks")
    
    def query_movies(self, question):
        """Query the movie database using RAG"""
        if not self.vector_db:
            return "Vector database not initialized. Please build it first."
        
        # Create RAG chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a movie expert assistant. Answer questions about movies showing in Beer Sheva cinemas.
            Use the provided context to give accurate, helpful answers. If you don't have enough information, say so.
            Always mention the cinema name and showtimes when relevant."""),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])
        
        # Create the RAG chain
        rag_chain = prompt | self.llm | StrOutputParser()
        
        # Retrieve relevant documents
        relevant_docs = self.vector_db.similarity_search(question, k=5)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Generate response
        response = rag_chain.invoke({"context": context, "question": question})
        return response
    
    def get_highest_rated_by_genre(self, genre):
        """Get the highest rated movie in a specific genre"""
        if not self.vector_db:
            return "Vector database not initialized."
        
        # Query for movies in the specified genre
        query = f"movies in {genre} genre with ratings"
        relevant_docs = self.vector_db.similarity_search(query, k=10)
        
        # Extract and sort by rating
        movies_with_ratings = []
        for doc in relevant_docs:
            metadata = doc.metadata
            if metadata.get('genre', '').lower().find(genre.lower()) != -1:
                try:
                    rating = float(metadata.get('rating', '0'))
                    movies_with_ratings.append({
                        'title': metadata.get('title'),
                        'rating': rating,
                        'cinema': metadata.get('cinema'),
                        'year': metadata.get('year')
                    })
                except ValueError:
                    continue
        
        if movies_with_ratings:
            # Sort by rating (highest first)
            movies_with_ratings.sort(key=lambda x: x['rating'], reverse=True)
            highest_rated = movies_with_ratings[0]
            
            return f"The highest rated {genre} movie is '{highest_rated['title']}' ({highest_rated['year']}) with a rating of {highest_rated['rating']}/10, showing at {highest_rated['cinema']}."
        else:
            return f"No {genre} movies found in the database."

# Example usage
if __name__ == "__main__":
    rag_system = MovieRAGSystem()
    
    # Example: Get highest rated comedy
    result = rag_system.get_highest_rated_by_genre("comedy")
    print(result) 