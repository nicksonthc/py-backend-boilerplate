from typing import Dict, Any
from pydantic import BaseModel, Field


class CreateSetting(BaseModel):
    key: str = Field(..., description="Setting key")
    value: Dict[str, Any] = Field(..., description="Setting value as JSON")
    description: str | None = Field(None, description="Optional description of the setting")


class UpdateSetting(BaseModel):
    value: Dict[str, Any] | None = Field(None, description="Updated setting value as JSON")
    description: str | None = Field(None, description="Optional updated description of the setting")
