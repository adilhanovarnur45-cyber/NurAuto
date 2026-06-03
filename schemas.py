from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name:     str
    email:    EmailStr
    phone:    Optional[str] = None
    password: str

class UserOut(BaseModel):
    id:         int
    name:       str
    email:      str
    phone:      Optional[str]
    role:       str
    created_at: datetime
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    user:         UserOut

class CarCreate(BaseModel):
    brand:         str
    model:         str
    year:          int
    price:         float
    engine:        Optional[str] = None
    power:         Optional[int] = None
    drive:         Optional[str] = None
    acceleration:  Optional[float] = None
    max_speed:     Optional[int] = None
    color:         Optional[str] = None
    image_url:     Optional[str] = None
    status:        str = "available"
    deposit_amount: Optional[float] = None
    delivery_days:  Optional[int] = None

class CarOut(CarCreate):
    id:         int
    created_at: datetime
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    car_id:     int
    order_type: str
    message:    Optional[str] = None

class OrderOut(BaseModel):
    id:         int
    user_id:    int
    car_id:     int
    order_type: str
    status:     str
    message:    Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class TransitCreate(BaseModel):
    car_name:  str
    route:     str
    transport: Optional[str] = None
    progress:  int = 0
    days_left: int = 0