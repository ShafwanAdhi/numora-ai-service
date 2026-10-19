import os
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Settings:
    enabled: bool = False
    token: str = ""
    database_url: str = ""
    principal_id: str = ""
    lease_seconds: int = 60
    heartbeat_seconds: float = 15
    execution_seconds: float = 30

    @classmethod
    def from_env(cls):
        return cls(enabled=os.environ.get("NUMORA_GENERATOR_ENABLED", "false").lower() == "true",
                   token=os.environ.get("NUMORA_GENERATOR_TOKEN", ""),
                   database_url=os.environ.get("COMPUTE_DATABASE_URL", ""),
                   principal_id=os.environ.get("COMPUTE_SERVICE_PRINCIPAL_ID", ""))

    def valid(self):
        try:
            if UUID(self.principal_id).int == 0:
                return False
        except (ValueError, AttributeError):
            return False
        return (len(self.token) >= 32 and bool(self.database_url) and bool(self.principal_id) and
                0 < self.heartbeat_seconds < self.execution_seconds < self.lease_seconds)
