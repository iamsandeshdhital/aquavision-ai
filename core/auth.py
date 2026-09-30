"""
Authentication Module
Secures API and dashboard access.
"""

import hashlib
import secrets
import time
import threading
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class User:
    """Represents an authenticated user."""
    username: str
    password_hash: str
    role: str  # "admin", "operator", "viewer"
    created_at: float
    last_login: Optional[float] = None


@dataclass
class Session:
    """Represents an active session."""
    token: str
    username: str
    role: str
    created_at: float
    expires_at: float


class AuthManager:
    """Manages user authentication and sessions."""

    def __init__(self, config: dict):
        self.config = config
        self._lock = threading.Lock()
        self._running = False

        # Session timeout (default 24 hours)
        self.session_timeout = config.get("auth", {}).get("session_timeout_hours", 24) * 3600

        # In-memory user store (in production, use database)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}

        # Add default admin user
        self._add_default_users()

    def _add_default_users(self):
        """Add default users from config."""
        default_users = self.config.get("auth", {}).get("users", [])
        for user_config in default_users:
            self.register_user(
                user_config.get("username", ""),
                user_config.get("password", ""),
                user_config.get("role", "viewer")
            )

        # If no users configured, add default admin
        if not self.users:
            self.register_user("admin", "admin123", "admin")

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str, role: str = "viewer") -> bool:
        """Register a new user."""
        with self._lock:
            if username in self.users:
                return False
            self.users[username] = User(
                username=username,
                password_hash=self._hash_password(password),
                role=role,
                created_at=time.time()
            )
        return True

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return session token."""
        with self._lock:
            if username not in self.users:
                return None

            user = self.users[username]
            if user.password_hash != self._hash_password(password):
                return None

            # Create session
            token = secrets.token_urlsafe(32)
            session = Session(
                token=token,
                username=username,
                role=user.role,
                created_at=time.time(),
                expires_at=time.time() + self.session_timeout
            )
            self.sessions[token] = session
            user.last_login = time.time()

            return token

    def validate_token(self, token: str) -> Optional[Session]:
        """Validate a session token."""
        with self._lock:
            if token not in self.sessions:
                return None

            session = self.sessions[token]
            if time.time() > session.expires_at:
                del self.sessions[token]
                return None

            return session

    def logout(self, token: str):
        """Logout a user."""
        with self._lock:
            if token in self.sessions:
                del self.sessions[token]

    def check_permission(self, token: str, required_role: str) -> bool:
        """Check if a user has the required permission."""
        session = self.validate_token(token)
        if not session:
            return False

        role_hierarchy = {"viewer": 0, "operator": 1, "admin": 2}
        user_level = role_hierarchy.get(session.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.users.get(username)

    def list_users(self) -> list:
        """List all users (admin only)."""
        with self._lock:
            return [
                {
                    "username": u.username,
                    "role": u.role,
                    "created_at": u.created_at,
                    "last_login": u.last_login
                }
                for u in self.users.values()
            ]

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        with self._lock:
            current_time = time.time()
            expired = [token for token, session in self.sessions.items() if current_time > session.expires_at]
            for token in expired:
                del self.sessions[token]
