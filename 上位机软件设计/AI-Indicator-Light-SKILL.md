---
name: ai-indicator
description: "AI指示灯控制 - 通过串口控制LED指示灯和蜂鸣器，显示AI状态（空闲/思考/故障）"
version: "1.2.0"
author: "AI Assistant"
agent_created: true
---

# AI指示灯控制 Skill v1.2

## ⚡ 关键使用规则（必须遵守）

**状态切换必须"第一时间"触发，不能延迟到任务中后期！**

| 时机 | 立即执行的动作 |
|------|---------------|
| **收到用户任务的第一时间**（在任何工具调用、读文件之前） | `POST /api/light/yellow` → 🟡 黄灯 |
| **任务完成、等待用户下一步** | `POST /api/light/green` → 🟢 绿灯 |
| **遇到错误、需要用户确认/授权** | `POST /api/light/red` → 🔴 红灯 |
| **重要节点完成（如交付文件）** | `POST /api/buzzer` 音量50响1秒 → 🔊 提示 |

**反模式（禁止）**：
- ❌ 先读完文件/执行多个工具调用，才发黄灯
- ❌ 任务做完很久后才切回绿灯
- ❌ 把状态切换放到任务最后批量执行

**正确模式**：
- ✅ 收到任务的**第一个动作**就是发黄灯（哪怕只是读个文件）
- ✅ 任务真正完成的**最后一个动作**是发绿灯
- ✅ 状态变化与实际AI工作状态实时同步

### 快速触发模板

收到任务时，**并行**执行（不要串行等待）：

```bash
# 立即发黄灯（不等任何结果）
curl -s -X POST http://127.0.0.1:5000/api/light/yellow --connect-timeout 1 > /dev/null &

# 然后才开始真正的任务
# ... 你的工具调用 ...
```

任务完成时：

```bash
# 发绿灯 + 可选蜂鸣
curl -s -X POST http://127.0.0.1:5000/api/light/green --connect-timeout 1 > /dev/null
curl -s -X POST http://127.0.0.1:5000/api/buzzer -H "Content-Type: application/json" -d '{"volume":30,"duration":1}' --connect-timeout 1 > /dev/null
```

## 功能描述

这个Skill允许Agent通过HTTP API控制AI指示灯硬件，实现以下功能：

- 🟢 **绿灯**：表示AI处于空闲状态
- 🟡 **黄灯**：表示AI正在思考/处理
- 🔴 **红灯**：表示故障/异常状态
- ⚫ **关闭**：关闭指示灯
- 🔊 **蜂鸣器**：设置音量和时长

## 使用前准备

### 1. 安装依赖

```bash
cd "C:\Users\87165\Desktop\Project\AI指示灯\上位机软件设计"
pip install -r requirements.txt
```

### 2. 启动软件

```bash
cd "C:\Users\87165\Desktop\Project\AI指示灯\上位机软件设计"
python main.py
```

然后在界面中：
1. 选择串口（波特率固定115200）
2. 点击"连接串口"
3. 勾选"启用API服务"

### 3. 硬件连接

- LED：PA5(红) / PA6(黄) / PA7(绿)
- 蜂鸣器：PB1 (TIM3_CH4 PWM, 1KHz)
- 串口：USART1 (PA9=TX, PA10=RX, 115200, 8N1)

## API调用方法

API服务启动后，默认地址：`http://127.0.0.1:5000`

### 1. 设置绿灯（AI空闲）

```python
import requests
response = requests.post('http://127.0.0.1:5000/api/light/green')
```

### 2. 设置黄灯（AI思考）

```python
response = requests.post('http://127.0.0.1:5000/api/light/yellow')
```

### 3. 设置红灯（故障/异常）

```python
response = requests.post('http://127.0.0.1:5000/api/light/red')
```

### 4. 关闭灯光

```python
response = requests.post('http://127.0.0.1:5000/api/light/off')
```

### 5. 设置蜂鸣器

```python
response = requests.post('http://127.0.0.1:5000/api/buzzer',
    json={"volume": 80, "duration": 10})
```

### 6. 检查服务状态

```python
response = requests.get('http://127.0.0.1:5000/api/health')
```

## Agent集成示例

```python
import requests
from typing import Literal

class AIIndicatorController:
    """AI指示灯控制器"""

    def __init__(self, api_url: str = "http://127.0.0.1:5000"):
        self.api_url = api_url

    def set_status(self, status: Literal["idle", "thinking", "error", "off"]):
        """设置AI状态指示灯"""
        endpoint_map = {
            "idle": "/api/light/green",
            "thinking": "/api/light/yellow",
            "error": "/api/light/red",
            "off": "/api/light/off"
        }
        endpoint = endpoint_map.get(status)
        if not endpoint:
            return False
        try:
            response = requests.post(f"{self.api_url}{endpoint}", timeout=2)
            return response.json().get("success", False)
        except:
            return False

    def set_buzzer(self, volume: int, duration: int):
        """设置蜂鸣器"""
        try:
            response = requests.post(f"{self.api_url}/api/buzzer",
                json={"volume": volume, "duration": duration}, timeout=2)
            return response.json().get("success", False)
        except:
            return False

# 使用示例
indicator = AIIndicatorController()
indicator.set_status("thinking")   # AI开始思考
indicator.set_status("idle")       # AI恢复空闲
indicator.set_buzzer(50, 3)        # 蜂鸣器：音量50，响3秒
```

## 通信协议

帧格式：`[0xAA] [命令字] [数据长度] [数据] [校验和]`
校验和：XOR异或

| 命令 | 值 | 数据 |
|------|-----|------|
| 绿灯 | 0x01 | 无 |
| 黄灯 | 0x02 | 无 |
| 红灯 | 0x03 | 无 |
| 关闭 | 0x04 | 无 |
| 蜂鸣器 | 0x05 | [音量, 时长] |

## 故障排除

1. **API无法连接**：确认软件已启动且已启用API服务
2. **串口连接失败**：确认串口未被占用，波特率固定115200
3. **指示灯无反应**：检查硬件连接和协议配置
