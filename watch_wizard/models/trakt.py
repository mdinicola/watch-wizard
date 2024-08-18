from pydantic import BaseModel
   
class DeviceAuthData(BaseModel):
    user_code: str
    device_code: str
    verification_url: str
    poll_interval: int