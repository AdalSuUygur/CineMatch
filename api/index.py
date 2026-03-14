import os
import sys

# Add the root directory to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_path)

from backend.main import app
