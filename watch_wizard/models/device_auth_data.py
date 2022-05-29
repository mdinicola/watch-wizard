from dataclasses import dataclass

@dataclass
class DeviceAuthData:
    user_code: str
    device_code: str
    verification_url: str
    poll_interval: int