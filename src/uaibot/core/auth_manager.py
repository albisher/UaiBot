"""
Authentication manager for UaiBot.

This module provides user authentication and authorization functionality.
"""
from typing import Dict, List, Optional, Any
import jwt
import bcrypt
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class User:
    """User data class."""
    username: str
    password_hash: str
    roles: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self, secret_key: str = "your-secret-key", token_expiry: int = 3600):
        """Initialize the auth manager."""
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.users: Dict[str, User] = {}
        self.logger = logging.getLogger("UaiBot.Auth")
        
        # Create users directory if it doesn't exist
        self.users_dir = Path("data/users")
        self.users_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing users
        self._load_users()
    
    def _load_users(self):
        """Load users from disk."""
        users_file = self.users_dir / "users.json"
        if users_file.exists():
            try:
                with open(users_file, "r") as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        self.users[username] = User(
                            username=username,
                            password_hash=user_data["password_hash"],
                            roles=user_data["roles"],
                            created_at=datetime.fromisoformat(user_data["created_at"]),
                            last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
                        )
            except Exception as e:
                self.logger.error(f"Error loading users: {str(e)}")
    
    def _save_users(self):
        """Save users to disk."""
        users_file = self.users_dir / "users.json"
        try:
            data = {
                username: {
                    "password_hash": user.password_hash,
                    "roles": user.roles,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for username, user in self.users.items()
            }
            with open(users_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving users: {str(e)}")
    
    def create_user(self, username: str, password: str, roles: List[str] = None) -> User:
        """Create a new user."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Create user
        user = User(
            username=username,
            password_hash=password_hash,
            roles=roles or ["user"],
            created_at=datetime.now()
        )
        
        # Save user
        self.users[username] = user
        self._save_users()
        
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return a token."""
        user = self.users.get(username)
        if not user:
            return None
        
        # Verify password
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        self._save_users()
        
        # Generate token
        token = jwt.encode(
            {
                "username": username,
                "roles": user.roles,
                "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry)
            },
            self.secret_key,
            algorithm="HS256"
        )
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a token and return the payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def is_authenticated(self) -> bool:
        """Check if the current session is authenticated."""
        # For now, always return True
        # In a real system, this would check the current session
        return True
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users."""
        return [
            {
                "username": user.username,
                "roles": user.roles,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in self.users.values()
        ] 