from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import backend.database
from backend.database import User, ParkingSpot, CreditRecord, PointRecord, ParkingStatus
from backend.schemas import (
    UserCreate, UserResponse, UserUpdate, CreditRecordResponse,
    PointRecordResponse, ParkingRecommendation
)
from backend.ai_engine import AIManager
from backend.auth import get_current_active_admin

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_admin)],
)
ai_manager = AIManager()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(backend.database.get_db)):
    db_user = db.query(User).filter(User.license_plate == user.license_plate).first()
    if db_user:
        raise HTTPException(status_code=400, detail="车牌号已存在")
    
    db_user = db.query(User).filter(User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="手机号已存在")
    
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(backend.database.get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(backend.database.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(backend.database.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    for key, value in user_update.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(backend.database.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return None

@router.get("/{user_id}/credit-records", response_model=List[CreditRecordResponse])
def get_user_credit_records(user_id: int, db: Session = Depends(backend.database.get_db)):
    records = db.query(CreditRecord).filter(CreditRecord.user_id == user_id).all()
    return records

@router.get("/{user_id}/point-records", response_model=List[PointRecordResponse])
def get_user_point_records(user_id: int, db: Session = Depends(backend.database.get_db)):
    records = db.query(PointRecord).filter(PointRecord.user_id == user_id).all()
    return records

@router.post("/{user_id}/redeem-points")
def redeem_points(user_id: int, points: int, reward_type: str, db: Session = Depends(backend.database.get_db)):
    success = ai_manager.credit_system.redeem_points(db, user_id, points, reward_type)
    if not success:
        raise HTTPException(status_code=400, detail="积分不足或用户不存在")
    return {"message": "兑换成功", "points_redeemed": points}

@router.get("/{user_id}/recommendations", response_model=ParkingRecommendation)
def get_parking_recommendations(user_id: int, db: Session = Depends(backend.database.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    violations = ai_manager.long_term_monitor.check_long_term_parking(db)
    user_violations = [v for v in violations if v["user_id"] == user_id]
    
    if user_violations:
        recommendations = ai_manager.long_term_monitor.generate_recommendations(user_violations)
        if recommendations:
            return recommendations[0]
    
    available_spots = db.query(ParkingSpot).filter(
        ParkingSpot.status == ParkingStatus.AVAILABLE
    ).limit(5).all()
    
    return ParkingRecommendation(
        recommended_spots=[spot.id for spot in available_spots],
        nearby_parking_lots=["合作停车场A", "合作停车场B"],
        subsidy_amount=0.0
    )
