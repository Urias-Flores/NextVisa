from lib.database import SupabaseConnection
from models.configuration import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_configuration() -> ConfigurationResponse:
    try:
        db = SupabaseConnection.get_client()
        # Get the first configuration found (assuming single config for now)
        response = db.from_("configuration").select("*").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            return ConfigurationResponse(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Unable to get configuration", e)
        raise e

def create_configuration(config: ConfigurationCreate) -> ConfigurationResponse:
    try:
        db = SupabaseConnection.get_client()
        data = config.dict()
        response = db.from_("configuration").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return ConfigurationResponse(**response.data[0])
        raise Exception("Failed to create configuration")
    except Exception as e:
        logger.error(f"Unable to create configuration", e)
        raise e

def update_configuration(id: int, config: ConfigurationUpdate) -> ConfigurationResponse:
    try:
        db = SupabaseConnection.get_client()
        data = config.dict(exclude_unset=True)
        data['updated_at'] = datetime.now().isoformat()
        
        response = db.from_("configuration").update(data).eq("id", id).execute()
        
        if response.data and len(response.data) > 0:
            return ConfigurationResponse(**response.data[0])
        raise Exception(f"Failed to update configuration with id {id}")
    except Exception as e:
        logger.error(f"Unable to update configuration", e)
        raise e