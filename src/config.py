import os
from pydantic import BaseModel

class PlatformConfig(BaseModel):
    PLATFORM_NAME: str = "KARIS OS™"
    PLATFORM_VERSION: str = "1.0.0-PROD-V1"
    DEFAULT_CURRENCY: str = "KES"
    DEFAULT_COUNTRY: str = "KE"
    LEDGER_IMMUTABLE: bool = True
    EVENT_DRIVEN_STRICT: bool = True
    KRT_MINT_ON_PURCHASE_RATIO: float = 0.05  # 5% of purchase value awarded as KRT
    KRT_KES_EXCHANGE_RATE: float = 1.0        # 1 KRT = 1 KES (Administrator Configurable)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./karis_os_core.db")

config = PlatformConfig()
