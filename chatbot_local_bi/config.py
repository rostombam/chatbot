import os
from dotenv import load_dotenv

# Load environment variables from .env file specifically for config
# This ensures that OPENAI_API_KEY is loaded when the app starts
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    DEBUG = False
    TESTING = False
    PORT = int(os.environ.get('PORT', 5001)) # Default to 5001 for Flask dev server

    # OpenAI API Key
    # It's crucial that this is set in your environment or .env file
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # Application specific configurations
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads') # Example, not used in current app.py
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit, example

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # In development, you might use a fixed SECRET_KEY or a more lenient one
    # SECRET_KEY = 'dev_secret_key' # Example, override if needed

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use a separate database or test configurations
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Example for testing with DB

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure SECRET_KEY is strong and set via environment variable
    # PORT might be managed by gunicorn or other WSGI server in production

# Helper to get config based on environment variable
# Not strictly necessary for this simple app but good practice
# def get_config():
#     env = os.environ.get('FLASK_ENV', 'development').lower()
#     if env == 'production':
#         return ProductionConfig()
#     elif env == 'testing':
#         return TestingConfig()
#     return DevelopmentConfig()

# Ensure the UPLOAD_FOLDER exists if you plan to use it
# if not os.path.exists(Config.UPLOAD_FOLDER):
#     os.makedirs(Config.UPLOAD_FOLDER)

# Validate that OPENAI_API_KEY is present at startup
if not Config.OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY set. Please set this environment variable or in the .env file.")
