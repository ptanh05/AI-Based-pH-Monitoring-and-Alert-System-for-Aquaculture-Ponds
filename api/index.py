import os
import sys

# Ensure root directory and current working directory are in sys.path for module resolution on Vercel
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [ROOT_DIR, os.getcwd(), "/var/task"]:
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from api.server import app
