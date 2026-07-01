# AI指示灯控制器 v1.1

一个美观的AI状态指示灯控制软件（上位机），通过串口与STM32下位机通信，实时显示AI的工作状态。

## 功能特性

- 🎨 **现代化深色主题GUI界面**：左右分栏布局，操作直观
- 🔌 **串口自动检测**：自动扫描可用串口，按编号从小到大排序
- 📡 **自定义通信协议**：带校验和的帧格式，数据可靠
- 💡 **三种状态指示**：
  - 🟢 **绿灯**：AI处于空闲状态
  - 🟡 **黄灯**：AI正在思考/处理
  - 🔴 **红灯**：故障/异常状态
- 🔊 **蜂鸣器控制**：音量0-100滑块调节，时长0-60秒手动输入
- 🌐 **HTTP API服务**：提供REST API，供Agent程序调用
- 📝 **运行日志**：实时显示操作日志，方便调试

## 快速开始

### 1. 安装依赖

```bash
cd "C:\Users\87165\Desktop\Project\AI指示灯\上位机软件设计"
pip install -r requirements.txt
```

### 2. 启动软件

```bash
python main.py
```

### 3. 操作步骤

1. 点击 **🔄** 刷新串口列表
2. 选择串口（波特率固定115200）
3. 点击 **📡 连接串口**
4. 使用灯光按钮控制LED（空闲/思考/故障/关闭）
5. 调整蜂鸣器音量和时长，点击 **💾 保存到设备**
6. 勾选 **启用API服务**（如需Agent调用）

## 通信协议 v1.1

### 帧格式

```
| 起始位 0xAA | 命令字 | 数据长度 | 数据 | 校验和 |
| 1字节       | 1字节  | 1字节   | N字节 | 1字节  |
```

- 校验和：从起始位到数据结束所有字节的 **XOR（异或）**

### 命令字

| 命令字 | 值 | 说明 | 数据 |
|--------|-----|------|------|
| 绿灯 | `0x01` | AI空闲 | 无 |
| 黄灯 | `0x02` | AI思考 | 无 |
| 红灯 | `0x03` | 故障/异常 | 无 |
| 关闭 | `0x04` | 关闭灯光 | 无 |
| 蜂鸣器 | `0x05` | 设置蜂鸣器 | [音量, 时长] |

详细协议文档见 `PROTOCOL.md`

## API文档

### 基础URL
```
http://127.0.0.1:5000
```

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/status` | GET | 获取当前状态 |
| `/api/serial/ports` | GET | 获取可用串口列表 |
| `/api/serial/connect` | POST | 连接串口 |
| `/api/serial/disconnect` | POST | 断开串口 |
| `/api/light/green` | POST | 点亮绿灯（AI空闲） |
| `/api/light/yellow` | POST | 点亮黄灯（AI思考） |
| `/api/light/red` | POST | 点亮红灯（故障/异常） |
| `/api/light/off` | POST | 关闭灯光 |
| `/api/buzzer` | POST | 设置蜂鸣器 |

### 蜂鸣器API示例

```bash
curl -X POST http://127.0.0.1:5000/api/buzzer \
  -H "Content-Type: application/json" \
  -d '{"volume": 80, "duration": 10}'
```

## 硬件配置

| 外设 | 引脚 | 说明 |
|------|------|------|
| LED_RED | PA5 | 红灯（故障/异常） |
| LED_YELLOW | PA6 | 黄灯（AI思考） |
| LED_GREEN | PA7 | 绿灯（AI空闲） |
| BUZZER | PB1 | 蜂鸣器（TIM3_CH4 PWM, 1KHz） |
| USART1_TX | PA9 | 串口发送 |
| USART1_RX | PA10 | 串口接收 |

## 项目结构

```
AI指示灯/
├── 上位机软件设计/          ← 本目录（Python GUI + API）
│   ├── main.py             # 主程序入口
│   ├── gui.py              # GUI界面（深色主题）
│   ├── serial_handler.py   # 串口通信（协议帧+校验和）
│   ├── api_server.py       # HTTP API服务（Flask）
│   ├── agent_example.py    # Agent集成示例
│   ├── test_api.py         # API测试脚本
│   ├── PROTOCOL.md         # 通信协议文档
│   ├── requirements.txt    # 依赖列表
│   ├── start.bat           # Windows启动脚本
│   └── install_deps.bat    # 依赖安装脚本
├── 下位机软件设计/          ← STM32固件（Keil工程）
├── 下位机硬件设计/          ← 硬件设计文件
└── .workbuddy/
    └── skills/
        └── ai-indicator/
            └── SKILL.md    ← Agent应用Skill文件
```

## 技术栈

- **GUI**：tkinter（深色主题）
- **串口通信**：pyserial（自定义协议帧）
- **API服务**：Flask
- **Python版本**：3.7+

## 更新日志

### v1.1 (2026-06-30)
- 移除波特率设置，固定115200
- GUI重新设计为现代化深色主题
- 红灯改为"故障/异常"（不再用"权限"命名）
- 通信协议升级为带校验和的帧格式
- 新增蜂鸣器控制（音量+时长）

### v1.0 (2026-06-30)
- 初始版本
