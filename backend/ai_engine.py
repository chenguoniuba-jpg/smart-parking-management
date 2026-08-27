from datetime import datetime, time, timedelta
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
from backend.database import (
    CreditRecord,
    ParkingRecord,
    ParkingSpot,
    ParkingStatus,
    PointRecord,
    TrafficPrediction,
    User,
    VehicleSize,
)

class TrafficPredictor:
    """Deterministic historical baseline, not a trained machine-learning model."""

    def __init__(self):
        self.historical_data = []
    
    def predict_peak_hours(self, db: Session, days_ahead: int = 7) -> List[TrafficPrediction]:
        predictions = []
        
        records = db.query(ParkingRecord).all()
        if not records:
            return self._generate_default_predictions(days_ahead)
        
        hourly_counts, observed_days = self._analyze_hourly_patterns(records)
        sample_coverage = min(0.90, len(records) / 100)
        
        for day in range(days_ahead):
            prediction_date = datetime.combine(
                (datetime.utcnow() + timedelta(days=day)).date(), time.min
            )
            peak_hour = self._find_peak_hour(hourly_counts, prediction_date)
            predicted_volume = self._estimate_volume(
                hourly_counts, peak_hour, observed_days
            )
            
            prediction = TrafficPrediction(
                prediction_date=prediction_date,
                predicted_peak_hour=peak_hour,
                predicted_volume=predicted_volume,
                confidence=round(sample_coverage, 2)
            )
            predictions.append(prediction)
        
        return predictions
    
    def _analyze_hourly_patterns(
        self, records: List[ParkingRecord]
    ) -> Tuple[Dict[int, int], int]:
        hourly_counts = {hour: 0 for hour in range(24)}
        observed_dates = set()
        
        for record in records:
            if record.entry_time:
                hour = record.entry_time.hour
                hourly_counts[hour] += 1
                observed_dates.add(record.entry_time.date())

        return hourly_counts, max(1, len(observed_dates))
    
    def _find_peak_hour(self, hourly_counts: Dict[int, int], date: datetime) -> int:
        if not hourly_counts or not any(hourly_counts.values()):
            return 9

        sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_hours[0][0]
    
    def _estimate_volume(
        self, hourly_counts: Dict[int, int], peak_hour: int, observed_days: int
    ) -> int:
        return round(hourly_counts.get(peak_hour, 0) / max(1, observed_days))
    
    def _generate_default_predictions(self, days_ahead: int) -> List[TrafficPrediction]:
        predictions = []
        for day in range(days_ahead):
            prediction_date = datetime.combine(
                (datetime.utcnow() + timedelta(days=day)).date(), time.min
            )
            
            prediction = TrafficPrediction(
                prediction_date=prediction_date,
                predicted_peak_hour=9,
                predicted_volume=0,
                confidence=0.0
            )
            predictions.append(prediction)
        
        return predictions

class SmartScheduler:
    def __init__(self):
        self.predictor = TrafficPredictor()
    
    def assign_parking_spot(self, db: Session, user: User, vehicle_size: str = None) -> int:
        if vehicle_size is None:
            vehicle_size = user.vehicle_size.value
        
        normalized_size = VehicleSize(vehicle_size.upper())
        available_spots = db.query(ParkingSpot).filter(
            ParkingSpot.status == ParkingStatus.AVAILABLE,
            ParkingSpot.size == normalized_size,
        ).all()
        
        if not available_spots:
            available_spots = db.query(ParkingSpot).filter(
                ParkingSpot.status == ParkingStatus.AVAILABLE
            ).all()
        
        if not available_spots:
            return None
        
        scored_spots = []
        for spot in available_spots:
            score = self._calculate_spot_score(spot, user)
            scored_spots.append((spot, score))
        
        scored_spots.sort(key=lambda x: x[1], reverse=True)
        
        best_spot = scored_spots[0][0]
        best_spot.status = ParkingStatus.OCCUPIED
        db.commit()
        
        return best_spot.id
    
    def _calculate_spot_score(self, spot: ParkingSpot, user: User) -> float:
        score = 0.0
        
        if spot.is_special_needs and user.is_special_needs:
            score += 50
        
        if spot.size.value == user.vehicle_size.value:
            score += 30
        elif self._is_size_compatible(spot.size.value, user.vehicle_size.value):
            score += 10
        
        score += (10 - spot.floor) * 2
        
        return score
    
    def _is_size_compatible(self, spot_size: str, vehicle_size: str) -> bool:
        size_order = {"SMALL": 1, "MEDIUM": 2, "LARGE": 3}
        return size_order[spot_size] >= size_order[vehicle_size]
    
    def check_capacity_expansion(self, db: Session) -> bool:
        total_spots = db.query(ParkingSpot).count()
        occupied_spots = db.query(ParkingSpot).filter(
            ParkingSpot.status == ParkingStatus.OCCUPIED
        ).count()
        
        occupancy_rate = occupied_spots / total_spots if total_spots > 0 else 0
        
        return occupancy_rate > 0.85
    
    def get_flash_sale_spots(self, db: Session, count: int = 5) -> List[int]:
        available_spots = db.query(ParkingSpot).filter(
            ParkingSpot.status == ParkingStatus.AVAILABLE
        ).limit(count * 2).all()
        
        return [spot.id for spot in available_spots[:count]]

class LongTermParkingMonitor:
    def __init__(self):
        self.threshold_days = 20
    
    def check_long_term_parking(self, db: Session) -> List[Dict]:
        users = db.query(User).all()
        violations = []
        
        for user in users:
            if user.monthly_parking_days > self.threshold_days:
                violations.append({
                    "user_id": user.id,
                    "username": user.username,
                    "license_plate": user.license_plate,
                    "monthly_days": user.monthly_parking_days,
                    "threshold": self.threshold_days
                })
        
        return violations
    
    def generate_recommendations(self, violations: List[Dict]) -> List[Dict]:
        recommendations = []
        
        for violation in violations:
            recommendation = {
                "user_id": violation["user_id"],
                "nearby_parking_lots": [
                    f"合作停车场A - {violation['username']}专属优惠",
                    f"合作停车场B - 月租套餐"
                ],
                "subsidy_amount": 200.0,
                "message": f"检测到您本月停车{violation['monthly_days']}天，超过阈值{self.threshold_days}天。"
            }
            recommendations.append(recommendation)
        
        return recommendations

class CreditSystem:
    def __init__(self):
        self.compliance_bonus = 10
        self.violation_penalty = -20
        self.no_show_penalty = -15
    
    def update_credit(self, db: Session, user_id: int, change: int, reason: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.credit_score = max(0, min(100, user.credit_score + change))
        
        credit_record = CreditRecord(
            user_id=user_id,
            change_amount=change,
            reason=reason
        )
        db.add(credit_record)
        db.commit()
        
        return True
    
    def update_points(self, db: Session, user_id: int, change: int, reason: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.points = max(0, user.points + change)
        
        point_record = PointRecord(
            user_id=user_id,
            change_amount=change,
            reason=reason
        )
        db.add(point_record)
        db.commit()
        
        return True
    
    def redeem_points(self, db: Session, user_id: int, points: int, reward_type: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.points < points:
            return False
        
        return self.update_points(db, user_id, -points, f"兑换{reward_type}")

class AIManager:
    def __init__(self):
        self.traffic_predictor = TrafficPredictor()
        self.smart_scheduler = SmartScheduler()
        self.long_term_monitor = LongTermParkingMonitor()
        self.credit_system = CreditSystem()
