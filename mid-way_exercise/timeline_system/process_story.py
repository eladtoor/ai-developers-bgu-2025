from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from timeline_map_reduce import map_reduce_timeline_function
from timeline_refine import refine_timeline_function

def process_new_story():
    """Process the new story using timeline tools directly"""
    
    print("Processing 'The Day Everything Slowed Down'...")
    print("="*60)
    
    # Create Map-Reduce timeline
    print("Creating Map-Reduce timeline...")
    map_reduce_timeline = map_reduce_timeline_function("The Day Everything Slowed Down")
    
    # Save Map-Reduce timeline
    with open("map_reduce_timeline_the_day_everything_slowed_down.txt", "w", encoding="utf-8") as f:
        f.write(map_reduce_timeline)
    print("✅ Map-Reduce timeline saved!")
    
    # Create Refine timeline
    print("\nCreating Refine timeline...")
    refine_timeline = refine_timeline_function("The Day Everything Slowed Down")
    
    # Save Refine timeline
    with open("refine_timeline_the_day_everything_slowed_down.txt", "w", encoding="utf-8") as f:
        f.write(refine_timeline)
    print("✅ Refine timeline saved!")
    
    print("\n🎉 Both timelines created successfully!")
    print("Files created:")
    print("- map_reduce_timeline_the_day_everything_slowed_down.txt")
    print("- refine_timeline_the_day_everything_slowed_down.txt")

if __name__ == "__main__":
    process_new_story() 