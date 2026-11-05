import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Application Settings
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "loan_approval.db"))

# FastAPI Server Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 2000))

# Agent Configuration
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 30))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# MCP Server Configuration
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", 10))

# Loan Approval Business Rules
MIN_CREDIT_SCORE = int(os.getenv("MIN_CREDIT_SCORE", 600))
MAX_DTI_RATIO = float(os.getenv("MAX_DTI_RATIO", 0.45))
MIN_INCOME = int(os.getenv("MIN_INCOME", 30000))

# Logging Configuration
def setup_logging():
    """Configure logging for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)

    # File handler
    log_file = LOG_DIR / "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger

# Initialize logger
logger = setup_logging()

# Configuration summary (for debugging)
if DEBUG:
    logger.info("=" * 50)
    logger.info("Application Configuration")
    logger.info("=" * 50)
    logger.info(f"Environment: {APP_ENV}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info(f"Database Path: {DATABASE_PATH}")
    logger.info(f"API Server: {API_HOST}:{API_PORT}")
    logger.info(f"LLM Model: {LLM_MODEL}")
    logger.info("=" * 50)
