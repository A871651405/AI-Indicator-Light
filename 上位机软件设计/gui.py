"""
GUI界面模块 - 提供美观简洁的用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from serial_handler import SerialHandler
from api_server import APIServer


class AIIndicatorGUI:
    """AI指示灯GUI界面 - 现代化设计"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI指示灯控制器 v1.1")
        self.root.geometry("750x650")
        self.root.configure(bg='#f0f2f5')
        self.root.resizable(True, True)

        self.serial_handler = SerialHandler()
        self.api_server = None
        self.api_thread = None

        # 颜色定义 - 浅色主题
        self.colors = {
            'bg_primary': '#f0f2f5',      # 主背景 - 浅灰
            'bg_secondary': '#ffffff',     # 卡片背景 - 白色
            'bg_card': '#e8ecf0',          # 输入框/状态栏背景 - 浅灰
            'accent': '#e94560',           # 强调红 - 保存按钮
            'accent_green': '#00b894',     # 绿色强调
            'accent_yellow': '#f39c12',    # 黄色强调
            'accent_red': '#e74c3c',       # 红色强调
            'text_primary': '#2c3e50',     # 主文字 - 深蓝灰
            'text_secondary': '#7f8c8d',   # 次文字 - 灰
            'text_on_color': '#ffffff',    # 彩色按钮上的文字 - 白色
            'success': '#27ae60',          # 成功绿 (深一点,白底可读)
            'warning': '#f39c12',          # 警告黄
            'danger': '#e74c3c',           # 危险红
            'log_text': '#2c3e50'          # 日志文字 - 深色
        }

        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # 标题区域
        self.create_header(main_container)

        # 内容区域（左右分栏）
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))

        # 左侧：串口配置 + 灯光控制
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.create_serial_section(left_frame)
        self.create_light_control(left_frame)

        # 右侧：蜂鸣器设置 + API服务 + 日志
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))

        self.create_buzzer_section(right_frame)
        self.create_api_section(right_frame)
        self.create_log_section(right_frame)

        # 状态栏
        self.create_status_bar()

        # 初始刷新串口（在所有UI组件创建完成后）
        self.refresh_ports()

    def create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # 标题
        title_label = tk.Label(
            header_frame,
            text="🤖 AI 指示灯控制器",
            font=('微软雅黑', 18, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=15)

        # 副标题
        subtitle_label = tk.Label(
            header_frame,
            text="AI Indicator Controller v1.1",
            font=('Consolas', 9),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack()

    def create_serial_section(self, parent):
        """创建串口配置区域"""
        frame = tk.LabelFrame(
            parent,
            text="📡 串口配置",
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_green'],
            padx=15,
            pady=15,
            relief='groove',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))

        # 串口选择行
        port_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        port_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            port_frame,
            text="串口:",
            font=('微软雅黑', 9),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            width=8,
            anchor='w'
        ).pack(side='left')

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            port_frame,
            textvariable=self.port_var,
            width=20,
            state='readonly',
            font=('微软雅黑', 9)
        )
        self.port_combo.pack(side='left', padx=(10, 10))

        refresh_btn = tk.Button(
            port_frame,
            text="🔄",
            command=self.refresh_ports,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            font=('微软雅黑', 10),
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            relief='flat'
        )
        refresh_btn.pack(side='left')

        # 连接按钮
        self.connect_btn = tk.Button(
            frame,
            text="📡 连接串口",
            command=self.toggle_connection,
            bg=self.colors['success'],
            fg=self.colors['text_on_color'],
            font=('微软雅黑', 10, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            relief='flat',
            activebackground=self.colors['accent_green']
        )
        self.connect_btn.pack(pady=(5, 0))

    def create_light_control(self, parent):
        """创建灯光控制区域"""
        frame = tk.LabelFrame(
            parent,
            text="💡 灯光控制",
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_yellow'],
            padx=15,
            pady=15,
            relief='groove',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))

        # 按钮容器
        btn_container = tk.Frame(frame, bg=self.colors['bg_secondary'])
        btn_container.pack(pady=10)

        # 自定义按钮样式
        button_configs = [
            {
                'text': '🟢 空闲',
                'color': self.colors['success'],
                'hover': '#1e8449',
                'command': lambda: self.send_light_command('green')
            },
            {
                'text': '🟡 思考',
                'color': self.colors['warning'],
                'hover': '#d68910',
                'command': lambda: self.send_light_command('yellow')
            },
            {
                'text': '🔴 故障',
                'color': self.colors['danger'],
                'hover': '#c0392b',
                'command': lambda: self.send_light_command('red')
            },
            {
                'text': '⚫ 关闭',
                'color': '#95a5a6',
                'hover': '#7f8c8d',
                'command': lambda: self.send_light_command('off')
            }
        ]

        for i, config in enumerate(button_configs):
            btn = tk.Button(
                btn_container,
                text=config['text'],
                command=config['command'],
                bg=config['color'],
                fg=self.colors['text_on_color'],
                font=('微软雅黑', 10, 'bold'),
                bd=0,
                padx=20,
                pady=12,
                cursor='hand2',
                relief='flat',
                width=12
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)

            # 绑定鼠标悬停效果
            btn.bind('<Enter>', lambda e, b=btn, c=config['hover']: b.configure(bg=c))
            btn.bind('<Leave>', lambda e, b=btn, c=config['color']: b.configure(bg=c))

    def create_buzzer_section(self, parent):
        """创建蜂鸣器设置区域"""
        frame = tk.LabelFrame(
            parent,
            text="🔊 蜂鸣器设置",
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent'],
            padx=15,
            pady=15,
            relief='groove',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))

        # 音量控制
        volume_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        volume_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            volume_frame,
            text="音量:",
            font=('微软雅黑', 9),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        ).pack(anchor='w')

        self.volume_var = tk.IntVar(value=50)
        self.volume_scale = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient='horizontal',
            variable=self.volume_var,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            troughcolor=self.colors['bg_card'],
            activebackground=self.colors['accent'],
            font=('微软雅黑', 8),
            length=200
        )
        self.volume_scale.pack(fill='x', pady=(5, 0))

        # 时间设置
        time_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        time_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            time_frame,
            text="响铃时长 (秒):",
            font=('微软雅黑', 9),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        ).pack(anchor='w')

        time_input_frame = tk.Frame(time_frame, bg=self.colors['bg_secondary'])
        time_input_frame.pack(fill='x', pady=(5, 0))

        self.time_var = tk.StringVar(value="5")
        self.time_entry = tk.Entry(
            time_input_frame,
            textvariable=self.time_var,
            font=('Consolas', 10),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent'],
            bd=0,
            relief='flat',
            width=10
        )
        self.time_entry.pack(side='left', padx=(0, 10))

        tk.Label(
            time_input_frame,
            text="秒 (0-60)",
            font=('微软雅黑', 8),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        ).pack(side='left')

        # 保存按钮
        save_btn = tk.Button(
            frame,
            text="💾 保存到设备",
            command=self.save_buzzer_settings,
            bg=self.colors['accent'],
            fg=self.colors['text_primary'],
            font=('微软雅黑', 10, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            relief='flat',
            activebackground='#d63447'
        )
        save_btn.pack(pady=(5, 0))

    def create_api_section(self, parent):
        """创建API服务区域"""
        frame = tk.LabelFrame(
            parent,
            text="🌐 API服务",
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_green'],
            padx=15,
            pady=15,
            relief='groove',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))

        # API开关
        self.api_var = tk.BooleanVar()
        api_check = tk.Checkbutton(
            frame,
            text="启用API服务 (供Agent调用)",
            variable=self.api_var,
            command=self.toggle_api,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('微软雅黑', 9),
            selectcolor=self.colors['bg_card'],
            activebackground=self.colors['bg_secondary'],
            activeforeground=self.colors['text_primary']
        )
        api_check.pack(anchor='w')

        # API地址显示
        self.api_label = tk.Label(
            frame,
            text="",
            font=('Consolas', 8),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        self.api_label.pack(anchor='w', pady=(5, 0))

    def create_log_section(self, parent):
        """创建日志区域"""
        frame = tk.LabelFrame(
            parent,
            text="📋 运行日志",
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            padx=15,
            pady=15,
            relief='groove',
            bd=2
        )
        frame.pack(fill='both', expand=True)

        # 创建文本框和滚动条
        text_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        text_frame.pack(fill='both', expand=True)

        self.log_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=('Consolas', 8),
            bg=self.colors['bg_primary'],
            fg=self.colors['log_text'],
            insertbackground=self.colors['accent'],
            bd=0,
            relief='flat'
        )
        self.log_text.pack(fill='both', expand=True)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_card'], height=35)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_bar,
            text="⚪ 未连接",
            font=('微软雅黑', 9),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(pady=8)

    def refresh_ports(self):
        """刷新串口列表"""
        ports = self.serial_handler.get_available_ports()
        
        # 排序串口（从小到大，COM1, COM2, COM3...）
        def sort_key(port):
            import re
            # 提取COM端口的编号（如 COM3 -> 3）
            match = re.search(r'COM(\d+)', port, re.IGNORECASE)
            if match:
                return (0, int(match.group(1)))  # COM端口：按编号数值排序
            return (1, port)  # 非COM端口：按字母排序
        
        ports.sort(key=sort_key)
        
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
        self.log(f"刷新串口列表: {len(ports)} 个可用")

    def toggle_connection(self):
        """切换连接状态"""
        if self.serial_handler.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        """连接串口"""
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("警告", "请选择串口")
            return

        # 使用固定波特率 115200
        if self.serial_handler.connect(port, 115200):
            self.connect_btn.configure(text="📡 断开连接", bg=self.colors['danger'])
            self.status_label.configure(text=f"🟢 已连接: {port} @ 115200")
            self.log(f"✓ 成功连接串口: {port}")
        else:
            messagebox.showerror("错误", "连接串口失败")

    def disconnect_serial(self):
        """断开串口"""
        self.serial_handler.disconnect()
        self.connect_btn.configure(text="📡 连接串口", bg=self.colors['success'])
        self.status_label.configure(text="⚪ 未连接")
        self.log("✓ 已断开串口连接")

    def send_light_command(self, color: str):
        """发送灯光控制指令"""
        if not self.serial_handler.is_connected:
            messagebox.showwarning("警告", "请先连接串口")
            return

        success = False
        if color == 'green':
            success = self.serial_handler.set_green()
            self.log("🟢 发送指令: 绿灯 (AI空闲)")
        elif color == 'yellow':
            success = self.serial_handler.set_yellow()
            self.log("🟡 发送指令: 黄灯 (AI思考)")
        elif color == 'red':
            success = self.serial_handler.set_red()
            self.log("🔴 发送指令: 红灯 (故障/异常)")
        elif color == 'off':
            success = self.serial_handler.turn_off()
            self.log("⚫ 发送指令: 关闭灯光")

        if not success:
            messagebox.showerror("错误", "发送指令失败")

    def save_buzzer_settings(self):
        """保存蜂鸣器设置到下位机"""
        if not self.serial_handler.is_connected:
            messagebox.showwarning("警告", "请先连接串口")
            return

        # 验证时间输入
        try:
            time_val = int(self.time_var.get())
            if time_val < 0 or time_val > 60:
                messagebox.showerror("错误", "时间必须在0-60秒之间")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        volume = self.volume_var.get()
        self.log(f"🔊 保存蜂鸣器设置: 音量={volume}, 时长={time_val}s")

        success = self.serial_handler.set_buzzer(volume, time_val)
        if success:
            self.log("✓ 蜂鸣器设置已发送到设备")
            messagebox.showinfo("成功", "设置已保存到设备")
        else:
            messagebox.showerror("错误", "发送设置失败")

    def toggle_api(self):
        """切换API服务状态"""
        if self.api_var.get():
            self.start_api()
        else:
            self.stop_api()

    def start_api(self):
        """启动API服务"""
        if self.api_server:
            return

        try:
            self.api_server = APIServer(self.serial_handler)
            self.api_thread = threading.Thread(
                target=self.api_server.run,
                kwargs={'host': '127.0.0.1', 'port': 5000},
                daemon=True
            )
            self.api_thread.start()

            api_url = "http://127.0.0.1:5000"
            self.api_label.configure(text=f"API: {api_url}")
            self.log(f"✓ API服务已启动: {api_url}")

        except Exception as e:
            self.log(f"✗ API服务启动失败: {e}")
            self.api_var.set(False)

    def stop_api(self):
        """停止API服务"""
        if self.api_server:
            self.api_server = None
            self.api_label.configure(text="")
            self.log("✓ API服务已停止")

    def log(self, message: str):
        """添加日志"""
        # 安全检查：如果log_text还未创建，直接返回
        if not hasattr(self, 'log_text') or not self.log_text:
            return
            
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

        # 限制日志行数
        lines = self.log_text.get('1.0', tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete('1.0', f'{len(lines)-50}.0')

    def on_closing(self):
        """窗口关闭时的处理"""
        if self.serial_handler.is_connected:
            self.serial_handler.disconnect()
        if self.api_server:
            self.stop_api()
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = AIIndicatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
