"""
智能停车管理系统 - 演示脚本

本脚本演示系统的核心功能，包括：
1. 创建用户和车位
2. 车辆入场和离场
3. 预约功能
4. 智能规则调度
5. 长时停车监控
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

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

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_result(message, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def demo_user_management():
    print_section("1. 用户管理演示")
    
    users = [
        {"username": "张经理", "phone": "13800001111", "license_plate": "京A88888", 
         "member_level": 4, "vehicle_size": "LARGE", "is_special_needs": False},
        {"username": "李工程师", "phone": "13800002222", "license_plate": "京A66666", 
         "member_level": 3, "vehicle_size": "MEDIUM", "is_special_needs": False},
        {"username": "王阿姨", "phone": "13800003333", "license_plate": "京A55555", 
         "member_level": 2, "vehicle_size": "SMALL", "is_special_needs": True},
    ]
    
    user_ids = []
    for user_data in users:
        response = SESSION.post(f"{API_BASE_URL}/api/users/", json=user_data)
        if response.status_code == 201:
            user = response.json()
            user_ids.append(user["id"])
            print_result(f"创建用户: {user['username']} (会员等级: {user['member_level']})")
        else:
            print_result(f"用户 {user_data['username']} 可能已存在", success=False)
    
    return user_ids

def demo_parking_spots():
    print_section("2. 车位管理演示")
    
    spots = [
        {"spot_number": "VIP001", "floor": 1, "zone": "VIP", "size": "LARGE", "is_special_needs": False},
        {"spot_number": "A001", "floor": 1, "zone": "A", "size": "MEDIUM", "is_special_needs": False},
        {"spot_number": "A002", "floor": 1, "zone": "A", "size": "MEDIUM", "is_special_needs": False},
        {"spot_number": "B001", "floor": 2, "zone": "B", "size": "SMALL", "is_special_needs": True},
        {"spot_number": "B002", "floor": 2, "zone": "B", "size": "MEDIUM", "is_special_needs": False},
    ]
    
    spot_ids = []
    for spot_data in spots:
        response = SESSION.post(f"{API_BASE_URL}/api/parking-spots/", json=spot_data)
        if response.status_code == 201:
            spot = response.json()
            spot_ids.append(spot["id"])
            print_result(f"创建车位: {spot['spot_number']} ({spot['floor']}层{spot['zone']}区)")
        else:
            print_result(f"车位 {spot_data['spot_number']} 可能已存在", success=False)
    
    response = SESSION.get(f"{API_BASE_URL}/api/parking-spots/stats/summary")
    if response.status_code == 200:
        stats = response.json()
        print(f"\n📊 车位统计:")
        print(f"   总车位: {stats['total_spots']}")
        print(f"   可用车位: {stats['available_spots']}")
        print(f"   占用率: {stats['occupancy_rate']*100:.1f}%")
    
    return spot_ids

def demo_parking_entry_exit(user_ids, spot_ids):
    print_section("3. 停车入场和离场演示")
    
    if not user_ids or not spot_ids:
        print_result("没有可用的用户或车位", success=False)
        return
    
    user_id = user_ids[0]
    spot_id = spot_ids[0]
    
    print(f"\n🚗 车辆入场...")
    record_data = {"user_id": user_id, "parking_spot_id": spot_id}
    response = SESSION.post(f"{API_BASE_URL}/api/parking-records/", json=record_data)
    if response.status_code == 201:
        record = response.json()
        print_result(f"入场成功！记录ID: {record['id']}")
        record_id = record['id']
        
        time.sleep(2)
        
        print(f"\n🚕 车辆离场...")
        response = SESSION.post(f"{API_BASE_URL}/api/parking-records/{record_id}/exit")
        if response.status_code == 200:
            result = response.json()
            print_result(f"离场成功！停车时长: {result['duration_hours']}小时，费用: ¥{result['fee']}")
            print(f"   用户获得信誉积分和奖励积分")
    else:
        print_result("入场失败", success=False)

def demo_smart_assignment(user_ids):
    print_section("4. 智能车位分配演示")
    
    if not user_ids:
        print_result("没有可用的用户", success=False)
        return
    
    user_id = user_ids[1] if len(user_ids) > 1 else user_ids[0]
    
    print(f"\n🧠 为用户 {user_id} 进行智能分配...")
    response = SESSION.post(f"{API_BASE_URL}/api/parking-spots/smart-assign/{user_id}")
    if response.status_code == 200:
        result = response.json()
        print_result(f"智能分配成功！分配车位ID: {result['spot_id']}")
        print(f"   系统根据用户等级、车辆尺寸、特殊需求等因素自动选择最优车位")
    else:
        print_result("智能分配失败，可能没有可用车位", success=False)

def demo_reservation(user_ids, spot_ids):
    print_section("5. 预约功能演示")
    
    if not user_ids or not spot_ids:
        print_result("没有可用的用户或车位", success=False)
        return
    
    user_id = user_ids[2] if len(user_ids) > 2 else user_ids[0]
    
    print(f"\n📅 创建预约...")
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)
    
    reservation_data = {
        "user_id": user_id,
        "parking_spot_id": spot_ids[1],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    response = SESSION.post(f"{API_BASE_URL}/api/reservations/", json=reservation_data)
    if response.status_code == 201:
        reservation = response.json()
        print_result(f"预约创建成功！预约ID: {reservation['id']}")
        print(f"   预约时间: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
    else:
        print_result("预约创建失败", success=False)

def demo_flash_sale(user_ids):
    print_section("6. 秒杀预约演示")
    
    if not user_ids:
        print_result("没有可用的用户", success=False)
        return
    
    user_id = user_ids[0]
    
    print(f"\n🔥 查看秒杀车位...")
    response = SESSION.get(f"{API_BASE_URL}/api/reservations/flash-sale/available")
    if response.status_code == 200:
        flash_sale = response.json()
        if flash_sale["count"] > 0:
            print(f"   当前有 {flash_sale['count']} 个秒杀车位可用")
            
            print(f"\n⚡ 用户 {user_id} 参与秒杀...")
            response = SESSION.post(f"{API_BASE_URL}/api/reservations/flash-sale/{user_id}")
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print_result(f"🎉 秒杀成功！预约ID: {result['reservation_id']}")
                else:
                    print_result(result["message"], success=False)
        else:
            print_result("当前没有可用的秒杀车位", success=False)

def demo_ai_predictions():
    print_section("7. AI流量预测演示")
    
    print(f"\n📈 生成未来7天的流量预测...")
    response = SESSION.post(f"{API_BASE_URL}/api/ai/traffic-predictions/generate?days_ahead=7")
    if response.status_code == 200:
        result = response.json()
        print_result(f"预测生成成功！生成 {result['predictions_count']} 天的预测")
        
        response = SESSION.get(f"{API_BASE_URL}/api/ai/traffic-predictions")
        if response.status_code == 200:
            predictions = response.json()
            print(f"\n📊 未来流量预测:")
            for pred in predictions[:3]:
                date = pred['prediction_date'][:10]
                peak_hour = pred['predicted_peak_hour']
                volume = pred['predicted_volume']
                confidence = pred['confidence'] * 100
                print(f"   {date}: 高峰时段 {peak_hour}:00, 预测流量 {volume}辆 (置信度: {confidence:.0f}%)")
    else:
        print_result("流量预测生成失败", success=False)

def demo_long_term_monitoring():
    print_section("8. 长时停车监控演示")
    
    print(f"\n🚨 检查长时停车违规...")
    response = SESSION.get(f"{API_BASE_URL}/api/ai/long-term-violations")
    if response.status_code == 200:
        violations = response.json()
        if violations["violations"]:
            print_result(f"发现 {len(violations['violations'])} 个长时停车违规")
            for violation in violations["violations"]:
                print(f"   ⚠️  用户 {violation['username']} (车牌: {violation['license_plate']})")
                print(f"      本月停车 {violation['monthly_days']} 天，超过阈值 {violation['threshold']} 天")
            
            print(f"\n💡 推荐解决方案:")
            for rec in violations["recommendations"][:2]:
                print(f"   补贴金额: ¥{rec['subsidy_amount']}")
                for lot in rec["nearby_parking_lots"]:
                    print(f"   • {lot}")
        else:
            print_result("✅ 没有发现长时停车违规，所有用户合规停车")

def demo_capacity_expansion():
    print_section("9. 容量扩容检查演示")
    
    print(f"\n📊 检查是否需要扩容...")
    response = SESSION.post(f"{API_BASE_URL}/api/ai/check-capacity-expansion")
    if response.status_code == 200:
        result = response.json()
        if result["should_expand"]:
            print_result(f"⚠️  {result['message']}")
            print(f"   当前占用率超过85%，建议启动扩容策略")
        else:
            print_result(f"✅ {result['message']}")
            print(f"   当前容量充足，无需扩容")

def demo_system_configs():
    print_section("10. 系统配置演示")
    
    print(f"\n⚙️  查看系统配置...")
    response = SESSION.get(f"{API_BASE_URL}/api/ai/configs")
    if response.status_code == 200:
        configs = response.json()
        print(f"   当前系统配置:")
        for config in configs:
            print(f"   • {config['config_key']}: {config['config_value']}")
            if config['description']:
                print(f"     ({config['description']})")

def main():
    print("\n" + "="*70)
    print("  🚗 智能停车管理系统 - 功能演示")
    print("="*70)
    print(f"\n演示开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        authenticate()
        user_ids = demo_user_management()
        spot_ids = demo_parking_spots()
        demo_parking_entry_exit(user_ids, spot_ids)
        demo_smart_assignment(user_ids)
        demo_reservation(user_ids, spot_ids)
        demo_flash_sale(user_ids)
        demo_ai_predictions()
        demo_long_term_monitoring()
        demo_capacity_expansion()
        demo_system_configs()
        
        print_section("演示完成")
        print(f"\n✅ 所有功能演示完成！")
        print(f"演示结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n💡 提示:")
        print(f"   - 访问前端界面: http://localhost:8000")
        print(f"   - 访问API文档: http://localhost:8000/docs")
        print(f"   - 查看完整项目文档: README.md")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到API服务器")
        print("请确保后端服务已启动:")
        print("  uv run python -m backend.main")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")

if __name__ == "__main__":
    main()
