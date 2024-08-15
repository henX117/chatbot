import string
import random

class Cipher:
    def __init__(self):
        self.cipher_map = None

    def generate_random_cipher(self):
        alphabet = list(string.ascii_uppercase)
        shuffled = alphabet[:]
        random.shuffle(shuffled)
        self.cipher_map = dict(zip(alphabet, shuffled))
        return self.cipher_map

    def set_custom_cipher(self, custom_key):
        if len(custom_key) == 26 and len(set(custom_key)) == 26 and all(char in string.ascii_uppercase for char in custom_key):
            self.cipher_map = dict(zip(string.ascii_uppercase, custom_key))
        else:
            raise ValueError("Invalid key. Must be 26 unique uppercase letters.")

    def cipher_text(self, text):
        if not self.cipher_map:
            raise ValueError("Cipher map is not set.")
        result = []
        for char in text:
            if char.upper() in self.cipher_map:
                transformed = self.cipher_map[char.upper()]
                result.append(transformed.lower() if char.islower() else transformed)
            else:
                result.append(char)
        return ''.join(result)

    def decipher_text(self, text):
        if not self.cipher_map:
            raise ValueError("Cipher map is not set.")
        inverse_cipher = {v: k for k, v in self.cipher_map.items()}
        result = []
        for char in text:
            if char.upper() in inverse_cipher:
                transformed = inverse_cipher[char.upper()]
                result.append(transformed.lower() if char.islower() else transformed)
            else:
                result.append(char)
        return ''.join(result)
