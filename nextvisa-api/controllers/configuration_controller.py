from services import configuration_services
from models.configuration import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("", response_model=ConfigurationResponse)
def get_configuration():
    """Get the current configuration"""
    try:
        config = configuration_services.get_configuration()
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=ConfigurationResponse)
def create_configuration(config: ConfigurationCreate):
    """Create a new configuration"""
    try:
        return configuration_services.create_configuration(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=ConfigurationResponse)
def update_configuration(id: int, config: ConfigurationUpdate):
    """Update the configuration"""
    try:
        return configuration_services.update_configuration(id, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))