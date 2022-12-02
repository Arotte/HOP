# C:\Users\thear\AppData\Local\Programs\Python\Python36\python.exe bert_server.py

''' bert_server.py

    This is a server that calculates word embeddings
    and word similairty scores to the 'philosophy' word.

    Requires Python 3.6 (excatly) and the following packages:
    - bert-embedding
    - flask

    python -m pip install bert-embedding flask

    Usage:
    path/to/python3.6 bert_server.py
'''
# C:\Users\thear\AppData\Local\Programs\Python\Python36\python.exe -m pip install bert-embedding flask
# C:\Users\thear\AppData\Local\Programs\Python\Python36\python.exe -m pip list

from bert_embedding import BertEmbedding
import numpy as np
import re
from numpy import dot
from numpy.linalg import norm
from flask import Flask, request, jsonify

app = Flask(__name__)
bert = BertEmbedding()

# ==================================================================================
# CONSTANTS
# ==================================================================================

PHIL_EMBEDDING_PATH = 'bert_embedding_phil.csv'
SERVER_PORT = 5000
RESTART_ON_SAVE = False


def rm_non_alphanum(seq: str) -> str:
    """Remove non-alphanumeric characters from a string"""
    return re.sub(r"\W+", "", seq)  

# ==================================================================================
# BERT EMBEDDING
# ==================================================================================

def embed_txt_bert(txt: str) -> tuple:
    """
    Embeds a text using BERT.
    :param txt: The text to be embedded.
    :return: The embedding of the text.
    """
    try:
        sentences = txt.split('\n')
        # sentences = txt.split('. ')
    except:
        sentences = [txt]

    result = bert(sentences)
    return result


def embed_word_bert(txt_embed_result: tuple, word: str) -> list:
    """
    Embeds a word using BERT.
    :param txt_embed_result: The embedding of the text.
    :param word: The word to be embedded.
    :return: The embedding of the word.
    """
    embeds_for_word = []
    for i in range(len(txt_embed_result)):  # sentences
        for j in range(len(txt_embed_result[i][0])):  # words
            if txt_embed_result[i][0][j].lower().strip() == word.lower().strip():
                embeds_for_word.append(txt_embed_result[i][1][j])
    
    if len(embeds_for_word) == 0:
        return None

    mean_vec = np.mean(embeds_for_word, axis=0)
    return mean_vec.tolist()


def load_phil_bert_embedding(fpath: str) -> list:
    """
    Load the BERT embedding of the
    word 'philosophy' from a csv file.
    """
    import csv
    ph_emb = []
    with open(fpath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            ph_emb.append(float(row[0]))
    return ph_emb


def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Computes the cosine similarity between two vectors.
    :param vec1: The first vector.
    :param vec2: The second vector.
    :return: The cosine similarity between the two vectors.
    """
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

# ==================================================================================
# SERVER ENDPOINTS
# ==================================================================================

@app.route('/embed', methods=['POST'])
def embed():
    ''' Calculate word embeddings for the given words. 
        Requires a JSON object with a 'words' and a 'text' field.
    '''

    print('Received request /embed')
    
    data = request.get_json()
    words = data['words']
    text = data['text']

    # Embed the text
    txt_embed_result = embed_txt_bert(text)

    # Embed the words
    word_embeddings = []
    for word in words:
        word_embeddings.append(embed_word_bert(txt_embed_result, word))

    # Return the embeddings
    return jsonify(word_embeddings)


@app.route('/similarity', methods=['POST'])
def similarity():
    ''' Calculate the similarity between the given words and the word 'philosophy'.
        Requires a JSON object with a 'words' and a 'text' field.
    '''

    print('Received request /similarity')

    data = request.get_json()
    words = data['words']
    text = data['text']

    # print(text)

    # Embed the text
    txt_embed_result = embed_txt_bert(text)

    # Embed the words

    def handle_multi_word(w, delimeter):
        # handle words that are multiple words
        word_parts = w.split(delimeter)
        part_embeddings = []
        for part in word_parts:
            part_embedding = embed_word_bert(txt_embed_result, part)
            if part_embedding is not None:
                part_embeddings.append(part_embedding)
        
        if len(part_embeddings) == 0:
            return None
        else:
            return np.mean(part_embeddings, axis=0).tolist()

    word_embeddings = []
    for word in words:
        # word = rm_non_alphanum(word)
        embedding = embed_word_bert(txt_embed_result, word)

        if ' ' in word and embedding is None:
            word_embeddings.append(handle_multi_word(word, ' '))
        elif '-' in word and embedding is None:
            word_embeddings.append(handle_multi_word(word, '-'))
        else:
            word_embeddings.append(embedding)


    # Load the philosophy embedding
    phil_embedding = load_phil_bert_embedding(PHIL_EMBEDDING_PATH)


    # Calculate the similarity
    similarities = []
    for word_embedding in word_embeddings:
        if word_embedding is None:
            similarities.append(None)
        else:
            similarities.append(cosine_similarity(word_embedding, phil_embedding))


    def most_similar():
        res = zip(words, similarities)
        most_sim_word = ''
        most_sim_score = 0.0

        for w, sim in res:
            if sim is not None and sim > most_sim_score and w != '':
                most_sim_word = w
                most_sim_score = sim

        return most_sim_word, most_sim_score


    # Return the similarities
    return jsonify({
        'similarities': similarities,
        'winner': most_similar()
    })

# ==================================================================================
# RUN SERVER
# ==================================================================================

if __name__ == '__main__':
    print('BERT embedding server started.')
    
    # Run the server
    app.run(port=SERVER_PORT, debug=True, use_reloader=RESTART_ON_SAVE)
