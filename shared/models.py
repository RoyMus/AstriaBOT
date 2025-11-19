"""
Shared configuration and models for microservices
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum


class UserState(str, Enum):
    NEW = "new"
    PICTURES_LOADED = "pictures_loaded"
    TUNE_READY = "tune_ready"
    WRITING_FEEDBACK = "writing_feedback"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    REPLY = "reply"
    LIST_REPLY = "list_reply"


class UserModel(BaseModel):
    phone: str
    state: UserState
    credits: str = "0"
    tune_id: Optional[str] = None
    chosen_pack: Optional[str] = None
    entity_type: Optional[str] = None
    language: str = "english"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MessageModel(BaseModel):
    message_id: str
    from_number: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: str
    status: str = "received"


class PackModel(BaseModel):
    id: int
    name: str
    slug: str
    price: float
    description: Optional[str] = None


class RatingModel(BaseModel):
    phone_number: str
    rating: int
    feedback: Optional[str] = None
    date: str
