import time

from gensim import models


# load pre-trained Word2Vec model
word2vec_path = "./embedding_models/glove-twitter-25.gz"

start = time.time()
w2v_model = models.KeyedVectors.load_word2vec_format(word2vec_path)
end = time.time()

print("Loaded word2vec model in {} seconds".format(end - start))

word_phil = "philosophy"
words = [
    "cat",
    "dog",
    "car",
    "concept",
    "leader",
    "abstract",
    "red",
    "black",
    "green",
    "building",
    "knife",
    "love",
    "hate",
]
for word in words:
    print(f"{word}: {w2v_model.similarity(word_phil, word)}")
