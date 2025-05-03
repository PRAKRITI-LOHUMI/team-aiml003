from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneauth1.token_endpoint import Token
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_session():
    """Create and return an authenticated session for OpenStack API calls"""
    # If token is available, use token authentication
    if os.getenv('OS_AUTH_TOKEN'):
        auth = Token(
            auth_url=os.getenv('OS_AUTH_URL'),
            token=os.getenv('OS_AUTH_TOKEN'),
            project_id=os.getenv('OS_PROJECT_ID')
        )
    else:
        # Fall back to password authentication
        auth = v3.Password(
            auth_url=os.getenv('OS_AUTH_URL'),
            username=os.getenv('OS_USERNAME'),
            password=os.getenv('OS_PASSWORD'),
            project_id=os.getenv('OS_PROJECT_ID'),
            user_domain_name=os.getenv('OS_USER_DOMAIN_NAME', 'Default')
        )
    
    return session.Session(auth=auth, verify=False)  # Set verify=True in production
