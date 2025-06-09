# cipher_core.py
import string
import random
import math
import os

# Define the path to the quadgram frequency file
QUADGRAMS_PATH = os.path.join(os.path.dirname(__file__), "english_quadgrams.txt")

class NGramScorer:
    def __init__(self, ngram_path):
        self.ngrams = {}
        self.N = 0
        with open(ngram_path, 'r') as f:
            for line in f:
                key, count = line.strip().split()
                self.ngrams[key] = int(count)
                self.N += int(count)
        self.L = math.log10(self.N)
        self.floor = math.log10(0.01 / self.N)

    def score(self, text):
        score = 0
        text = text.upper()
        for i in range(len(text) - 3):
            quad = text[i:i+4]
            if quad in self.ngrams:
                score += math.log10(self.ngrams[quad]) - self.L
            else:
                score += self.floor
        return score

def apply_key(text, key_map):
    inverse_map = {v: k for k, v in key_map.items()}
    result = []
    for char in text:
        if char.upper() in inverse_map:
            plain = inverse_map[char.upper()]
            result.append(plain.lower() if char.islower() else plain)
        else:
            result.append(char)
    return ''.join(result)

def random_key():
    alpha = list(string.ascii_uppercase)
    shuffled = alpha[:]
    random.shuffle(shuffled)
    return dict(zip(alpha, shuffled))

def mutate_key(key_map):
    a, b = random.sample(list(key_map.values()), 2)
    mutated = key_map.copy()
    for k, v in key_map.items():
        if v == a:
            mutated[k] = b
        elif v == b:
            mutated[k] = a
    return mutated
