from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class VehicleSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class ParkingStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    MAINTENANCE = "MAINTENANCE"

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    is_superuser: bool = False

class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
class AdminLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)

class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    admin_id: Optional[int] = None

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)
    license_plate: str = Field(..., min_length=5, max_length=20)
    vehicle_size: VehicleSize = VehicleSize.MEDIUM
    is_special_needs: bool = False

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=50)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    license_plate: Optional[str] = Field(default=None, min_length=5, max_length=20)
    vehicle_size: Optional[VehicleSize] = None
    is_special_needs: Optional[bool] = None
    status: Optional[UserStatus] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    phone: str
    license_plate: str
    member_level: int
    credit_score: int
    points: int
    vehicle_size: VehicleSize
    is_special_needs: bool
    status: UserStatus
    monthly_parking_days: int
    created_at: datetime
    
class ParkingSpotCreate(BaseModel):
    spot_number: str = Field(..., min_length=1, max_length=20)
    floor: int = Field(default=1, ge=1, le=10)
    zone: str = Field(default="A", min_length=1, max_length=10)
    size: VehicleSize = VehicleSize.MEDIUM
    is_special_needs: bool = False

class ParkingSpotUpdate(BaseModel):
    floor: Optional[int] = Field(default=None, ge=1, le=10)
    zone: Optional[str] = Field(default=None, min_length=1, max_length=10)
    size: Optional[VehicleSize] = None
    status: Optional[ParkingStatus] = None
    is_special_needs: Optional[bool] = None

class ParkingSpotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spot_number: str
    floor: int
    zone: str
    size: VehicleSize
    status: ParkingStatus
    is_special_needs: bool
    created_at: datetime
    
class ParkingRecordCreate(BaseModel):
    user_id: int
    parking_spot_id: int

class ParkingRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    parking_spot_id: int
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    fee: float
    is_compliant: bool
    created_at: datetime
    
class ReservationCreate(BaseModel):
    user_id: int
    parking_spot_id: int
    start_time: datetime
    end_time: datetime
    is_flash_sale: bool = False

class ReservationUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=20)

class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    parking_spot_id: int
    start_time: datetime
    end_time: datetime
    status: str
    is_flash_sale: bool
    created_at: datetime
    
class CreditRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    change_amount: int
    reason: str
    created_at: datetime
    
class PointRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    change_amount: int
    reason: str
    created_at: datetime
    
class SystemConfigCreate(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=50)
    config_value: str
    description: Optional[str] = None

class SystemConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    config_key: str
    config_value: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
class TrafficPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prediction_date: datetime
    predicted_peak_hour: int
    predicted_volume: int
    confidence: float
    created_at: datetime
    
class ParkingRecommendation(BaseModel):
    recommended_spots: List[int]
    nearby_parking_lots: List[str]
    subsidy_amount: float

class FlashSaleResponse(BaseModel):
    success: bool
    message: str
    reservation_id: Optional[int] = None

class DashboardStats(BaseModel):
    total_spots: int
    available_spots: int
    occupied_spots: int
    reserved_spots: int
    total_users: int
    active_users: int
    today_entries: int
    today_exits: int
    compliance_rate: float
    average_credit_score: float
