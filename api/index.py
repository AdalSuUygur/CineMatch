import os
import sys

# Add the project root to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Also add backend path for flexibility
backend_path = os.path.join(root_path, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.main import app
