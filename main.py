from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt

from database import engine, get_db, Base
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NurAuto API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "nurauto-2025-astana"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=24)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(models.User).filter(models.User.id == payload.get("user_id")).first()
        if not user:
            raise HTTPException(status_code=401, detail="Пайдаланушы табылмады")
        return user
    except:
        raise HTTPException(status_code=401, detail="Токен қате")

# ── AUTH ──────────────────────────────────────────
@app.post("/auth/register", tags=["Auth"])
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Бұл email тіркелген")
    user = models.User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token({"user_id": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.post("/auth/login", tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email немесе пароль қате")
    token = create_token({"user_id": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email}}

@app.get("/auth/me", tags=["Auth"])
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ── CARS ──────────────────────────────────────────
@app.get("/cars", tags=["Cars"])
def get_cars(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Car)
    if status:
        q = q.filter(models.Car.status == status)
    return q.all()

@app.get("/cars/{car_id}", tags=["Cars"])
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина табылмады")
    return car

# ── ORDERS ────────────────────────────────────────
@app.post("/orders", tags=["Orders"])
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = models.Order(
        user_id=current_user.id,
        car_id=data.car_id,
        order_type=data.order_type,
        message=data.message,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@app.get("/orders/my", tags=["Orders"])
def my_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

# ── TRANSIT ───────────────────────────────────────
@app.get("/transit", tags=["Transit"])
def get_transit(db: Session = Depends(get_db)):
    return db.query(models.Transit).filter(models.Transit.is_active == True).all()

# ── SEED — тест деректер ──────────────────────────
@app.get("/seed", tags=["Dev"])
def seed(db: Session = Depends(get_db)):
    if db.query(models.Car).count() > 0:
        return {"message": "Деректер бұрыннан бар"}
    
    cars = [
        models.Car(brand="Mercedes-Benz", model="G 63 AMG", year=2024, price=139900000,
                   engine="4.0L V8 Biturbo", power=585, drive="AWD",
                   acceleration=4.5, max_speed=220, color="Obsidian Black",
                   status="available",
                   image_url="https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=600"),
        models.Car(brand="Porsche", model="911 Turbo S", year=2024, price=124500000,
                   engine="3.7L Flat-6", power=650, drive="AWD",
                   acceleration=2.7, max_speed=330, color="GT Silver",
                   status="available",
                   image_url="https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=600"),
        models.Car(brand="Toyota", model="Land Cruiser 300", year=2024, price=62000000,
                   engine="3.5L V6 TT", power=415, drive="4WD",
                   acceleration=6.7, max_speed=210, color="Pearl White",
                   status="available",
                   image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600"),
        models.Car(brand="Rolls-Royce", model="Ghost", year=2025, price=320000000,
                   engine="6.75L V12", power=563, drive="AWD",
                   acceleration=4.8, max_speed=250, color="Кастом",
                   status="preorder", deposit_amount=30000000, delivery_days=90,
                   image_url="https://images.unsplash.com/photo-1631295387526-d4eae6bc6f49?w=600"),
        models.Car(brand="Lamborghini", model="Urus SE", year=2025, price=270000000,
                   engine="4.0L V8 Hybrid", power=800, drive="AWD",
                   acceleration=3.4, max_speed=305, color="Кастом",
                   status="preorder", deposit_amount=25000000, delivery_days=120,
                   image_url="https://images.unsplash.com/photo-1621135802920-133df287f89c?w=600"),
    ]
    
    admin = models.User(
        name="Adilkhanov Arnur Muratuly",
        email="admin@nurauto.kz",
        phone="+87027436964",
        password_hash=hash_password("Admin2025!"),
        role="admin"
    )
    
    transits = [
        models.Transit(car_name="Mercedes-Benz S-Class W223", route="Германия → Астана", transport="🚢 Теңіз", progress=75, days_left=4),
        models.Transit(car_name="Toyota LC300 — 5 дана", route="Жапония → Астана", transport="🚛 Жер жолы", progress=94, days_left=1),
        models.Transit(car_name="Porsche Cayenne Turbo GT", route="Германия → Астана", transport="🚛 Жер жолы", progress=45, days_left=8),
    ]
    
    db.add_all(cars + [admin] + transits)
    db.commit()
    return {"message": "✅ Деректер қосылды!", "cars": len(cars)}

@app.get("/", tags=["Root"])
def root():
    return {"app": "NurAuto API", "status": "🟢 Жұмыс жасап тур", "docs": "/docs"}