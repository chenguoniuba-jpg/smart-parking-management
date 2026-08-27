from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import backend.database
from backend.ai_engine import AIManager
from backend.auth import get_current_active_admin
from backend.database import ParkingRecord, ParkingSpot, ParkingStatus, User
from backend.schemas import ParkingRecordCreate, ParkingRecordResponse


router = APIRouter(
    prefix="/api/parking-records",
    tags=["parking-records"],
    dependencies=[Depends(get_current_active_admin)],
)
ai_manager = AIManager()


@router.post("/", response_model=ParkingRecordResponse, status_code=status.HTTP_201_CREATED)
def create_parking_record(
    record: ParkingRecordCreate, db: Session = Depends(backend.database.get_db)
):
    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == record.parking_spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")
    if spot.status != ParkingStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="车位不可用")

    spot.status = ParkingStatus.OCCUPIED
    user.monthly_parking_days += 1
    new_record = ParkingRecord(
        user_id=record.user_id,
        parking_spot_id=record.parking_spot_id,
        entry_time=datetime.utcnow(),
        is_compliant=True,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=List[ParkingRecordResponse])
def get_parking_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(backend.database.get_db),
):
    return (
        db.query(ParkingRecord)
        .order_by(ParkingRecord.entry_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/active", response_model=List[ParkingRecordResponse])
def get_active_records(db: Session = Depends(backend.database.get_db)):
    return db.query(ParkingRecord).filter(ParkingRecord.exit_time.is_(None)).all()


@router.get("/license-plate/{license_plate}")
def find_vehicle_by_license_plate(
    license_plate: str, db: Session = Depends(backend.database.get_db)
):
    user = db.query(User).filter(User.license_plate == license_plate).first()
    if not user:
        raise HTTPException(status_code=404, detail="未找到该车牌号的用户")

    active_record = db.query(ParkingRecord).filter(
        ParkingRecord.user_id == user.id,
        ParkingRecord.exit_time.is_(None),
    ).first()
    if not active_record:
        return {
            "user_id": user.id,
            "license_plate": license_plate,
            "status": "not_parked",
            "message": "车辆当前未在停车场",
        }

    spot = db.query(ParkingSpot).filter(
        ParkingSpot.id == active_record.parking_spot_id
    ).first()
    return {
        "user_id": user.id,
        "license_plate": license_plate,
        "status": "parked",
        "spot_id": active_record.parking_spot_id,
        "spot_number": spot.spot_number if spot else None,
        "floor": spot.floor if spot else None,
        "zone": spot.zone if spot else None,
        "entry_time": active_record.entry_time,
        "duration_hours": round(
            (datetime.utcnow() - active_record.entry_time).total_seconds() / 3600,
            2,
        ),
    }


@router.get("/stats/compliance")
def get_compliance_stats(db: Session = Depends(backend.database.get_db)):
    total_records = db.query(ParkingRecord).count()
    compliant_records = db.query(ParkingRecord).filter(
        ParkingRecord.is_compliant.is_(True)
    ).count()
    rate = compliant_records / total_records if total_records else 0
    return {
        "total_records": total_records,
        "compliant_records": compliant_records,
        "non_compliant_records": total_records - compliant_records,
        "compliance_rate": round(rate * 100, 2),
    }


@router.get("/{record_id}", response_model=ParkingRecordResponse)
def get_parking_record(
    record_id: int, db: Session = Depends(backend.database.get_db)
):
    record = db.query(ParkingRecord).filter(ParkingRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="停车记录不存在")
    return record


@router.post("/{record_id}/exit")
def exit_parking(record_id: int, db: Session = Depends(backend.database.get_db)):
    record = db.query(ParkingRecord).filter(ParkingRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="停车记录不存在")
    if record.exit_time:
        raise HTTPException(status_code=400, detail="车辆已离场")

    record.exit_time = datetime.utcnow()
    duration = (record.exit_time - record.entry_time).total_seconds() / 3600
    record.duration_hours = round(duration, 2)
    record.fee = round(duration * 5, 2)

    spot = db.query(ParkingSpot).filter(
        ParkingSpot.id == record.parking_spot_id
    ).first()
    if spot:
        spot.status = ParkingStatus.AVAILABLE
    if record.is_compliant:
        ai_manager.credit_system.update_credit(db, record.user_id, 10, "按时履约停车")
        ai_manager.credit_system.update_points(db, record.user_id, 5, "按时履约停车")

    db.commit()
    db.refresh(record)
    return {
        "message": "离场成功",
        "duration_hours": record.duration_hours,
        "fee": record.fee,
    }
