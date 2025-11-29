from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConfigurationBase(BaseModel):
    base_url: str
    hub_address: str
    sleep_time: float = 15.0
    push_token: str
    push_user: str
    df_msg: str

class ConfigurationCreate(ConfigurationBase):
    pass

class ConfigurationUpdate(ConfigurationBase):
    pass

class ConfigurationResponse(ConfigurationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True