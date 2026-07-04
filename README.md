# AI指示灯 (AI Indicator Light)

一个完整的上下位机AI状态指示灯系统，通过串口控制LED指示灯和蜂鸣器，实时显示AI的工作状态。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.1-green.svg)
![Platform](https://img.shields.io/badge/platform-STM32F030%20%7C%20Python-orange.svg)

## 项目简介

本项目旨在为AI助手提供一个物理状态指示灯，让用户在远离屏幕时也能直观感知AI的当前状态。系统分为上位机（Python GUI + API）和下位机（STM32固件）两部分。

### 状态定义

| 灯光 | 状态 | 说明 |
|------|------|------|
| 🟢 绿灯 | 空闲 | AI等待新任务 |
| 🟡 黄灯 | 思考 | AI正在处理任务 |
| 🔴 红灯 | 故障 | 故障/异常状态 |
| ⚫ 关闭 | - | 关闭指示灯 |
| 🔊 蜂鸣器 | - | 音量0-100，时长0-60秒 |

## 系统架构

```
┌──────────────────────────────────────────────┐
│  上位机 (Python)                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ GUI界面  │  │ HTTP API │  │ Agent Skill│  │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       └──────┬──────┘              │         │
│              ▼                     │         │
│     ┌────────────────┐             │         │
│     │ Serial Handler │◄────────────┘         │
│     │ (协议帧+校验和) │                      │
│     └───────┬────────┘                      │
└─────────────┼────────────────────────────────┘
              │ USB转TTL (115200, 8N1)
              ▼
┌──────────────────────────────────────────────┐
│  下位机 (STM32F030F4Px)                       │
│  ┌────────┐ ┌────────┐ ┌──────────────────┐  │
│  │ USART1 │ │ GPIO   │ │ TIM3 CH4 (PWM)  │  │
│  │PA9/PA10│ │PA5/6/7 │ │ PB1 (蜂鸣器)    │  │
│  └────────┘ └────────┘ └──────────────────┘  │
└──────────────────────────────────────────────┘
```

## 目录结构

```
AI指示灯/
├── 上位机软件设计/                  # Python GUI + Flask API
│   ├── main.py                      # 主程序入口
│   ├── gui.py                       # GUI界面 (深色主题)
│   ├── serial_handler.py            # 串口通信 (协议帧+XOR校验)
│   ├── api_server.py                # HTTP API服务 (Flask)
│   ├── agent_example.py             # Agent集成示例
│   ├── test_api.py                  # API测试脚本
│   ├── SKILL.md                     # WorkBuddy Skill 定义文件
│   ├── PROTOCOL.md                  # 通信协议文档
│   ├── requirements.txt             # Python依赖
│   ├── start.bat                    # Windows启动脚本
│   └── install_deps.bat             # 依赖安装脚本
│
├── 下位机软件设计/                  # STM32固件 (Keil工程)
│   └── AI_LED/
│       ├── Core/
│       │   ├── Inc/                 # 头文件
│       │   │   ├── main.h           # 引脚定义
│       │   │   ├── protocol.h       # 通信协议
│       │   │   ├── led.h            # LED控制
│       │   │   ├── buzzer.h         # 蜂鸣器控制
│       │   │   ├── tim.h            # 定时器
│       │   │   ├── usart.h          # 串口
│       │   │   └── gpio.h           # GPIO
│       │   └── Src/                 # 源文件
│       │       ├── main.c           # 主程序
│       │       ├── protocol.c       # 协议解析 (状态机)
│       │       ├── led.c            # LED控制实现
│       │       ├── buzzer.c         # 蜂鸣器PWM控制
│       │       ├── tim.c            # TIM3 PWM (1KHz)
│       │       ├── usart.c          # 串口中断接收
│       │       ├── gpio.c           # GPIO初始化
│       │       └── stm32f0xx_it.c   # 中断服务
│       ├── Drivers/                 # HAL库 + CMSIS
│       ├── MDK-ARM/
│       │   ├── AI_LED.uvprojx       # Keil工程文件
│       │   └── startup_stm32f030x6.s  # 启动文件
│       └── AI_LED.ioc               # CubeMX工程配置
│
├── 下位机硬件设计/                  # EasyEDA Pro硬件工程
│   └── ProPrj_AI工作灯_2026-06-30.epro
│
├── .gitignore
└── README.md                        # 本文件
```

## 快速开始

### 上位机

**环境要求**：Python 3.7+

```bash
cd 上位机软件设计
pip install -r requirements.txt
python main.py
```

启动后：
1. 选择串口 → 点击「连接串口」
2. 使用灯光按钮控制LED
3. 调整蜂鸣器音量和时长 → 点击「保存到设备」
4. 勾选「启用API服务」供Agent调用

### 下位机

**工具**：Keil MDK-ARM v5

1. 用Keil打开 `下位机软件设计/AI_LED/MDK-ARM/AI_LED.uvprojx`
2. 编译并下载到STM32F030F4Px

### 硬件连接

| 上位机 (USB转TTL) | 下位机 (STM32) | 说明 |
|:-:|:-:|:-:|
| TX | PA10 (RX) | 串口交叉连接 |
| RX | PA9 (TX) | 串口交叉连接 |
| GND | GND | 共地 |

## 通信协议

### 帧格式

```
| 起始位 0xAA | 命令字 | 数据长度 | 数据 | 校验和 |
| 1字节       | 1字节  | 1字节   | N字节 | 1字节  |
```

**校验和**：从起始位到数据结束所有字节的 XOR（异或）

### 命令字

| 命令 | 值 | 数据 | 示例帧 |
|------|-----|------|--------|
| 绿灯 | 0x01 | 无 | `AA 01 00 AA` |
| 黄灯 | 0x02 | 无 | `AA 02 00 A8` |
| 红灯 | 0x03 | 无 | `AA 03 00 AB` |
| 关闭 | 0x04 | 无 | `AA 04 00 AE` |
| 蜂鸣器 | 0x05 | [音量, 时长] | `AA 05 02 50 0A FD` |

完整协议文档：[上位机软件设计/PROTOCOL.md](上位机软件设计/PROTOCOL.md)

## API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/status` | GET | 获取当前状态 |
| `/api/serial/ports` | GET | 获取可用串口列表 |
| `/api/serial/connect` | POST | 连接串口 |
| `/api/serial/disconnect` | POST | 断开串口 |
| `/api/light/green` | POST | 点亮绿灯 |
| `/api/light/yellow` | POST | 点亮黄灯 |
| `/api/light/red` | POST | 点亮红灯 |
| `/api/light/off` | POST | 关闭灯光 |
| `/api/buzzer` | POST | 设置蜂鸣器 |

### 调用示例

```python
import requests

# AI开始思考 → 黄灯
requests.post('http://127.0.0.1:5000/api/light/yellow')

# AI恢复空闲 → 绿灯
requests.post('http://127.0.0.1:5000/api/light/green')

# 设置蜂鸣器：音量80，响10秒
requests.post('http://127.0.0.1:5000/api/buzzer',
    json={"volume": 80, "duration": 10})
```

## 硬件配置

| 外设 | 引脚 | 说明 |
|------|------|------|
| LED_RED | PA5 | 红灯 - 推挽输出 |
| LED_YELLOW | PA6 | 黄灯 - 推挽输出 |
| LED_GREEN | PA7 | 绿灯 - 推挽输出 |
| BUZZER | PB1 | 蜂鸣器 - TIM3_CH4 PWM (1KHz) |
| USART1_TX | PA9 | 串口发送 |
| USART1_RX | PA10 | 串口接收 |

- **MCU**：STM32F030F4Px (Cortex-M0, 48MHz)
- **串口**：115200 baud, 8N1
- **PWM频率**：1KHz (48MHz / 48 / 1000)

## 技术栈

**上位机**：
- Python 3.7+
- tkinter (GUI)
- pyserial (串口通信)
- Flask (HTTP API)

**下位机**：
- STM32F030F4Px
- HAL库
- Keil MDK-ARM

## Agent集成

本项目提供了WorkBuddy Skill文件，Agent可自动调用指示灯：

```python
from agent_example import AIIndicatorController

indicator = AIIndicatorController()
indicator.set_thinking()    # AI开始思考 → 黄灯
indicator.set_idle()        # AI恢复空闲 → 绿灯
indicator.set_buzzer(50, 3) # 蜂鸣器：音量50，响3秒
```

### SKILL.md 是什么？

[`上位机软件设计/SKILL.md`](上位机软件设计/SKILL.md) 是一份 **WorkBuddy Skill 定义文件**，描述了如何通过 HTTP API 控制本指示灯。WorkBuddy（或其他兼容的 AI Agent 平台）加载该文件后，Agent 即可在执行任务时自动联动指示灯：

- 收到任务的**第一时刻** → 点亮黄灯（表示"AI 正在思考"）
- 任务**完成**后 → 切换绿灯（表示"AI 空闲，等待新指令"）
- 遇到**错误或需要用户授权** → 点亮红灯 + 蜂鸣器提示

**使用方法**：

1. 启动上位机软件并勾选「启用 API 服务」（默认监听 `http://127.0.0.1:5000`）
2. 将 `SKILL.md` 复制到 WorkBuddy 的用户级 skills 目录：
   - Windows：`C:\Users\<用户名>\.workbuddy\skills\ai-indicator\SKILL.md`
3. 重启 WorkBuddy 会话，Agent 即可自动识别并调用

> 📌 仓库里的 `SKILL.md` 仅为存档与分享用途。真正生效的副本位于 `~/.workbuddy/skills/` 目录，修改后需同步回去才会被 Agent 加载。

## License

MIT License
