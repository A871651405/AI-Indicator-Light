"""
串口通信模块 - 负责与AI指示灯硬件通信
使用自定义协议，包含校验和
"""

import re
import serial
import serial.tools.list_ports
from typing import Optional, List, Dict


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
    CMD_READ_PARAMS = 0x06  # 读取下位机参数

    # 起始位
    START_BYTE = 0xAA

    # 常见 USB 转串口芯片 VID:PID 映射表
    # key: (VID, PID) 大写十六进制字符串
    USB_SERIAL_CHIPS: Dict[tuple, str] = {
        # WCH 沁恒 - CH340 / CH341
        ('1A86', '7523'): 'CH340',
        ('1A86', '5523'): 'CH341',
        ('1A86', '7522'): 'CH340N',
        # Silicon Labs - CP210x
        ('10C4', 'EA60'): 'CP2102',
        ('10C4', 'EA61'): 'CP2104',
        ('10C4', 'EA62'): 'CP2105',
        ('10C4', 'EA63'): 'CP2108',
        ('10C4', 'EA70'): 'CP2105',
        # FTDI - FT232 系列
        ('0403', '6001'): 'FT232R',
        ('0403', '6014'): 'FT232H',
        ('0403', '6015'): 'FT231X',
        ('0403', '6010'): 'FT2232C',
        ('0403', '6011'): 'FT4232H',
        # Prolific - PL2303
        ('067B', '2303'): 'PL2303',
        ('067B', '23A3'): 'PL2303TA',
        ('067B', '23C3'): 'PL2303RA',
        ('067B', '23D3'): 'PL2303SA',
        # STMicroelectronics - STM32 USB CDC (虚拟串口)
        ('0483', '5740'): 'STM32-CDC',
        # Arduino UNO R3 (ATmega16U2)
        ('2341', '0043'): 'Arduino-UNO',
        ('2341', '0001'): 'Arduino-UNO',
        # Cypress
        ('04B4', '0002'): 'CY7C64225',
    }

    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False

    def get_available_ports(self) -> List[str]:
        """获取可用的串口列表（仅设备名，向后兼容）"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def _parse_vid_pid(self, hwid: str) -> Optional[tuple]:
        """
        从 hwid 字符串中解析 VID 和 PID

        hwid 示例: 'USB VID:PID=1A86:7523 SER=5&1A2B3C4D LOCATION=1-2'
                   'PCI VID:PID=1A86:7523 ...'

        Returns:
            (VID, PID) 大写十六进制字符串元组，解析失败返回 None
        """
        if not hwid:
            return None
        match = re.search(r'VID:PID=([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})', hwid)
        if match:
            return (match.group(1).upper(), match.group(2).upper())
        return None

    def _identify_chip(self, port) -> str:
        """
        识别串口对应的 USB 芯片型号

        优先级：
        1. VID:PID 精确匹配映射表
        2. 从 description/product 中提取更精确的型号（如 CH340K）
        3. description/product 关键字推断
        4. 返回 '未知'

        Args:
            port: serial.tools.list_ports.ListPortInfo 对象

        Returns:
            芯片型号字符串
        """
        # 1. 尝试 VID:PID 匹配
        vid_pid = self._parse_vid_pid(port.hwid)
        chip_from_vid = None
        if vid_pid:
            chip_from_vid = self.USB_SERIAL_CHIPS.get(vid_pid)

        # 收集所有描述文本（大写）
        text = ' '.join(filter(None, [getattr(port, 'product', None),
                                       getattr(port, 'description', None),
                                       getattr(port, 'manufacturer', None)]))
        text_upper = text.upper() if text else ''

        # 2. 如果 VID 命中了，尝试从描述里提取更精确的型号
        #    （例如 VID 是 WCH 1A86，映射表给 CH340，但描述里有 CH340K，就用 CH340K）
        if chip_from_vid:
            # CH340/CH341 系列尝试提取带后缀的精确型号
            if chip_from_vid.startswith('CH34'):
                m = re.search(r'(CH34[01][A-Z]?)', text_upper)
                if m:
                    return m.group(1)
            if chip_from_vid.startswith('CP210'):
                m = re.search(r'(CP210[0-9])', text_upper)
                if m:
                    return m.group(1)
            if chip_from_vid.startswith('FT232') or chip_from_vid.startswith('FT231') \
               or chip_from_vid.startswith('FT2232') or chip_from_vid.startswith('FT4232'):
                m = re.search(r'(FT23[0-9][A-Z]?|FT2232[A-Z]?|FT4232[A-Z]?)', text_upper)
                if m:
                    return m.group(1)
            # 没有更精确的就返回映射表的值
            return chip_from_vid

        # 3. VID 没命中，用关键字推断
        if 'CH340' in text_upper or 'CH341' in text_upper:
            m = re.search(r'(CH34[01][A-Z]?)', text_upper)
            return m.group(1) if m else 'CH340/CH341'
        if 'CP210' in text_upper:
            m = re.search(r'(CP210[0-9])', text_upper)
            return m.group(1) if m else 'CP210x'
        if 'FT232' in text_upper or 'FT231' in text_upper \
           or 'FT2232' in text_upper or 'FT4232' in text_upper:
            m = re.search(r'(FT23[0-9][A-Z]?|FT2232[A-Z]?|FT4232[A-Z]?)', text_upper)
            return m.group(1) if m else 'FT232x'
        if 'PL2303' in text_upper:
            return 'PL2303'

        # 4. 未知芯片
        return '未知'

    def get_available_ports_with_info(self) -> List[Dict[str, str]]:
        """
        获取可用的串口列表（含芯片信息）

        Returns:
            列表，每项为 dict:
            {
                'device': 'COM3',                  # 串口设备名
                'chip': 'CH340',                   # USB 芯片型号
                'description': 'USB-SERIAL CH340', # 系统描述
                'display': 'COM3 (CH340)'          # 下拉框显示文本
            }
        """
        ports = serial.tools.list_ports.comports()
        result = []
        for port in ports:
            chip = self._identify_chip(port)
            display = f"{port.device} ({chip})"
            result.append({
                'device': port.device,
                'chip': chip,
                'description': port.description or '',
                'display': display
            })
        return result

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

    def set_buzzer(self, volume: int, duration: int, enabled: bool = True) -> bool:
        """
        设置蜂鸣器（音量、时长、启用标志）

        Args:
            volume: 音量 (0-100)
            duration: 时长 (秒, 0-60)
            enabled: 启用标志 (True=启用, False=关闭)

        Returns:
            bool: 发送是否成功
        """
        # 限制范围
        volume = max(0, min(100, volume))
        duration = max(0, min(60, duration))

        # 数据格式：[音量 1字节][时长 1字节][启用标志 1字节]
        data = bytes([volume, duration, 1 if enabled else 0])
        return self.send_command(self.CMD_BUZZER, data)

    def get_status(self) -> dict:
        """获取当前连接状态"""
        return {
            'is_connected': self.is_connected,
            'port': self.serial_port.port if self.serial_port else None,
            'baudrate': self.serial_port.baudrate if self.serial_port else None
        }

    def read_params(self, timeout: float = 0.5) -> Optional[tuple]:
        """
        读取下位机保存的蜂鸣器参数（音量、时长、启用标志）

        发送 CMD_READ_PARAMS 命令，下位机返回数据帧：
            [0xAA][0x06][0x03][volume][duration][enabled][checksum]

        Args:
            timeout: 读取响应超时时间（秒）

        Returns:
            (volume, duration, enabled) 元组，读取失败返回 None
        """
        if not self.is_connected or not self.serial_port:
            return None

        try:
            # 清空接收缓冲区，避免残留数据干扰
            self.serial_port.reset_input_buffer()

            # 发送读取参数命令帧
            frame = self._build_frame(self.CMD_READ_PARAMS)
            self.serial_port.write(frame)

            # 设置临时超时
            old_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout

            # 查找起始位 0xAA（最多读 20 个字节）
            start_found = False
            for _ in range(20):
                byte = self.serial_port.read(1)
                if not byte:
                    break
                if byte == bytes([self.START_BYTE]):
                    start_found = True
                    break

            if not start_found:
                self.serial_port.timeout = old_timeout
                return None

            # 读取剩余 6 字节：命令字 + 数据长度 + 3字节数据 + 校验和
            remaining = self.serial_port.read(6)
            self.serial_port.timeout = old_timeout

            if len(remaining) < 6:
                return None

            # 组装完整帧
            response = bytes([self.START_BYTE]) + remaining

            # 解析帧
            cmd = response[1]
            data_len = response[2]
            if cmd != self.CMD_READ_PARAMS or data_len != 3:
                return None

            volume = response[3]
            duration = response[4]
            enabled = bool(response[5])
            checksum = response[6]

            # 验证校验和
            calc_checksum = self._calculate_checksum(response[:6])
            if calc_checksum != checksum:
                print(f"校验和失败: 计算={calc_checksum:#x}, 接收={checksum:#x}")
                return None

            return (volume, duration, enabled)

        except Exception as e:
            print(f"读取参数失败: {e}")
            return None
