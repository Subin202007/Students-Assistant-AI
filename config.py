import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    AI_API_KEY = os.getenv('AI_API_KEY', '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')
    AI_API_URL = os.getenv('AI_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
    AI_MODEL = os.getenv('AI_MODEL', 'openrouter/free')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg'}