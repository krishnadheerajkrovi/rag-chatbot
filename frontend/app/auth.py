import streamlit as st
import requests
from jose import jwt
from jose.exceptions import JWTError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class Auth:
    def __init__(self):
        self.token = None
        self.user = None
        self._load_session()

    def _load_session(self):
        """Load user session from Streamlit session state"""
        if 'token' in st.session_state:
            self.token = st.session_state.token
            self.user = st.session_state.get('user')

    def _save_session(self, token, user=None):
        """Save user session to Streamlit session state"""
        st.session_state.token = token
        if user:
            st.session_state.user = user
        self.token = token
        self.user = user

    def clear_session(self):
        """Clear user session"""
        if 'token' in st.session_state:
            del st.session_state.token
        if 'user' in st.session_state:
            del st.session_state.user
        self.token = None
        self.user = None

    def is_authenticated(self):
        """Check if user is authenticated"""
        if not self.token:
            return False
        try:
            # Verify token is not expired
            payload = jwt.get_unverified_claims(self.token)
            return True
        except JWTError:
            return False

    def get_user_info(self):
        """Get user information from token"""
        if not self.token:
            return None
        try:
            payload = jwt.get_unverified_claims(self.token)
            return {
                'username': payload.get('sub'),
                'email': payload.get('email')
            }
        except JWTError:
            return None

    def login(self, username: str, password: str) -> bool:
        """Attempt to log in with username and password"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token_data = response.json()
                user_info = self.get_user_info_from_token(token_data["access_token"])
                self._save_session(token_data["access_token"], user_info)
                return True
            return False
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False

    def get_user_info_from_token(self, token: str) -> dict:
        """Extract user information from JWT token"""
        try:
            payload = jwt.get_unverified_claims(token)
            return {
                'username': payload.get('sub'),
                'email': payload.get('email'),
                'is_admin': payload.get('is_admin', False)
            }
        except JWTError:
            return {}

auth = Auth()
