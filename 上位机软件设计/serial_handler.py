"""
串口通信模块 - 负责与AI指示灯硬件通信
使用自定义协议，包含校验和
"""

import serial
import serial.tools.list_ports
from typing import Optional, List


class SerialHandler:
    """串口处理器，负责打开发送指令
    
    通信协议：
    - 帧格式：[起始位 0xAA][命令字 1字节][数据长度 1字节][数据 N字节][校验和 1字节]
    - 校验和：从起始位到数据结束所有字节的异或（XOR）
    
    命令字定义：
    - 0x01: 绿灯（AI空闲）
    - 0x02: 黄灯（AI思考）
    - 0x03: 红灯（故障/异常）
    - 0x04: 关闭灯光
    - 0x05: 蜂鸣器设置（数据：[音量 1字节][时长 1字节]）
    """

    # 命令字
    CMD_GREEN = 0x01      # 绿灯
    CMD_YELLOW = 0x02     # 黄灯
    CMD_RED = 0x03        # 红灯
    CMD_OFF = 0x04         # 关闭
    CMD_BUZZER = 0x05     # 蜂鸣器设置

    # 起始位
    START_BYTE = 0xAA

    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False

    def get_available_ports(self) -> List[str]:
        """获取可用的串口列表"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """
        连接串口

        Args:
            port: 串口名称 (如 COM3)
            baudrate: 波特率，固定为115200

        Returns:
            bool: 连接是否成功
        """
        try:
            if self.is_connected:
                self.disconnect()

            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接串口失败: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False

    def _calculate_checksum(self, data: bytes) -> int:
        """
        计算校验和（XOR异或）

        Args:
            data: 待计算的数据字节

        Returns:
            int: 校验和
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def _build_frame(self, command: int, data: bytes = b'') -> bytes:
        """
        构建通信帧

        Args:
            command: 命令字
            data: 数据字节（可选）

        Returns:
            bytes: 完整的通信帧
        """
        # 起始位
        frame = bytes([self.START_BYTE])

        # 命令字
        frame += bytes([command])

        # 数据长度
        data_len = len(data)
        frame += bytes([data_len])

        # 数据
        if data_len > 0:
            frame += data

        # 校验和（从起始位到数据结束所有字节的XOR）
        checksum = self._calculate_checksum(frame)
        frame += bytes([checksum])

        return frame

    def send_command(self, command: int, data: bytes = b'') -> bool:
        """
        发送指令到串口

        Args:
            command: 命令字
            data: 数据字节（可选）

        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected or not self.serial_port:
            print("串口未连接")
            return False

        try:
            frame = self._build_frame(command, data)
            print(f"发送帧: {frame.hex(' ')}")
            self.serial_port.write(frame)
            return True
        except Exception as e:
            print(f"发送指令失败: {e}")
            return False

    def set_green(self) -> bool:
        """设置绿灯（AI空闲）"""
        return self.send_command(self.CMD_GREEN)

    def set_yellow(self) -> bool:
        """设置黄灯（AI思考）"""
        return self.send_command(self.CMD_YELLOW)

    def set_red(self) -> bool:
        """设置红灯（故障/异常）"""
        return self.send_command(self.CMD_RED)

    def turn_off(self) -> bool:
        """关闭灯光"""
        return self.send_command(self.CMD_OFF)

    def set_buzzer(self, volume: int, duration: int) -> bool:
        """
        设置蜂鸣器

        Args:
            volume: 音量 (0-100)
            duration: 时长 (秒, 0-60)

        Returns:
            bool: 发送是否成功
        """
        # 限制范围
        volume = max(0, min(100, volume))
        duration = max(0, min(60, duration))

        # 数据格式：[音量 1字节][时长 1字节]
        data = bytes([volume, duration])
        return self.send_command(self.CMD_BUZZER, data)

    def get_status(self) -> dict:
        """获取当前连接状态"""
        return {
            'is_connected': self.is_connected,
            'port': self.serial_port.port if self.serial_port else None,
            'baudrate': self.serial_port.baudrate if self.serial_port else None
        }
