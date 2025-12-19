import os
import logging
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class SupabaseConnection:
    __instance = None
    __client: Client | None = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SupabaseConnection, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

            # Debug logging to verify environment variables are loaded
            if url:
                # Mask the URL for security, only show first 20 characters
                masked_url = url[:20] + "..." if len(url) > 20 else url
                logger.info(f"SUPABASE_URL loaded: {masked_url}")
            else:
                logger.error("SUPABASE_URL is not set or empty")
            
            if key:
                logger.info(f"SUPABASE_KEY loaded: {key[:10]}...")
            else:
                logger.error("SUPABASE_KEY is not set or empty")

            if not url:
                raise Exception("SUPABASE_URL environment variable is missing or empty. Check your .env file.")
            if not key:
                raise Exception("SUPABASE_KEY environment variable is missing or empty. Check your .env file.")

            try:
                logger.info(f"Attempting to connect to Supabase at: {url}")
                self.__class__.__client = create_client(url, key)
                logger.info("Supabase connection created successfully")
            except Exception as e:
                logger.error(f"Failed to create Supabase client. URL: {url}, Error: {e}")
                logger.exception("Full exception details:")
                raise e

    @classmethod
    def get_client(cls) -> Client:
        if cls.__client is None:
            cls()
        return cls.__client
