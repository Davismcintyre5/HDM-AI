"""
HDM AI - Encryption Utilities
AES-256-CBC for third-party API keys
"""

import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from loguru import logger

from config import settings

# Use JWT secret as encryption key (padded to 32 bytes)
_KEY = settings.JWT_SECRET_KEY.encode("utf-8").ljust(32, b"\x00")[:32]


def _pad(data: bytes) -> bytes:
    """PKCS7 padding."""
    block_size = 16
    padding_len = block_size - (len(data) % block_size)
    return data + bytes([padding_len] * padding_len)


def _unpad(data: bytes) -> str:
    """Remove PKCS7 padding."""
    padding_len = data[-1]
    if padding_len > 16 or padding_len == 0:
        raise ValueError("Invalid padding")
    return data[:-padding_len].decode("utf-8")


def encrypt_key(plaintext: str) -> str:
    """Encrypt a string using AES-256-CBC."""
    try:
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(_pad(plaintext.encode("utf-8"))) + encryptor.finalize()
        encrypted = iv + ciphertext
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_key(encrypted_text: str) -> str:
    """Decrypt an AES-256-CBC encrypted string."""
    try:
        encrypted = base64.b64decode(encrypted_text)
        iv = encrypted[:16]
        ciphertext = encrypted[16:]
        cipher = Cipher(algorithms.AES(_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        return _unpad(padded)
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise