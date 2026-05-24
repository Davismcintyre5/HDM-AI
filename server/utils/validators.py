"""
HDM AI - Input Validators
"""

import re
from typing import Tuple, Optional

VALID_PROJECTS = {"general", "smartpos", "spark", "vibe", "vault", "erp", "widget"}


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, None


def validate_project(project: str) -> bool:
    """Check if project name is valid."""
    return project in VALID_PROJECTS