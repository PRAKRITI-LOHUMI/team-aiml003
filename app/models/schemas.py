from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime

class UserInteractionBase(BaseModel):
    user_message: str
    detected_intent: str
    entities: Dict[str, Any]
    system_response: str
    operation_executed: Optional[str] = None
    operation_result: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True
