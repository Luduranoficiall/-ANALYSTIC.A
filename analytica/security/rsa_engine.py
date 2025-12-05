from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


# Geração das chaves
def generate_keys():
    private = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public = private.public_key()
    return private, public

def rsa_sign(private_key, message: str):
    return private_key.sign(
        message.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

def rsa_verify(public_key, message: str, signature: bytes):
    return public_key.verify(
        signature,
        message.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
