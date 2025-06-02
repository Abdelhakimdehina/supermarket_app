import hashlib
import os

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt"""
    # In a real application, you would use a proper password hashing algorithm like bcrypt
    # This is a simplified version for demonstration purposes
    salt = "supermarket_salt"  # In production, this should be a random salt per user
    salted = password + salt
    return hashlib.sha256(salted.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed