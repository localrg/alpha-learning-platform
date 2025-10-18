import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)

# Add the src directory to Python path
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)

# Import app from src/main.py
from src.main import app

if __name__ == "__main__":
    app.run()
