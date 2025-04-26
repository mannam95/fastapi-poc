from sqlalchemy import Column, String, Text
from app.models.base import BaseModel


class Process(BaseModel):
    """Process model"""
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)