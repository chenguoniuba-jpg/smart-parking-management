from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import backend.database
from backend.database import TrafficPrediction, SystemConfig
from backend.schemas import TrafficPredictionResponse, SystemConfigCreate, SystemConfigResponse
from backend.ai_engine import AIManager
from backend.auth import get_current_active_admin

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
    dependencies=[Depends(get_current_active_admin)],
)
ai_manager = AIManager()

@router.get("/traffic-predictions", response_model=List[TrafficPredictionResponse])
def get_traffic_predictions(days_ahead: int = 7, db: Session = Depends(backend.database.get_db)):
    predictions = ai_manager.traffic_predictor.predict_peak_hours(db, days_ahead)
    
    for prediction in predictions:
        existing = db.query(TrafficPrediction).filter(
            TrafficPrediction.prediction_date == prediction.prediction_date
        ).first()
        
        if not existing:
            db.add(prediction)
    
    db.commit()
    
    all_predictions = db.query(TrafficPrediction).filter(
        TrafficPrediction.prediction_date >= datetime.utcnow().date()
    ).order_by(TrafficPrediction.prediction_date).all()
    
    return all_predictions

@router.post("/traffic-predictions/generate")
def generate_traffic_predictions(days_ahead: int = 7, db: Session = Depends(backend.database.get_db)):
    predictions = ai_manager.traffic_predictor.predict_peak_hours(db, days_ahead)
    
    for prediction in predictions:
        existing = db.query(TrafficPrediction).filter(
            TrafficPrediction.prediction_date == prediction.prediction_date
        ).first()
        
        if existing:
            existing.predicted_peak_hour = prediction.predicted_peak_hour
            existing.predicted_volume = prediction.predicted_volume
            existing.confidence = prediction.confidence
        else:
            db.add(prediction)
    
    db.commit()
    
    return {
        "message": "流量预测生成成功",
        "predictions_count": len(predictions)
    }

@router.get("/long-term-violations")
def get_long_term_violations(db: Session = Depends(backend.database.get_db)):
    violations = ai_manager.long_term_monitor.check_long_term_parking(db)
    recommendations = ai_manager.long_term_monitor.generate_recommendations(violations)
    
    return {
        "violations": violations,
        "recommendations": recommendations,
        "threshold_days": ai_manager.long_term_monitor.threshold_days
    }

@router.post("/check-capacity-expansion")
def check_capacity_expansion(db: Session = Depends(backend.database.get_db)):
    should_expand = ai_manager.smart_scheduler.check_capacity_expansion(db)
    
    return {
        "should_expand": should_expand,
        "message": "建议启动扩容策略" if should_expand else "当前容量充足",
        "timestamp": datetime.utcnow()
    }

@router.post("/manual-expand")
def manual_capacity_expansion(db: Session = Depends(backend.database.get_db)):
    from backend.database import ParkingSpot, VehicleSize, ParkingStatus
    
    new_spots = []
    for i in range(1, 6):
        spot_number = f"EXP-{datetime.utcnow().strftime('%Y%m%d')}-{i:03d}"
        new_spot = ParkingSpot(
            spot_number=spot_number,
            floor=1,
            zone="EXP",
            size=VehicleSize.MEDIUM,
            status=ParkingStatus.AVAILABLE
        )
        db.add(new_spot)
        new_spots.append(new_spot)
    
    db.commit()
    
    return {
        "message": "手动扩容成功",
        "new_spots_count": len(new_spots),
        "new_spots": [spot.spot_number for spot in new_spots]
    }

@router.get("/configs", response_model=List[SystemConfigResponse])
def get_system_configs(db: Session = Depends(backend.database.get_db)):
    configs = db.query(SystemConfig).all()
    return configs

@router.post("/configs", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
def create_system_config(config: SystemConfigCreate, db: Session = Depends(backend.database.get_db)):
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == config.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="配置键已存在")
    
    new_config = SystemConfig(**config.model_dump())
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return new_config

@router.put("/configs/{config_key}", response_model=SystemConfigResponse)
def update_system_config(config_key: str, config_value: str, db: Session = Depends(backend.database.get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config.config_value = config_value
    config.updated_at = datetime.utcnow()
    
    if config_key == "long_term_threshold":
        ai_manager.long_term_monitor.threshold_days = int(config_value)
    
    db.commit()
    db.refresh(config)
    
    return config

@router.get("/configs/{config_key}", response_model=SystemConfigResponse)
def get_system_config(config_key: str, db: Session = Depends(backend.database.get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config

@router.delete("/configs/{config_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_config(config_key: str, db: Session = Depends(backend.database.get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    db.delete(config)
    db.commit()
    return None

@router.post("/init-default-configs")
def init_default_configs(db: Session = Depends(backend.database.get_db)):
    default_configs = [
        {"config_key": "long_term_threshold", "config_value": "20", "description": "长时停车阈值天数"},
        {"config_key": "compliance_bonus", "config_value": "10", "description": "履约奖励积分"},
        {"config_key": "violation_penalty", "config_value": "-20", "description": "违规扣分"},
        {"config_key": "no_show_penalty", "config_value": "-15", "description": "预约失约扣分"},
        {"config_key": "flash_sale_duration", "config_value": "30", "description": "秒杀预约时长（分钟）"},
        {"config_key": "expansion_threshold", "config_value": "0.85", "description": "扩容阈值（占用率）"},
    ]
    
    created_count = 0
    for config_data in default_configs:
        existing = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_data["config_key"]
        ).first()
        
        if not existing:
            new_config = SystemConfig(**config_data)
            db.add(new_config)
            created_count += 1
    
    db.commit()
    
    return {
        "message": "默认配置初始化完成",
        "created_count": created_count
    }
