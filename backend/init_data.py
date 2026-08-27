"""Initialize a local demo database with clearly labeled demonstration data."""

from __future__ import annotations

import os
import secrets
from typing import Optional

from backend.database import (
    Admin,
    ParkingSpot,
    ParkingStatus,
    SessionLocal,
    SystemConfig,
    User,
    VehicleSize,
    init_db,
)


DEMO_USERS = [
    {
        "username": "演示用户01",
        "phone": "13000000001",
        "license_plate": "DEMO-001",
        "member_level": 3,
        "credit_score": 95,
        "points": 500,
        "vehicle_size": VehicleSize.MEDIUM,
        "is_special_needs": False,
    },
    {
        "username": "演示用户02",
        "phone": "13000000002",
        "license_plate": "DEMO-002",
        "member_level": 2,
        "credit_score": 88,
        "points": 300,
        "vehicle_size": VehicleSize.SMALL,
        "is_special_needs": False,
    },
    {
        "username": "演示用户03",
        "phone": "13000000003",
        "license_plate": "DEMO-003",
        "member_level": 1,
        "credit_score": 75,
        "points": 150,
        "vehicle_size": VehicleSize.LARGE,
        "is_special_needs": True,
    },
]

# 286 spaces: example identifiers matching the confirmed on-site capacity, not live spot records.
DEMO_LAYOUT = [
    (1, "A", 48),
    (1, "B", 48),
    (1, "VIP", 10),
    (2, "C", 60),
    (2, "D", 60),
    (3, "E", 50),
    (3, "EV", 10),
]

DEFAULT_CONFIGS = [
    {"config_key": "long_term_threshold", "config_value": "20", "description": "长时停车阈值天数"},
    {"config_key": "compliance_bonus", "config_value": "10", "description": "履约奖励积分"},
    {"config_key": "violation_penalty", "config_value": "-20", "description": "违规扣分"},
    {"config_key": "no_show_penalty", "config_value": "-15", "description": "预约失约扣分"},
    {"config_key": "flash_sale_duration", "config_value": "30", "description": "限时预约时长（分钟）"},
    {"config_key": "expansion_threshold", "config_value": "0.85", "description": "扩容提示阈值（占用率）"},
]


def init_sample_data() -> None:
    init_db()
    db = SessionLocal()
    generated_password: Optional[str] = None

    try:
        username = os.getenv("ADMIN_USERNAME", "admin").strip() or "admin"
        email = os.getenv("ADMIN_EMAIL", "admin@example.invalid").strip()
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin:
            password = os.getenv("ADMIN_PASSWORD", "")
            if not password:
                password = secrets.token_urlsafe(16)
                generated_password = password
            admin = Admin(
                username=username,
                email=email,
                is_superuser=True,
            )
            admin.set_password(password)
            db.add(admin)

        for user_data in DEMO_USERS:
            exists = db.query(User).filter(
                User.license_plate == user_data["license_plate"]
            ).first()
            if not exists:
                db.add(User(**user_data))

        sizes = [VehicleSize.SMALL, VehicleSize.MEDIUM, VehicleSize.LARGE]
        for floor, zone, count in DEMO_LAYOUT:
            for index in range(1, count + 1):
                spot_number = f"{floor}-{zone}-{index:03d}"
                exists = db.query(ParkingSpot).filter(
                    ParkingSpot.spot_number == spot_number
                ).first()
                if not exists:
                    db.add(
                        ParkingSpot(
                            spot_number=spot_number,
                            floor=floor,
                            zone=zone,
                            size=sizes[(index + floor) % len(sizes)],
                            is_special_needs=index % 30 == 0,
                            status=ParkingStatus.AVAILABLE,
                        )
                    )

        for config_data in DEFAULT_CONFIGS:
            exists = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_data["config_key"]
            ).first()
            if not exists:
                db.add(SystemConfig(**config_data))

        db.commit()

        print("Demo database initialized.")
        print(f"Admin username: {username}")
        if generated_password:
            print(f"Generated one-time admin password: {generated_password}")
            print("Save it temporarily and change it after the first login.")
        else:
            print("Admin password was read from ADMIN_PASSWORD.")
        print(f"Demo users: {db.query(User).count()}")
        print(f"Demo parking spaces: {db.query(ParkingSpot).count()}")
        print("All seeded records are public example data, separate from Shanghai live operational data.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()
