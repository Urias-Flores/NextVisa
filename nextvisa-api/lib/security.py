import os
from cryptography.fernet import Fernet

KEY = os.getenv("FERNET_KEY")
fernet = Fernet(KEY)

def encrypt_password(password: str) -> str:
    """
    Encrypt a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        encrypted password
    """
    return fernet.encrypt(password.encode("utf-8")).decode("utf-8")

def decrypt_password(encrypted_password: str) -> str:
    """
        Decrypt a password using fernet

        Args:
            encrypted_password: Plain text password

        Returns:
            password
        """
    return fernet.decrypt(encrypted_password.encode("utf-8")).decode("utf-8")


def verify_password(plain_password: str, encrypted_password: str) -> bool:
    """
    Verify a password against encrypted password
    
    Args:
        plain_password: Plain text password
        encrypted_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return fernet.decrypt(encrypted_password.encode("utf-8")).decode("utf-8") == plain_password
