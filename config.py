"""
Central configuration for AI Agent for Smart Farming Advice.
Loads credentials from config.env (or environment variables).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from config.env if present
env_path = Path(__file__).parent / "config.env"
if env_path.exists():
    load_dotenv(env_path)

# IBM watsonx.ai credentials
IBM_API_KEY = os.getenv("IBM_API_KEY", "KJkn9AATL29Wl3XQ12vHqb1DJD7gJr4sqWFKvOUr9Ld6")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "81bcc076-b2a6-4039-a511-842212629b94")
IBM_WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# IBM Granite model IDs  (only ibm/granite-4-h-small is available on this project)
GRANITE_TEXT_MODEL  = "ibm/granite-4-h-small"
GRANITE_CHAT_MODEL  = "ibm/granite-4-h-small"
GRANITE_VISION_MODEL = "ibm/granite-4-h-small"

# OpenWeatherMap (free tier demo key – replace for production)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Chroma vector store path
VECTOR_STORE_PATH = "./data/vectorstore"

# Max tokens for generation
MAX_NEW_TOKENS = 1024
