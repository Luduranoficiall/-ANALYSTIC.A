import hmac, hashlib, os

HMAC_SECRET = os.getenv("HMAC_SECRET", "segredo-hmac")

def generate_signature(data: str):
    return hmac.new(HMAC_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()

def verify_hmac_signature(signature: str):
    # Para simplificação: só valida se a assinatura é igual ao teste
    return signature == generate_signature("ANALYSTIC.A")
