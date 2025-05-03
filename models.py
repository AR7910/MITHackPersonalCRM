from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    source_document: str
    event: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    follow_up_status: Optional[str] = "Not Started"  # Not Started, In Progress, Done
    last_contacted: Optional[str] = None
    connection_status: Optional[str] = None  # Not Connected, Requested, Connected
    date_added: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Add the to_dict method that's missing
    def to_dict(self):
        return self.model_dump()  # For pydantic v2
        # If using older pydantic version, use: return self.dict()
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
