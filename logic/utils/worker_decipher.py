# worker_decipher.py
import time
from multiprocessing import Pool
from logic.utils.cipher_core import (
    NGramScorer, apply_key, random_key, mutate_key, QUADGRAMS_PATH
)

def hill_climb(ciphertext, time_limit):
    scorer = NGramScorer(QUADGRAMS_PATH)
    best_key = random_key()
    best_score = scorer.score(apply_key(ciphertext, best_key))
    start_time = time.time()
    attempts = 0

    while time.time() - start_time < time_limit:
        candidate_key = mutate_key(best_key)
        candidate_score = scorer.score(apply_key(ciphertext, candidate_key))
        attempts += 1
        if candidate_score > best_score:
            best_key, best_score = candidate_key, candidate_score

    return (best_key, best_score, attempts)

def run_parallel_decipher(ciphertext, time_budget=10, num_processes=1):
    scorer = NGramScorer(QUADGRAMS_PATH)
    best_key = random_key()
    best_score = scorer.score(apply_key(ciphertext, best_key))
    start_time = time.time()
    attempts = 0

    while time.time() - start_time < time_budget:
        candidate_key = mutate_key(best_key)
        candidate_score = scorer.score(apply_key(ciphertext, candidate_key))
        attempts += 1
        if candidate_score > best_score:
            best_key, best_score = candidate_key, candidate_score

    plaintext = apply_key(ciphertext, best_key)
    return plaintext, attempts, time_budget, 1


if __name__ == "__main__":
    test_ciphertext = input("Paste ciphertext: ")
    plaintext, mutations, seconds, cores = run_parallel_decipher(test_ciphertext)
    print("\nLikely deciphered text:\n")
    print(plaintext)
    print(f"\n[Deciphered using {mutations} mutations over {seconds} seconds x {cores} cores]")
