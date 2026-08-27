import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum
from backend.security import hash_password, verify_password

# 数据库文件放在项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'ai_parking.db')}",
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class VehicleSize(enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class ParkingStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    MAINTENANCE = "MAINTENANCE"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    member_level = Column(Integer, default=1)
    credit_score = Column(Integer, default=100)
    points = Column(Integer, default=0)
    vehicle_size = Column(Enum(VehicleSize), default=VehicleSize.MEDIUM)
    is_special_needs = Column(Boolean, default=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    monthly_parking_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    parking_records = relationship("ParkingRecord", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    credit_records = relationship("CreditRecord", back_populates="user")
    point_records = relationship("PointRecord", back_populates="user")

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
    
    def set_password(self, password: str):
        self.hashed_password = hash_password(password)

class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String(20), unique=True, index=True, nullable=False)
    floor = Column(Integer, default=1)
    zone = Column(String(20), default="A")
    size = Column(Enum(VehicleSize), default=VehicleSize.MEDIUM)
    status = Column(Enum(ParkingStatus), default=ParkingStatus.AVAILABLE)
    is_special_needs = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    parking_records = relationship("ParkingRecord", back_populates="parking_spot")
    reservations = relationship("Reservation", back_populates="parking_spot")

class ParkingRecord(Base):
    __tablename__ = "parking_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    fee = Column(Float, default=0.0)
    is_compliant = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="parking_records")
    parking_spot = relationship("ParkingSpot", back_populates="parking_records")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")
    is_flash_sale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reservations")
    parking_spot = relationship("ParkingSpot", back_populates="reservations")

class CreditRecord(Base):
    __tablename__ = "credit_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="credit_records")

class PointRecord(Base):
    __tablename__ = "point_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="point_records")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(50), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrafficPrediction(Base):
    __tablename__ = "traffic_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(DateTime, nullable=False)
    predicted_peak_hour = Column(Integer, nullable=False)
    predicted_volume = Column(Integer, nullable=False)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
