import gensim.downloader as api
print(api.BASE_DIR)
from numpy import dot
from numpy.linalg import norm

# טען את המודל
model = api.load("word2vec-google-news-300")

def get_embedding(word: str):
    return model[word]

def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def analogy(word_a, word_b, word_c, model, topn=1):
    # word_a is to word_b as word_c is to ?
    result = model.most_similar(positive=[word_b, word_c], negative=[word_a], topn=topn)
    return result

# דוגמה לשימוש
word_pairs = [
    ("run", "walk"),
    ("run", "runs"),
    ("king", "kings"),
    ("big", "large"),
    ("big", "bigger"),
    ("man", "woman"),
]

for w1, w2 in word_pairs:
    emb1 = get_embedding(w1)
    emb2 = get_embedding(w2)
    sim = cosine_similarity(emb1, emb2)
    print(f"Cosine similarity between '{w1}' and '{w2}': {sim}")

# דוגמה:
result = analogy("teacher", "school", "doctor", model, topn=10)
print(result)

