# File for DB connection and reusable config

import os  # For environment variables
from dotenv.main import load_dotenv

load_dotenv() # Load variables from the .env file

# Database connection setup
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432)
}