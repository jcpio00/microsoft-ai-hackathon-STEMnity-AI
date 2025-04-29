import os
from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_MODEL_ID = os.getenv("GITHUB_MODEL_ID")

if not GITHUB_PAT:
    print("Warning: GITHUB_PAT environment variable not set.")
if not GITHUB_MODEL_ID:
    print("Warning: GITHUB_MODEL_ID environment variable not set.")
