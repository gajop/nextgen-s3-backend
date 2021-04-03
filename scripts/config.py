from dotenv import load_dotenv
import os

load_dotenv()

SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')
SPACES_REGION_NAME = os.getenv('SPACES_REGION_NAME')
SPACES_ENDPOINT_URL = os.getenv('SPACES_ENDPOINT_URL')
SPACES_BUCKET = os.getenv('SPACES_BUCKET')
REMOVE_ON_UPLOAD = os.getenv('REMOVE_ON_UPLOAD') == 'true'
HISTORY_GENERATION_SIZE = int(os.getenv('HISTORY_GENERATION_SIZE'))