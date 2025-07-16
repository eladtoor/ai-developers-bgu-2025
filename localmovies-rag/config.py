import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # IMDB/OMDB API
    omdb_api_key: str = os.getenv("OMDB_API_KEY", "")
    
    # Vector Database
    chroma_persist_directory: str = "./chroma_db"
    
    # Cinema APIs (you'll need to get these)
    yes_planet_api_key: str = os.getenv("YES_PLANET_API_KEY", "")
    cinema_city_api_key: str = os.getenv("CINEMA_CITY_API_KEY", "")
    
    # Local settings
    city_name: str = "Beer Sheva"
    cinemas: list = ["Yes Planet", "Cinema City"]
    
    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

settings = Settings() 