import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# For Vercel deployment - this is the entry point
# The app is already configured in app.py with all routes