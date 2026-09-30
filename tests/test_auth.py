"""Tests for Authentication Module"""
import unittest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.auth import AuthManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.config = {"auth": {"session_timeout_hours": 24, "users": []}}
        self.auth = AuthManager(self.config)

    def test_initialization(self):
        self.assertIsNotNone(self.auth)

    def test_register_user(self):
        result = self.auth.register_user("testuser", "testpass", "operator")
        self.assertTrue(result)

    def test_authenticate_success(self):
        self.auth.register_user("testuser", "testpass", "operator")
        token = self.auth.authenticate("testuser", "testpass")
        self.assertIsNotNone(token)

    def test_authenticate_failure(self):
        self.auth.register_user("testuser", "testpass", "operator")
        token = self.auth.authenticate("testuser", "wrongpass")
        self.assertIsNone(token)

    def test_validate_token(self):
        self.auth.register_user("testuser", "testpass", "operator")
        token = self.auth.authenticate("testuser", "testpass")
        session = self.auth.validate_token(token)
        self.assertIsNotNone(session)

    def test_logout(self):
        self.auth.register_user("testuser", "testpass", "operator")
        token = self.auth.authenticate("testuser", "testpass")
        self.auth.logout(token)
        session = self.auth.validate_token(token)
        self.assertIsNone(session)

    def test_check_permission(self):
        # Default admin user already exists with password "admin123"
        token = self.auth.authenticate("admin", "admin123")
        self.assertTrue(self.auth.check_permission(token, "operator"))

if __name__ == "__main__":
    unittest.main()
