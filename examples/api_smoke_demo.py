import requests
import json
import os
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"
SESSION = requests.Session()

def authenticate():
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("Set ADMIN_PASSWORD before running this example")
    response = SESSION.post(
        f"{API_BASE_URL}/api/auth/login/json",
        json={"username": os.getenv("ADMIN_USERNAME", "admin"), "password": password},
    )
    response.raise_for_status()
    SESSION.headers.update({
        "Authorization": f"Bearer {response.json()['access_token']}"
    })

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    if response.status_code in [200, 201]:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.text}")

def test_system():
    print("\n" + "="*60)
    print("AI智能停车场管理系统 - 功能测试")
    print("="*60)
    
    print("\n1. 测试用户管理")
    print("-" * 60)
    
    new_user = {
        "username": "测试用户",
        "phone": "13900139000",
        "license_plate": "京TEST01",
        "vehicle_size": "MEDIUM",
        "is_special_needs": False
    }
    
    response = SESSION.post(f"{API_BASE_URL}/api/users/", json=new_user)
    print_response(response, "创建用户")
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        
        response = SESSION.get(f"{API_BASE_URL}/api/users/")
        print_response(response, "获取用户列表")
        
        response = SESSION.get(f"{API_BASE_URL}/api/users/{user_id}")
        print_response(response, "获取用户详情")
    
    print("\n2. 测试车位管理")
    print("-" * 60)
    
    new_spot = {
        "spot_number": "TEST001",
        "floor": 1,
        "zone": "T",
        "size": "MEDIUM",
        "is_special_needs": False
    }
    
    response = SESSION.post(f"{API_BASE_URL}/api/parking-spots/", json=new_spot)
    print_response(response, "创建车位")
    
    if response.status_code == 201:
        spot_id = response.json()["id"]
        
        response = SESSION.get(f"{API_BASE_URL}/api/parking-spots/")
        print_response(response, "获取车位列表")
        
        response = SESSION.get(f"{API_BASE_URL}/api/parking-spots/stats/summary")
        print_response(response, "获取车位统计")
    
    print("\n3. 测试停车记录")
    print("-" * 60)
    
    if 'user_id' in locals() and 'spot_id' in locals():
        new_record = {
            "user_id": user_id,
            "parking_spot_id": spot_id
        }
        
        response = SESSION.post(f"{API_BASE_URL}/api/parking-records/", json=new_record)
        print_response(response, "创建停车记录（入场）")
        
        if response.status_code == 201:
            record_id = response.json()["id"]
            
            response = SESSION.get(f"{API_BASE_URL}/api/parking-records/active")
            print_response(response, "获取当前在停车辆")
            
            response = SESSION.get(f"{API_BASE_URL}/api/parking-records/license-plate/京TEST01")
            print_response(response, "根据车牌号查找车辆")
            
            response = SESSION.post(f"{API_BASE_URL}/api/parking-records/{record_id}/exit")
            print_response(response, "车辆离场")
    
    print("\n4. 测试预约管理")
    print("-" * 60)
    
    if 'user_id' in locals():
        available_spots = SESSION.get(f"{API_BASE_URL}/api/parking-spots/?status_filter=AVAILABLE")
        if available_spots.status_code == 200 and len(available_spots.json()) > 0:
            available_spot_id = available_spots.json()[0]["id"]
            
            start_time = datetime.now() + timedelta(hours=1)
            end_time = datetime.now() + timedelta(hours=3)
            
            new_reservation = {
                "user_id": user_id,
                "parking_spot_id": available_spot_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            response = SESSION.post(f"{API_BASE_URL}/api/reservations/", json=new_reservation)
            print_response(response, "创建预约")
            
            if response.status_code == 201:
                reservation_id = response.json()["id"]
                
                response = SESSION.get(f"{API_BASE_URL}/api/reservations/")
                print_response(response, "获取预约列表")
    
    print("\n5. 测试AI智能调度")
    print("-" * 60)
    
    response = SESSION.post(f"{API_BASE_URL}/api/ai/traffic-predictions/generate?days_ahead=7")
    print_response(response, "生成流量预测")
    
    response = SESSION.get(f"{API_BASE_URL}/api/ai/traffic-predictions")
    print_response(response, "获取流量预测")
    
    response = SESSION.get(f"{API_BASE_URL}/api/ai/long-term-violations")
    print_response(response, "获取长时停车违规")
    
    response = SESSION.post(f"{API_BASE_URL}/api/ai/check-capacity-expansion")
    print_response(response, "检查容量扩容")
    
    response = SESSION.get(f"{API_BASE_URL}/api/ai/configs")
    print_response(response, "获取系统配置")
    
    response = SESSION.post(f"{API_BASE_URL}/api/ai/init-default-configs")
    print_response(response, "初始化默认配置")
    
    print("\n6. 测试智能分配")
    print("-" * 60)
    
    if 'user_id' in locals():
        response = SESSION.post(f"{API_BASE_URL}/api/parking-spots/smart-assign/{user_id}")
        print_response(response, "智能分配车位")
    
    print("\n7. 测试秒杀预约")
    print("-" * 60)
    
    if 'user_id' in locals():
        response = SESSION.get(f"{API_BASE_URL}/api/reservations/flash-sale/available")
        print_response(response, "获取秒杀车位")
        
        if response.status_code == 200 and response.json()["count"] > 0:
            response = SESSION.post(f"{API_BASE_URL}/api/reservations/flash-sale/{user_id}")
            print_response(response, "参与秒杀预约")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

if __name__ == "__main__":
    try:
        authenticate()
        test_system()
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到API服务器")
        print("请确保后端服务已启动: uv run python -m backend.main")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
