import os
import json
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from functools import wraps

@dataclass
class User:
    """Represents a user in the system."""
    username: str
    password_hash: str
    roles: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/Documents/uaibot/config")
        self.users_file = os.path.join(self.config_dir, "users.json")
        self.secret_key = self._load_or_generate_secret_key()
        os.makedirs(self.config_dir, exist_ok=True)
        self.users: Dict[str, User] = self._load_users()
        
    def _load_or_generate_secret_key(self) -> str:
        """Load or generate a secret key for JWT signing."""
        key_file = os.path.join(self.config_dir, "secret_key.txt")
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip()
        else:
            key = secrets.token_hex(32)
            with open(key_file, 'w') as f:
                f.write(key)
            return key
            
    def _load_users(self) -> Dict[str, User]:
        """Load users from the users file."""
        if not os.path.exists(self.users_file):
            return {}
            
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        users = {}
        for username, user_data in data.items():
            users[username] = User(
                username=username,
                password_hash=user_data['password_hash'],
                roles=user_data['roles'],
                created_at=datetime.fromisoformat(user_data['created_at']),
                last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                is_active=user_data.get('is_active', True)
            )
        return users
        
    def _save_users(self):
        """Save users to the users file."""
        data = {}
        for username, user in self.users.items():
            data[username] = {
                'password_hash': user.password_hash,
                'roles': user.roles,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active
            }
            
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_user(self, username: str, password: str, roles: List[str] = None) -> User:
        """Create a new user."""
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")
            
        user = User(
            username=username,
            password_hash=self._hash_password(password),
            roles=roles or ['user'],
            created_at=datetime.now()
        )
        
        self.users[username] = user
        self._save_users()
        return user
        
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return a JWT token."""
        user = self.users.get(username)
        if not user or not user.is_active:
            return None
            
        if user.password_hash != self._hash_password(password):
            return None
            
        # Update last login
        user.last_login = datetime.now()
        self._save_users()
        
        # Generate JWT token
        token = jwt.encode(
            {
                'username': username,
                'roles': user.roles,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            self.secret_key,
            algorithm='HS256'
        )
        
        return token
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return the payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.InvalidTokenError:
            return None
            
    def has_role(self, token: str, role: str) -> bool:
        """Check if a user has a specific role."""
        payload = self.verify_token(token)
        if not payload:
            return False
        return role in payload.get('roles', [])
        
    def require_auth(self, roles: Optional[List[str]] = None):
        """Decorator to require authentication for a function."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                token = kwargs.get('token')
                if not token:
                    raise ValueError("Authentication required")
                    
                payload = self.verify_token(token)
                if not payload:
                    raise ValueError("Invalid token")
                    
                if roles:
                    if not any(role in payload.get('roles', []) for role in roles):
                        raise ValueError("Insufficient permissions")
                        
                return func(*args, **kwargs)
            return wrapper
        return decorator
        
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.users.get(username)
        
    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """Update a user's properties."""
        user = self.users.get(username)
        if not user:
            return None
            
        if 'password' in kwargs:
            user.password_hash = self._hash_password(kwargs['password'])
        if 'roles' in kwargs:
            user.roles = kwargs['roles']
        if 'is_active' in kwargs:
            user.is_active = kwargs['is_active']
            
        self._save_users()
        return user
        
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username not in self.users:
            return False
            
        del self.users[username]
        self._save_users()
        return True
        
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (excluding password hashes)."""
        return [
            {
                'username': user.username,
                'roles': user.roles,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active
            }
            for user in self.users.values()
        ] 