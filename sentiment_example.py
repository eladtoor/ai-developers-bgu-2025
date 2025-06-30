from transformers import pipeline

# Create a sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Test some different texts
texts = [
    "It's complicated.",
    "Maybe.",
    "I don't know.",
    "The sky is blue.",
    "Water is wet.",
    "The time is 3 PM.",
    "This is a sentence.",
    "The number is 42."
]

print("=== Sentiment Analysis Examples ===\n")

for text in texts:
    # Get the sentiment
    result = sentiment_analyzer(text)
    
    # Print the result
    print(f"Text: {text}")
    print(f"Sentiment: {result[0]['label']}")
    print(f"Confidence: {result[0]['score']:.2%}")
    print("-" * 50) 