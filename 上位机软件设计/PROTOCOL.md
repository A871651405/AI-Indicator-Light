# AI指示灯通信协议 v1.1

## 协议概述

本软件使用自定义二进制协议与下位机（单片机）通信，包含校验机制确保数据可靠性。

---

## 帧格式

```
| 起始位 | 命令字 | 数据长度 | 数据 | 校验和 |
|---------|--------|----------|------|--------|
| 1字节  | 1字节 | 1字节   | N字节 | 1字节 |
```

### 字段说明

| 字段 | 长度 | 说明 |
|------|------|------|
| 起始位 | 1字节 | 固定为 `0xAA` |
| 命令字 | 1字节 | 指定要执行的操作 |
| 数据长度 | 1字节 | 数据字段的字节数（0-255） |
| 数据 | N字节 | 可选，根据命令字确定内容 |
| 校验和 | 1字节 | 从起始位到数据结束所有字节的 **XOR（异或）** |

---

## 命令字定义

| 命令字 | 值 | 说明 | 数据 |
|--------|-----|------|------|
| `CMD_GREEN` | `0x01` | 点亮绿灯（AI空闲） | 无 |
| `CMD_YELLOW` | `0x02` | 点亮黄灯（AI思考） | 无 |
| `CMD_RED` | `0x03` | 点亮红灯（故障/异常） | 无 |
| `CMD_OFF` | `0x04` | 关闭灯光 | 无 |
| `CMD_BUZZER` | `0x05` | 设置蜂鸣器 | [音量, 时长] |

---

## 校验和计算

**算法**：XOR（异或）

**计算范围**：从起始位到数据字段的最后一个字节

**示例**：
```
帧：0xAA 0x01 0x00 0xAB
计算：0xAA ^ 0x01 ^ 0x00 = 0xAB
```

---

## 命令详解

### 1. 点亮绿灯（AI空闲）

**命令字**：`0x01`

**数据**：无（数据长度 = 0）

**完整帧**：
```
0xAA 0x01 0x00 0xAA
```

**说明**：
- 起始位：`0xAA`
- 命令字：`0x01`
- 数据长度：`0x00`（无数据）
- 校验和：`0xAA ^ 0x01 ^ 0x00 = 0xAA`

---

### 2. 点亮黄灯（AI思考）

**命令字**：`0x02`

**数据**：无

**完整帧**：
```
0xAA 0x02 0x00 0xA8
```

**校验和计算**：`0xAA ^ 0x02 ^ 0x00 = 0xA8`

---

### 3. 点亮红灯（故障/异常）

**命令字**：`0x03`

**数据**：无

**完整帧**：
```
0xAA 0x03 0x00 0xAB
```

**校验和计算**：`0xAA ^ 0x03 ^ 0x00 = 0xAB`

---

### 4. 关闭灯光

**命令字**：`0x04`

**数据**：无

**完整帧**：
```
0xAA 0x04 0x00 0xAE
```

**校验和计算**：`0xAA ^ 0x04 ^ 0x00 = 0xAE`

---

### 5. 设置蜂鸣器

**命令字**：`0x05`

**数据**：2字节
- 字节1：音量（0-100）
- 字节2：时长（秒，0-60）

**示例**：设置音量为80，时长为10秒

**完整帧**：
```
0xAA 0x05 0x02 0x50 0x0A 0xFD
```

**字段解析**：
- 起始位：`0xAA`
- 命令字：`0x05`
- 数据长度：`0x02`（2字节数据）
- 数据：`0x50`（音量80）、`0x0A`（时长10秒）
- 校验和：`0xAA ^ 0x05 ^ 0x02 ^ 0x50 ^ 0x0A = 0xFD`

---

## 下位机实现指南

### 单片机端解析流程

1. **等待起始位**：持续读取串口，直到收到 `0xAA`
2. **读取命令字**：读取1字节
3. **读取数据长度**：读取1字节（N）
4. **读取数据**：根据N读取对应字节数
5. **读取校验和**：读取1字节
6. **验证校验和**：重新计算校验和并与接收到的比较
7. **执行命令**：根据命令字执行对应操作

### 伪代码（C语言）

```c
#define START_BYTE 0xAA
#define CMD_GREEN 0x01
#define CMD_YELLOW 0x02
#define CMD_RED 0x03
#define CMD_OFF 0x04
#define CMD_BUZZER 0x05

void parse_frame() {
    uint8_t byte;
    uint8_t frame[64];
    uint8_t idx = 0;
    
    // 等待起始位
    while (1) {
        if (Serial.available()) {
            byte = Serial.read();
            if (byte == START_BYTE) {
                frame[idx++] = byte;
                break;
            }
        }
    }
    
    // 读取命令字
    while (!Serial.available());
    frame[idx++] = Serial.read();
    
    // 读取数据长度
    while (!Serial.available());
    uint8_t data_len = Serial.read();
    frame[idx++] = data_len;
    
    // 读取数据
    for (int i = 0; i < data_len; i++) {
        while (!Serial.available());
        frame[idx++] = Serial.read();
    }
    
    // 读取校验和
    while (!Serial.available());
    uint8_t received_checksum = Serial.read();
    
    // 计算校验和
    uint8_t calculated_checksum = 0;
    for (int i = 0; i < idx; i++) {
        calculated_checksum ^= frame[i];
    }
    
    // 验证校验和
    if (calculated_checksum != received_checksum) {
        // 校验失败，发送错误响应
        Serial.write(0xFF);  // 错误标志
        return;
    }
    
    // 执行命令
    uint8_t cmd = frame[1];
    switch (cmd) {
        case CMD_GREEN:
            // 点亮绿灯
            digitalWrite(GREEN_LED_PIN, HIGH);
            digitalWrite(YELLOW_LED_PIN, LOW);
            digitalWrite(RED_LED_PIN, LOW);
            break;
            
        case CMD_YELLOW:
            // 点亮黄灯
            digitalWrite(GREEN_LED_PIN, LOW);
            digitalWrite(YELLOW_LED_PIN, HIGH);
            digitalWrite(RED_LED_PIN, LOW);
            break;
            
        case CMD_RED:
            // 点亮红灯
            digitalWrite(GREEN_LED_PIN, LOW);
            digitalWrite(YELLOW_LED_PIN, LOW);
            digitalWrite(RED_LED_PIN, HIGH);
            break;
            
        case CMD_OFF:
            // 关闭所有灯
            digitalWrite(GREEN_LED_PIN, LOW);
            digitalWrite(YELLOW_LED_PIN, LOW);
            digitalWrite(RED_LED_PIN, LOW);
            break;
            
        case CMD_BUZZER:
            // 设置蜂鸣器
            uint8_t volume = frame[3];  // 数据起始位置
            uint8_t duration = frame[4];
            // 设置PWM控制蜂鸣器音量
            analogWrite(BUZZER_PIN, (volume * 255) / 100);
            delay(duration * 1000);
            analogWrite(BUZZER_PIN, 0);
            break;
    }
    
    // 发送成功响应
    Serial.write(0x00);  // 成功标志
}
```

---

## API调用示例

### 点亮绿灯

```bash
curl -X POST http://127.0.0.1:5000/api/light/green
```

### 点亮黄灯

```bash
curl -X POST http://127.0.0.1:5000/api/light/yellow
```

### 点亮红灯

```bash
curl -X POST http://127.0.0.1:5000/api/light/red
```

### 关闭灯光

```bash
curl -X POST http://127.0.0.1:5000/api/light/off
```

### 设置蜂鸣器

```bash
curl -X POST http://127.0.0.1:5000/api/buzzer \
  -H "Content-Type: application/json" \
  -d '{"volume": 80, "duration": 10}'
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-06-30 | 初始版本，使用单字节指令 |
| v1.1 | 2026-06-30 | 改为协议帧格式，加入校验和，新增蜂鸣器控制 |

---

**作者**：AI Assistant  
**日期**：2026-06-30
