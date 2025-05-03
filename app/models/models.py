from sqlalchemy import Column, Integer, String, JSON, DateTime
from .database import Base
import datetime

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_message = Column(String)
    detected_intent = Column(String)
    entities = Column(JSON)
    system_response = Column(String)
    operation_executed = Column(String, nullable=True)
    operation_result = Column(JSON, nullable=True)
