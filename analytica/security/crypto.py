from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

def encrypt_data(key: bytes, plaintext: str) -> str:
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_data(key: bytes, encrypted: str) -> str:
    raw = base64.b64decode(encrypted)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext, None).decode()
