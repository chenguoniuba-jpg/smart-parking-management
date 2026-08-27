from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import backend.database
from backend.ai_engine import AIManager
from backend.auth import get_current_active_admin
from backend.database import ParkingRecord, ParkingSpot, ParkingStatus, Reservation, User
from backend.schemas import (
    FlashSaleResponse,
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)


router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"],
    dependencies=[Depends(get_current_active_admin)],
)
ai_manager = AIManager()


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(backend.database.get_db),
):
    if reservation.start_time >= reservation.end_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    if not db.query(User).filter(User.id == reservation.user_id).first():
        raise HTTPException(status_code=404, detail="用户不存在")
    spot = db.query(ParkingSpot).filter(
        ParkingSpot.id == reservation.parking_spot_id
    ).first()
    if not spot:
        raise HTTPException(status_code=404, detail="车位不存在")
    if spot.status != ParkingStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="车位不可用")

    new_reservation = Reservation(**reservation.model_dump())
    spot.status = ParkingStatus.RESERVED
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(backend.database.get_db),
):
    return (
        db.query(Reservation)
        .order_by(Reservation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/user/{user_id}", response_model=List[ReservationResponse])
def get_user_reservations(
    user_id: int, db: Session = Depends(backend.database.get_db)
):
    return (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id)
        .order_by(Reservation.created_at.desc())
        .all()
    )


@router.get("/flash-sale/available")
def get_flash_sale_spots(db: Session = Depends(backend.database.get_db)):
    spot_ids = ai_manager.smart_scheduler.get_flash_sale_spots(db, count=5)
    spots = db.query(ParkingSpot).filter(ParkingSpot.id.in_(spot_ids)).all() if spot_ids else []
    by_id = {spot.id: spot for spot in spots}
    items = [
        {
            "spot_id": by_id[spot_id].id,
            "spot_number": by_id[spot_id].spot_number,
            "floor": by_id[spot_id].floor,
            "zone": by_id[spot_id].zone,
            "size": by_id[spot_id].size.value,
        }
        for spot_id in spot_ids
        if spot_id in by_id
    ]
    return {"available_spots": items, "count": len(items)}


@router.post("/flash-sale/{user_id}", response_model=FlashSaleResponse)
def participate_flash_sale(
    user_id: int, db: Session = Depends(backend.database.get_db)
):
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="用户不存在")
    spot_ids = ai_manager.smart_scheduler.get_flash_sale_spots(db, count=3)
    if not spot_ids:
        return FlashSaleResponse(success=False, message="当前没有限时预约车位")

    selected_spot_id = spot_ids[0]
    start_time = datetime.utcnow() + timedelta(minutes=30)
    new_reservation = Reservation(
        user_id=user_id,
        parking_spot_id=selected_spot_id,
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        status="confirmed",
        is_flash_sale=True,
    )
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == selected_spot_id).first()
    if spot:
        spot.status = ParkingStatus.RESERVED
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return FlashSaleResponse(
        success=True,
        message="限时预约成功",
        reservation_id=new_reservation.id,
    )


@router.post("/{reservation_id}/check-in")
def check_in_reservation(
    reservation_id: int, db: Session = Depends(backend.database.get_db)
):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    if reservation.status != "confirmed":
        raise HTTPException(status_code=400, detail="预约状态不正确")

    now = datetime.utcnow()
    if now < reservation.start_time - timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="还未到预约时间")
    if now > reservation.end_time:
        reservation.status = "expired"
        ai_manager.credit_system.update_credit(
            db, reservation.user_id, -15, "预约失约"
        )
        db.commit()
        raise HTTPException(status_code=400, detail="预约已过期")

    spot = db.query(ParkingSpot).filter(
        ParkingSpot.id == reservation.parking_spot_id
    ).first()
    if spot:
        spot.status = ParkingStatus.OCCUPIED
    new_record = ParkingRecord(
        user_id=reservation.user_id,
        parking_spot_id=reservation.parking_spot_id,
        entry_time=now,
        is_compliant=True,
    )
    reservation.status = "completed"
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"message": "签到成功", "record_id": new_record.id}


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int, db: Session = Depends(backend.database.get_db)
):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    return reservation


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    db: Session = Depends(backend.database.get_db),
):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")

    updates = reservation_update.model_dump(exclude_none=True)
    start_time = updates.get("start_time", reservation.start_time)
    end_time = updates.get("end_time", reservation.end_time)
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    for key, value in updates.items():
        setattr(reservation, key, value)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    reservation_id: int, db: Session = Depends(backend.database.get_db)
):
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    spot = db.query(ParkingSpot).filter(
        ParkingSpot.id == reservation.parking_spot_id
    ).first()
    if spot and spot.status == ParkingStatus.RESERVED:
        spot.status = ParkingStatus.AVAILABLE
    db.delete(reservation)
    db.commit()
    return None
