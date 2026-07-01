"""
API测试脚本 - 测试AI指示灯控制器的所有API端点
"""

import requests
import time


BASE_URL = "http://127.0.0.1:5000"


def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试1：健康检查")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    

def test_get_ports():
    """测试获取串口列表"""
    print("=" * 60)
    print("测试2：获取串口列表")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/serial/ports")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    

def test_light_control():
    """测试灯光控制"""
    print("=" * 60)
    print("测试3：灯光控制")
    print("=" * 60)
    
    # 测试绿灯
    print("→ 点亮绿灯（AI空闲）...")
    response = requests.post(f"{BASE_URL}/api/light/green")
    print(f"  响应: {response.json()}")
    time.sleep(1)
    
    # 测试黄灯
    print("→ 点亮黄灯（AI思考）...")
    response = requests.post(f"{BASE_URL}/api/light/yellow")
    print(f"  响应: {response.json()}")
    time.sleep(1)
    
    # 测试红灯
    print("→ 点亮红灯（故障/异常）...")
    response = requests.post(f"{BASE_URL}/api/light/red")
    print(f"  响应: {response.json()}")
    time.sleep(1)
    
    # 测试关闭
    print("→ 关闭灯光...")
    response = requests.post(f"{BASE_URL}/api/light/off")
    print(f"  响应: {response.json()}")
    print()
    

def test_buzzer():
    """测试蜂鸣器控制"""
    print("=" * 60)
    print("测试4：蜂鸣器控制")
    print("=" * 60)
    
    # 测试设置蜂鸣器
    print("→ 设置蜂鸣器（音量50，时长5秒）...")
    data = {"volume": 50, "duration": 5}
    response = requests.post(f"{BASE_URL}/api/buzzer", json=data)
    print(f"  响应: {response.json()}")
    print()
    
    # 测试边界值
    print("→ 测试边界值（音量0，时长0）...")
    data = {"volume": 0, "duration": 0}
    response = requests.post(f"{BASE_URL}/api/buzzer", json=data)
    print(f"  响应: {response.json()}")
    print()
    
    # 测试最大边界值
    print("→ 测试最大边界值（音量100，时长60）...")
    data = {"volume": 100, "duration": 60}
    response = requests.post(f"{BASE_URL}/api/buzzer", json=data)
    print(f"  响应: {response.json()}")
    print()
    

def test_status():
    """测试获取状态"""
    print("=" * 60)
    print("测试5：获取状态")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    

def test_protocol():
    """测试通信协议"""
    print("=" * 60)
    print("测试6：通信协议验证")
    print("=" * 60)
    
    print("协议帧格式：")
    print("  [起始位 0xAA] [命令字] [数据长度] [数据] [校验和]")
    print()
    
    print("示例帧（点亮绿灯）：")
    print("  0xAA 0x01 0x00 0xAA")
    print("  └─起始位  └命令  └无数据  └校验和")
    print()
    
    print("示例帧（设置蜂鸣器，音量80，时长10秒）：")
    print("  0xAA 0x05 0x02 0x50 0x0A 0xFD")
    print("  └─起始位  └命令  └2字节  └音量  └时长  └校验和")
    print()
    

def main():
    """主函数"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AI指示灯控制器 - API测试脚本" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # 测试健康检查
        test_health()
        
        # 测试获取串口
        test_get_ports()
        
        # 测试灯光控制
        test_light_control()
        
        # 测试蜂鸣器
        test_buzzer()
        
        # 测试状态查询
        test_status()
        
        # 显示协议信息
        test_protocol()
        
        print("=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print()
        print("✗ 错误：无法连接到API服务器")
        print()
        print("请确保：")
        print("  1. 软件已启动")
        print("  2. 已勾选'启用API服务'")
        print("  3. API服务运行在 http://127.0.0.1:5000")
        print()
        
    except Exception as e:
        print()
        print(f"✗ 测试过程中出现错误: {e}")
        print()
        

if __name__ == '__main__':
    main()
