from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    phone         = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), default="user")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    orders        = relationship("Order", back_populates="user")

class Car(Base):
    __tablename__ = "cars"
    id           = Column(Integer, primary_key=True, index=True)
    brand        = Column(String(100), nullable=False)
    model        = Column(String(100), nullable=False)
    year         = Column(Integer, nullable=False)
    price        = Column(Float, nullable=False)
    engine       = Column(String(100))
    power        = Column(Integer)
    drive        = Column(String(50))
    acceleration = Column(Float)
    max_speed    = Column(Integer)
    color        = Column(String(100))
    image_url    = Column(String(500))
    status       = Column(String(50), default="available")
    deposit_amount  = Column(Float, nullable=True)
    delivery_days   = Column(Integer, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    orders       = relationship("Order", back_populates="car")

class Order(Base):
    __tablename__ = "orders"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id     = Column(Integer, ForeignKey("cars.id"), nullable=False)
    order_type = Column(String(50), nullable=False)
    status     = Column(String(50), default="pending")
    message    = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User", back_populates="orders")
    car        = relationship("Car", back_populates="orders")

class Transit(Base):
    __tablename__ = "transit"
    id        = Column(Integer, primary_key=True, index=True)
    car_name  = Column(String(200), nullable=False)
    route     = Column(String(300), nullable=False)
    transport = Column(String(100))
    progress  = Column(Integer, default=0)
    days_left = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)