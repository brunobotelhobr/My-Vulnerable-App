from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token schema for authentication responses."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema for decoded JWT payload."""
    username: Optional[str] = None


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str


class UserCreate(UserBase):
    """User creation schema with password field."""
    password: str


class CommentCreate(BaseModel):
    """Comment creation schema."""
    content: str


class CommentResponse(BaseModel):
    """Comment response schema with full details."""
    id: int
    name: str
    content: str
    created_at: datetime
    product_id: int

    class Config:
        from_attributes = True


class Address(BaseModel):
    """Address schema for user shipping information."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class CartItem(BaseModel):
    """Cart item schema for shopping cart operations."""
    product_id: int
    quantity: int


class PasswordChange(BaseModel):
    """Password change schema for user password updates."""
    current_password: str
    new_password: str 