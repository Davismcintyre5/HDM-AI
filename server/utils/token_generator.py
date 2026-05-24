# ====================================================================================================
# server/utils/token_generator.py
# ====================================================================================================
"""
HDM AI - Token & API Key Generator
"""

import secrets
import hashlib
from typing import Tuple


def generate_api_key(prefix: str = "hdm_") -> str:
    """Generate a cryptographically secure API key with prefix."""
    random_part = secrets.token_hex(24)  # 48 hex chars
    return f"{prefix}{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for database storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(plain_key) == hashed_key


def generate_project_keys() -> dict:
    """Generate all 7 project keys with prefixes."""
    prefixes = {
        "general": "hdm_gen_",
        "smartpos": "hdm_pos_",
        "spark": "hdm_spk_",
        "vibe": "hdm_vib_",
        "vault": "hdm_vlt_",
        "erp": "hdm_erp_",
        "widget": "hdm_wdg_",
    }
    return {name: generate_api_key(prefix) for name, prefix in prefixes.items()}