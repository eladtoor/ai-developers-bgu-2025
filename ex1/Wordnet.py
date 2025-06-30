import nltk
from nltk.corpus import wordnet

def get_synonyms(word):
    """
    Get all synonyms for a given word using WordNet.
    
    Args:
        word (str): The word to find synonyms for
    
    Returns:
        list: A list of synonyms for the given word
    """
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() != word:  # Exclude the original word
                synonyms.append(lemma.name())
    return list(set(synonyms))  # Remove duplicates

def get_hypernyms(word):
    """
    Get all hypernyms for a given word using WordNet.
    
    Args:
        word (str): The word to find hypernyms for
    
    Returns:
        list: A list of hypernyms for the given word
    """
    hypernyms = []
    for syn in wordnet.synsets(word):
        for hypernym in syn.hypernyms():
            for lemma in hypernym.lemmas():
                hypernyms.append(lemma.name())
    return list(set(hypernyms))  # Remove duplicates

# Example usage
'''
if __name__ == "__main__":
    # Download required NLTK data if not already downloaded
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    
    # Example word
    test_word = "happy"
    
    # Get and print synonyms
    print(f"\nSynonyms for '{test_word}':")
    synonyms = get_synonyms(test_word)
    for synonym in synonyms:
        print(f"- {synonym}")
    
    # Get and print hypernyms
    print(f"\nHypernyms for '{test_word}':")
    hypernyms = get_hypernyms(test_word)
    for hypernym in hypernyms:
        print(f"- {hypernym}")
'''

# Get synonyms for a word
synonyms = get_synonyms("nice")
print("Synonyms:", synonyms)
print("--------------------------------")

# Get hypernyms for a word
hypernyms = get_hypernyms("dog")
print("Hypernyms:", hypernyms)
print("--------------------------------") 