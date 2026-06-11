import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload

    # AI Provider defaults
    DEFAULT_AI_PROVIDER = 'claude'  # 'claude', 'openai', 'deepseek', or 'fallback'
    CLAUDE_MODEL = 'claude-sonnet-4-20250514'
    OPENAI_MODEL = 'gpt-4o-mini'
    DEEPSEEK_MODEL = 'deepseek-chat'  # DeepSeek-V3

    # Generation settings
    AI_TIMEOUT = 60  # seconds
    AI_MAX_RETRIES = 2


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False
