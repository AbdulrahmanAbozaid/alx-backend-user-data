#!/usr/bin/env python3
"""
This module contains functionality for hashing and verifying passwords.
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt with a salt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validate if the provided password matches the hashed password.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
