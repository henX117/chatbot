# decipher.py
import os
import sys

# Allow relative import of logic.* from this script
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logic.utils.worker_decipher import run_parallel_decipher


def main():
    if len(sys.argv) < 2:
        print("Usage: python decipher.py '<ciphertext>'")
        sys.exit(1)

    ciphertext = sys.argv[1]
    print("Starting deciphering...")  # Add debug line
    plaintext, mutations, seconds, cores = run_parallel_decipher(ciphertext, time_budget=20, num_processes=4)

    print("[[BEGIN-DECRYPTED]]")
    print(plaintext)
    print("[[END-DECRYPTED]]")
    print(f"[INFO] Used {mutations} mutations over {seconds} seconds on {cores} cores.")

if __name__ == "__main__":
    main()
