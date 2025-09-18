import os
import json
import base64
from typing import Dict, Any
from argon2.low_level import hash_secret_raw, Type as Argon2Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SALT_LEN = 16
AES_GCM_NONCE = 12
KEY_LEN = 32

DEFAULT_ARGON2_PARAMS = {
    "time_cost": 3,
    "memory_cost": 65536,
    "parallelism": 4,
    "hash_len": KEY_LEN,
    "type": Argon2Type.ID,
}

CURRENT_VERSION = 2


def _b64u_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _b64u_decode(s: str) -> bytes:
    s_bytes = s.encode("ascii")
    padding = b"=" * ((4 - len(s_bytes) % 4) % 4)
    return base64.urlsafe_b64decode(s_bytes + padding)


def _derive_master_key(password: str, salt: bytes, params: Dict[str, Any]) -> bytes:
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    
    argon2_type = params["type"]
    if isinstance(argon2_type, str):
        argon2_type = Argon2Type.ID if argon2_type == "ID" else Argon2Type.I
    
    return hash_secret_raw(
        secret=password_bytes,
        salt=salt,
        time_cost=params["time_cost"],
        memory_cost=params["memory_cost"],
        parallelism=params["parallelism"],
        hash_len=params["hash_len"],
        type=argon2_type
    )


def encrypt_secret(plaintext: str, master_password: str) -> str:
    plaintext_bytes = plaintext.encode("utf-8")

    master_salt = os.urandom(SALT_LEN)
    master_key = _derive_master_key(master_password, master_salt, DEFAULT_ARGON2_PARAMS)

    secret_key = os.urandom(KEY_LEN)
    aes_secret = AESGCM(secret_key)
    secret_nonce = os.urandom(AES_GCM_NONCE)
    encrypted_data = aes_secret.encrypt(secret_nonce, plaintext_bytes, associated_data=None)

    aes_master = AESGCM(master_key)
    master_nonce = os.urandom(AES_GCM_NONCE)
    encrypted_secret_key = aes_master.encrypt(master_nonce, secret_key, associated_data=None)

    payload = {
        "v": CURRENT_VERSION,
        "kdf": "argon2id",
        "master_salt": _b64u_encode(master_salt),
        "master_nonce": _b64u_encode(master_nonce),
        "encrypted_secret_key": _b64u_encode(encrypted_secret_key),
        "secret_nonce": _b64u_encode(secret_nonce),
        "encrypted_secret": _b64u_encode(encrypted_data),
        "argon2_params": {
            "time_cost": DEFAULT_ARGON2_PARAMS["time_cost"],
            "memory_cost": DEFAULT_ARGON2_PARAMS["memory_cost"],
            "parallelism": DEFAULT_ARGON2_PARAMS["parallelism"],
            "hash_len": DEFAULT_ARGON2_PARAMS["hash_len"],
            "type": "ID",
        },
    }

    json_blob = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64u_encode(json_blob)


def decrypt_secret(blob: str, master_password: str) -> str:
    json_bytes = _b64u_decode(blob)
    payload = json.loads(json_bytes.decode('utf-8') if isinstance(json_bytes, bytes) else json_bytes)

    master_salt = _b64u_decode(payload["master_salt"])
    secret_nonce = _b64u_decode(payload["secret_nonce"])
    encrypted_secret = _b64u_decode(payload["encrypted_secret"])
    encrypted_secret_key = _b64u_decode(payload["encrypted_secret_key"])
    master_nonce = _b64u_decode(payload["master_nonce"])
    params = payload["argon2_params"]

    master_key = _derive_master_key(master_password, master_salt, params)
    aes_master = AESGCM(master_key)
    secret_key = aes_master.decrypt(master_nonce, encrypted_secret_key, associated_data=None)

    aes_secret = AESGCM(secret_key)
    plaintext_bytes = aes_secret.decrypt(secret_nonce, encrypted_secret, associated_data=None)
    return plaintext_bytes.decode("utf-8")