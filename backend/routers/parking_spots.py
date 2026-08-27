from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import backend.database
from backend.ai_engine import AIManager
from backend.auth import get_current_active_admin
from backend.database import ParkingSpot, ParkingStatus, User
from backend.schemas import ParkingSpotCreate, ParkingSpotResponse, ParkingSpotUpdate


router = APIRouter(
    prefix="/api/parking-spots",
    tags=["parking-spots"],
    dependencies=[Depends(get_current_active_admin)],
)
ai_manager = AIManager()


@router.post("/", response_model=ParkingSpotResponse, status_code=status.HTTP_201_CREATED)
def create_parking_spot(
    spot: ParkingSpotCreate, db: Session = Depends(backend.database.get_db)
):
    if db.query(ParkingSpot).filter(ParkingSpot.spot_number == spot.spot_number).first():
        raise HTTPException(status_code=400, detail="车位号已存在")

    new_spot = ParkingSpot(**spot.model_dump())
    db.add(new_spot)
    db.commit()
    db.refresh(new_spot)
    return new_spot


@router.get("/", response_model=List[ParkingSpotResponse])
def get_parking_spots(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ParkingStatus] = None,
    db: Session = Depends(backend.database.get_db),
):
    query = db.query(ParkingSpot)
    if status_filter:
        query = query.filter(ParkingSpot.status == status_filter)
    return query.offset(skip).limit(limit).all()


# Static routes are declared before /{spot_id} so FastAPI does not interpret
# "stats" or "smart-assign" as an integer identifier.
@router.get("/stats/summary")
def get_parking_stats(db: Session = Depends(backend.database.get_db)):
    total_spots = db.query(ParkingSpot).count()
    available_spots = db.query(ParkingSpot).filter(
        ParkingSpot.status == ParkingStatus.AVAILABLE
    ).count()
    occupied_spots = db.query(ParkingSpot).filter(
        ParkingSpot.status == ParkingStatus.OCCUPIED
    ).count()
    reserved_spots = db.query(ParkingSpot).filter(
        ParkingSpot.status == ParkingStatus.RESERVED
    ).count()
    return {
        "total_spots": total_spots,
        "available_spots": available_spots,
        "occupied_spots": occupied_spots,
        "reserved_spots": reserved_spots,
        "occupancy_rate": occupied_spots / total_spots if total_spots else 0,
    }


@router.post("/smart-assign/{user_id}")
def smart_assign_spot(
    user_id: int, db: Session = Depends(backend.database.get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    assigned_spot_id = ai_manager.smart_scheduler.assign_parking_spot(db, user)
    if not assigned_spot_id:
        raise HTTPException(status_code=400, detail="没有可用车位")
    return {"message": "规则分配成功", "spot_id": assigned_spot_id}


@router.post("/check-expansion")
def check_capacity_expansion(db: Session = Depends(backend.database.get_db)):
    should_expand = ai_manager.smart_scheduler.check_capacity_expansion(db)
    return {
        "should_expand": should_expand,
        "message": "建议评估扩容" if should_expand else "当前容量充足",
    }


@router.get("/{spot_id}", response_model=ParkingSpotResponse)
def get_parking_spot(spot_id: int, db: Session = Depends(backend.database.get_db)):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")
    return spot


@router.put("/{spot_id}", response_model=ParkingSpotResponse)
def update_parking_spot(
    spot_id: int,
    spot_update: ParkingSpotUpdate,
    db: Session = Depends(backend.database.get_db),
):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")

    for key, value in spot_update.model_dump(exclude_none=True).items():
        setattr(spot, key, value)
    db.commit()
    db.refresh(spot)
    return spot


@router.post("/{spot_id}/assign")
def assign_spot(
    spot_id: int,
    user_id: int,
    db: Session = Depends(backend.database.get_db),
):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")
    if spot.status != ParkingStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="车位不可用")
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="用户不存在")

    spot.status = ParkingStatus.OCCUPIED
    db.commit()
    return {"message": "指定车位分配成功", "spot_id": spot.id}


@router.delete("/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_spot(
    spot_id: int, db: Session = Depends(backend.database.get_db)
):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")
    db.delete(spot)
    db.commit()
    return None
