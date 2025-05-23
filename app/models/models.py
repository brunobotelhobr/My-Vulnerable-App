from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database.database import Base


class User(Base):
    """User model for authentication and profile information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Product(Base):
    """Product model for the store inventory."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String)


class Comment(Base):
    """Comment model for product reviews and feedback."""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))


class Cart(Base):
    """Shopping cart model for user items."""
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)


class UserAddress(Base):
    """User address model for shipping information."""
    __tablename__ = "user_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    is_default = Column(Integer, default=0) 