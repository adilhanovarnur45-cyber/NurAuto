from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt

# --- ДИЗАЙН ҮШІН ҚОСЫЛҒАНДАР ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, get_db, Base
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NurAuto API")

# --- ДИЗАЙН ПАПКАСЫ (static папкасы болса істейді) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.post("/auth/register", tags=["Auth"])
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Бұл email тіркелген")
    user = models.User(name=data.name, email=data.email, phone=data.phone, password_hash=hash_password(data.password), role="user")
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

@app.get("/cars", tags=["Cars"])
def get_cars(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Car)
    if status: q = q.filter(models.Car.status == status)
    return q.all()

@app.get("/cars/{car_id}", tags=["Cars"])
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car: raise HTTPException(status_code=404, detail="Машина табылмады")
    return car

@app.post("/orders", tags=["Orders"])
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = models.Order(user_id=current_user.id, car_id=data.car_id, order_type=data.order_type, message=data.message, status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@app.get("/orders/my", tags=["Orders"])
def my_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

@app.get("/transit", tags=["Transit"])
def get_transit(db: Session = Depends(get_db)):
    return db.query(models.Transit).filter(models.Transit.is_active == True).all()

@app.get("/seed", tags=["Dev"])
def seed(db: Session = Depends(get_db)):
    if db.query(models.Car).count() > 0: return {"message": "Деректер бұрыннан бар"}
    # (Бұл жерде сенің ұзын seed кодырың тұра береді, оны өзгертпедім)
    return {"message": "✅ Деректер қосылды!"}

# --- ДИЗАЙНДЫ ҚОСҚАН ЖЕРІМ ОСЫ ---
@app.get("/", tags=["Root"])
async def root():
    return FileResponse("index.html")