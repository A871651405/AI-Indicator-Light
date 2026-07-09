"""
PyQt5 现代化 GUI 界面模块

特性：
- 现代简洁卡片式布局
- 浅色/深色双主题运行时切换
- 串口下拉框显示芯片型号
- 蜂鸣器拨动开关
- 系统托盘（关闭时可选最小化到托盘）
- 自定义应用图标
- 完整功能：串口配置、灯光控制、蜂鸣器设置、API服务、日志
"""

import re
import os
import datetime
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit, QSlider,
    QCheckBox, QTextEdit, QFrame, QGroupBox, QSizePolicy, QScrollArea,
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QSize
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPixmap, QPainter, QColor, QBrush

from serial_handler import SerialHandler
from api_server import APIServer
from theme import ThemeManager, FONT_FAMILY, FONT_MONO


# ============================================================
# 自定义拨动开关组件（iOS 风格）
# ============================================================

class ToggleSwitch(QWidget):
    """iOS 风格拨动开关，支持主题色自适应"""

    toggled = pyqtSignal(bool)

    def __init__(self, theme_manager: ThemeManager, checked: bool = False, parent=None):
        super().__init__(parent)
        self._theme = theme_manager
        self._checked = checked
        self.setFixedSize(46, 26)
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(checked)
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

    def paintEvent(self, event):
        t = self._theme.current
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 轨道
        track = QColor(t['success']) if self._checked else QColor(t['border'])
        painter.setBrush(QBrush(track))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 46, 26, 13, 13)
        # 滑块
        x = 23 if self._checked else 3
        painter.setBrush(QBrush(QColor(t['surface'])))
        painter.drawEllipse(x, 3, 20, 20)


# ============================================================
# 信号桥：把子线程的日志/状态更新转发到主线程
# ============================================================

class _Signals(QObject):
    """跨线程信号集合"""
    log = pyqtSignal(str)
    status = pyqtSignal(str, str)   # (text, color_key)
    api_state = pyqtSignal(bool, str)  # (running, url)
    params_ready = pyqtSignal(int, int, bool)  # (volume, duration, enabled) 参数读取完成


# ============================================================
# 主窗口
# ============================================================

class AIIndicatorGUI(QMainWindow):
    """AI 指示灯控制器 - PyQt5 现代化界面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 指示灯控制器")
        self.resize(920, 700)
        self.setMinimumSize(860, 640)

        # 业务对象
        self.serial_handler = SerialHandler()
        self.api_server = None
        self.api_thread = None
        self._ports_info = {}  # display_text -> info dict

        # 主题
        self.theme = ThemeManager()

        # 跨线程信号
        self.signals = _Signals()
        self.signals.log.connect(self._append_log)
        self.signals.status.connect(self._apply_status)
        self.signals.api_state.connect(self._apply_api_state)
        self.signals.params_ready.connect(self._apply_params)

        # 构建 UI
        self._build_ui()
        # 设置窗口图标
        self._set_window_icon()
        # 应用初始主题
        self.theme.apply(QApplication.instance())
        # 初始化系统托盘
        self._init_tray()
        # 初始刷新串口
        self.refresh_ports()

    # ============================================================
    # UI 构建
    # ============================================================

    def _build_ui(self):
        """构建整体界面"""
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 12)
        root.setSpacing(16)

        # 顶部标题栏（含主题切换）
        root.addWidget(self._build_header())

        # 内容区（左右分栏）
        content = QHBoxLayout()
        content.setSpacing(16)

        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        left_col.addWidget(self._build_serial_card())
        left_col.addWidget(self._build_light_card())
        left_col.addStretch(1)
        content.addLayout(left_col, 1)

        # 右侧：可滚动区域（蜂鸣器+API+日志）
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        right_scroll.setFrameShape(QScrollArea.NoFrame)
        right_scroll.setProperty('class', 'ScrollArea')  # 可被 QSS 选中

        right_widget = QWidget()
        right_col = QVBoxLayout(right_widget)
        right_col.setSpacing(16)
        right_col.setContentsMargins(0, 0, 8, 0)
        right_col.addWidget(self._build_buzzer_card())
        right_col.addWidget(self._build_api_card())
        right_col.addWidget(self._build_log_card(), 1)
        right_col.addStretch(0)

        right_scroll.setWidget(right_widget)
        content.addWidget(right_scroll, 1)

        root.addLayout(content, 1)

        # 底部状态栏
        root.addWidget(self._build_status_bar())

    # ---------- 顶部标题栏 ----------

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("CardFrame")
        h = QHBoxLayout(frame)
        h.setContentsMargins(20, 16, 20, 16)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("🤖 AI 指示灯控制器")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("AI Indicator Controller  ·  PyQt5 Edition")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        h.addLayout(title_box)
        h.addStretch(1)

        # 主题切换按钮
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("IconButton")
        self.theme_btn.setToolTip("切换浅色/深色主题")
        self.theme_btn.setFixedSize(44, 36)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        h.addWidget(self.theme_btn)

        return frame

    # ---------- 串口配置卡片 ----------

    def _build_serial_card(self) -> QGroupBox:
        group = QGroupBox("📡 串口配置")
        v = QVBoxLayout(group)
        v.setSpacing(12)

        # 串口选择行
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel("串口")
        lbl.setObjectName("SectionLabel")
        lbl.setFixedWidth(36)
        row.addWidget(lbl)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(260)
        self.port_combo.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.port_combo, 1)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setObjectName("IconButton")
        refresh_btn.setFixedSize(44, 36)
        refresh_btn.setToolTip("刷新串口列表")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_ports)
        row.addWidget(refresh_btn)
        v.addLayout(row)

        # 连接按钮
        self.connect_btn = QPushButton("📡 连接串口")
        self.connect_btn.setObjectName("PrimaryButton")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.toggle_connection)
        v.addWidget(self.connect_btn)

        return group

    # ---------- 灯光控制卡片 ----------

    def _build_light_card(self) -> QGroupBox:
        group = QGroupBox("💡 灯光控制")
        grid = QGridLayout(group)
        grid.setSpacing(10)
        grid.setContentsMargins(16, 28, 16, 16)

        buttons = [
            ("🟢 空闲", "GreenButton", 'green'),
            ("🟡 思考", "YellowButton", 'yellow'),
            ("🔴 故障", "RedButton", 'red'),
            ("⚫ 关闭", "NeutralButton", 'off'),
        ]
        for i, (text, obj_name, color) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, c=color: self.send_light_command(c))
            grid.addWidget(btn, i // 2, i % 2)

        return group

    # ---------- 蜂鸣器设置卡片 ----------

    def _build_buzzer_card(self) -> QGroupBox:
        group = QGroupBox("🔊 蜂鸣器设置")
        group.setMinimumHeight(250)  # 确保所有控件不会被压缩隐藏
        v = QVBoxLayout(group)
        v.setSpacing(12)

        # 顶部：拨动开关 + 标签
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(10)
        toggle_lbl = QLabel("蜂鸣器启用")
        toggle_lbl.setObjectName("SectionLabel")
        toggle_row.addWidget(toggle_lbl)
        toggle_row.addStretch(1)

        self.buzzer_toggle = ToggleSwitch(self.theme, checked=True)
        self.buzzer_toggle.toggled.connect(self._on_buzzer_toggle)
        toggle_row.addWidget(self.buzzer_toggle)

        self.buzzer_status_label = QLabel("已开启")
        self.buzzer_status_label.setObjectName("StatusLabel")
        self.buzzer_status_label.setMinimumWidth(40)
        toggle_row.addWidget(self.buzzer_status_label)
        v.addLayout(toggle_row)

        # 音量
        vol_row = QHBoxLayout()
        vol_lbl = QLabel("音量")
        vol_lbl.setObjectName("SectionLabel")
        vol_lbl.setFixedWidth(48)
        self.volume_value = QLabel("50")
        self.volume_value.setObjectName("SectionLabel")
        self.volume_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vol_row.addWidget(vol_lbl)
        vol_row.addWidget(self.volume_value, 1)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setCursor(Qt.PointingHandCursor)
        self.volume_slider.valueChanged.connect(
            lambda val: self.volume_value.setText(str(val))
        )
        v.addLayout(vol_row)
        v.addWidget(self.volume_slider)

        # 时长
        time_row = QHBoxLayout()
        time_row.setSpacing(8)
        time_lbl = QLabel("响铃时长")
        time_lbl.setObjectName("SectionLabel")
        time_lbl.setFixedWidth(60)
        time_row.addWidget(time_lbl)

        self.time_edit = QLineEdit("5")
        self.time_edit.setFixedWidth(60)
        self.time_edit.setAlignment(Qt.AlignCenter)
        time_row.addWidget(self.time_edit)

        unit = QLabel("秒 (0-60)")
        unit.setObjectName("StatusLabel")
        time_row.addWidget(unit)
        time_row.addStretch(1)
        v.addLayout(time_row)

        # 保存按钮
        self.save_buzzer_btn = QPushButton("💾 保存到设备")
        self.save_buzzer_btn.setObjectName("PrimaryButton")
        self.save_buzzer_btn.setCursor(Qt.PointingHandCursor)
        self.save_buzzer_btn.clicked.connect(self.save_buzzer_settings)
        v.addWidget(self.save_buzzer_btn)

        return group

    def _on_buzzer_toggle(self, checked: bool):
        """拨动开关切换：启用/禁用蜂鸣器"""
        self._update_buzzer_controls(checked)
        state = "启用" if checked else "关闭"
        self._log(f"🔊 蜂鸣器设置已{state}")
        # 如果已连接串口，立即同步开关状态到下位机
        if self.serial_handler.is_connected:
            volume = self.volume_slider.value()
            try:
                duration = max(0, min(60, int(self.time_edit.text())))
            except ValueError:
                duration = 5
            ok = self.serial_handler.set_buzzer(volume, duration, checked)
            if ok:
                self._log(f"📤 蜂鸣器状态已同步到设备：{state}")
            else:
                self._log(f"⚠️ 同步蜂鸣器状态失败")

    def _update_buzzer_controls(self, enabled: bool):
        """更新控件启用状态"""
        self.buzzer_status_label.setText("已开启" if enabled else "已关闭")
        self.volume_slider.setEnabled(enabled)
        self.time_edit.setEnabled(enabled)
        self.save_buzzer_btn.setEnabled(enabled)

    # ---------- API 服务卡片 ----------

    def _build_api_card(self) -> QGroupBox:
        group = QGroupBox("🌐 API 服务")
        v = QVBoxLayout(group)
        v.setSpacing(8)

        self.api_check = QCheckBox("启用 API 服务（供 Agent 调用）")
        self.api_check.setCursor(Qt.PointingHandCursor)
        self.api_check.stateChanged.connect(self._on_api_toggled)
        v.addWidget(self.api_check)

        self.api_label = QLabel("")
        self.api_label.setObjectName("StatusLabel")
        v.addWidget(self.api_label)

        return group

    # ---------- 日志卡片 ----------

    def _build_log_card(self) -> QGroupBox:
        group = QGroupBox("📋 运行日志")
        v = QVBoxLayout(group)
        v.setSpacing(8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(80)
        v.addWidget(self.log_text, 1)  # 日志区域优先占据伸展空间

        return group

    # ---------- 底部状态栏 ----------

    def _build_status_bar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("StatusBar")
        frame.setFixedHeight(34)
        h = QHBoxLayout(frame)
        h.setContentsMargins(16, 0, 16, 0)

        self.status_label = QLabel("⚪ 未连接")
        self.status_label.setObjectName("StatusLabel")
        h.addWidget(self.status_label)
        h.addStretch(1)

        # 右侧主题标识
        self.theme_indicator = QLabel("☀️ 浅色")
        self.theme_indicator.setObjectName("StatusLabel")
        h.addWidget(self.theme_indicator)

        return frame

    # ============================================================
    # 主题切换
    # ============================================================

    def _toggle_theme(self):
        name = self.theme.toggle(QApplication.instance())
        # 更新按钮图标和指示器
        if name == 'dark':
            self.theme_btn.setText("☀️")
            self.theme_indicator.setText("🌙 深色")
        else:
            self.theme_btn.setText("🌙")
            self.theme_indicator.setText("☀️ 浅色")
        # 刷新拨动开关颜色
        if hasattr(self, 'buzzer_toggle'):
            self.buzzer_toggle.update()
        self._log(f"主题已切换至：{('深色' if name == 'dark' else '浅色')}")

    # ============================================================
    # 串口相关
    # ============================================================

    def refresh_ports(self):
        """刷新串口列表（含芯片型号）"""
        ports_info = self.serial_handler.get_available_ports_with_info()

        # 排序：COM 号升序
        def sort_key(info):
            m = re.search(r'COM(\d+)', info['device'], re.IGNORECASE)
            if m:
                return (0, int(m.group(1)))
            return (1, info['device'])

        ports_info.sort(key=sort_key)

        # 保存映射
        self._ports_info = {info['display']: info for info in ports_info}

        # 更新下拉框
        self.port_combo.clear()
        displays = [info['display'] for info in ports_info]
        self.port_combo.addItems(displays)
        if displays:
            self.port_combo.setCurrentIndex(0)

        if ports_info:
            chip_summary = ', '.join(f"{i['device']}={i['chip']}" for i in ports_info)
            self._log(f"刷新串口列表：{len(ports_info)} 个可用 [{chip_summary}]")
        else:
            self._log("刷新串口列表：0 个可用")

    def toggle_connection(self):
        if self.serial_handler.is_connected:
            self._disconnect_serial()
        else:
            self._connect_serial()

    def _connect_serial(self):
        selected = self.port_combo.currentText()
        if not selected:
            self._log("⚠️ 请先选择串口")
            return

        info = self._ports_info.get(selected)
        if info:
            port = info['device']
            chip = info['chip']
        else:
            m = re.search(r'(COM\d+)', selected, re.IGNORECASE)
            port = m.group(1) if m else selected
            chip = '未知'

        if self.serial_handler.connect(port, 115200):
            self.connect_btn.setText("📡 断开连接")
            self._set_button_style(self.connect_btn, "RedButton")
            self._set_status(f"🟢 已连接：{port} ({chip}) @ 115200", 'success')
            self._log(f"✓ 成功连接串口：{port} [{chip}]")
            # 后台读取下位机参数（避免阻塞 UI）
            self._log("⏳ 正在读取下位机参数...")
            t = threading.Thread(target=self._read_params_worker, daemon=True)
            t.start()
        else:
            self._log("✗ 连接串口失败")

    def _disconnect_serial(self):
        self.serial_handler.disconnect()
        self.connect_btn.setText("📡 连接串口")
        self._set_button_style(self.connect_btn, "PrimaryButton")
        self._set_status("⚪ 未连接", 'secondary')
        self._log("✓ 已断开串口连接")

    def _read_params_worker(self):
        """后台线程：读取下位机参数（音量、时长、启用标志）"""
        result = self.serial_handler.read_params(timeout=0.5)
        if result is not None:
            volume, duration, enabled = result
            self.signals.params_ready.emit(volume, duration, enabled)
        else:
            self._log("⚠️ 读取下位机参数失败（下位机固件可能未支持）")

    def _apply_params(self, volume: int, duration: int, enabled: bool):
        """主线程槽：用读取到的参数更新界面"""
        # 限制范围
        volume = max(0, min(100, volume))
        duration = max(0, min(60, duration))
        # 更新音量滑块
        self.volume_slider.setValue(volume)
        # 更新时长输入
        self.time_edit.setText(str(duration))
        # 更新开关状态
        self.buzzer_toggle.blockSignals(True)
        self.buzzer_toggle.setChecked(enabled)
        self.buzzer_toggle.blockSignals(False)
        self._update_buzzer_controls(enabled)
        self._log(f"✓ 读取下位机参数：音量={volume}, 时长={duration}s, 蜂鸣器={'启用' if enabled else '关闭'}")

    def _set_button_style(self, btn: QPushButton, obj_name: str):
        """切换按钮的 objectName 并强制刷新 QSS 样式"""
        btn.style().unpolish(btn)
        btn.setObjectName(obj_name)
        btn.style().polish(btn)

    # ============================================================
    # 灯光控制
    # ============================================================

    def send_light_command(self, color: str):
        if not self.serial_handler.is_connected:
            self._log("⚠️ 请先连接串口")
            return

        cmd_map = {
            'green':  ('🟢 绿灯 (AI空闲)',     self.serial_handler.set_green),
            'yellow': ('🟡 黄灯 (AI思考)',     self.serial_handler.set_yellow),
            'red':    ('🔴 红灯 (故障/异常)',   self.serial_handler.set_red),
            'off':    ('⚫ 关闭灯光',           self.serial_handler.turn_off),
        }
        desc, fn = cmd_map.get(color, (None, None))
        if fn is None:
            return
        ok = fn()
        self._log(f"{desc}  {'✓' if ok else '✗ 失败'}")

    # ============================================================
    # 蜂鸣器设置
    # ============================================================

    def save_buzzer_settings(self):
        if not self.serial_handler.is_connected:
            self._log("⚠️ 请先连接串口")
            return

        try:
            time_val = int(self.time_edit.text())
            if not (0 <= time_val <= 60):
                self._log("✗ 时长必须在 0-60 秒之间")
                return
        except ValueError:
            self._log("✗ 请输入有效的数字")
            return

        volume = self.volume_slider.value()
        enabled = self.buzzer_toggle.isChecked()
        ok = self.serial_handler.set_buzzer(volume, time_val, enabled)
        if ok:
            self._log(f"🔊 蜂鸣器设置已保存：音量={volume}, 时长={time_val}s, {'启用' if enabled else '关闭'}")
        else:
            self._log("✗ 发送蜂鸣器设置失败")

    # ============================================================
    # API 服务
    # ============================================================

    def _on_api_toggled(self, state):
        if state == Qt.Checked:
            self._start_api()
        else:
            self._stop_api()

    def _start_api(self):
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
            url = "http://127.0.0.1:5000"
            self._set_api_state(True, url)
            self._log(f"✓ API 服务已启动：{url}")
        except Exception as e:
            self._log(f"✗ API 服务启动失败：{e}")
            self.api_check.blockSignals(True)
            self.api_check.setChecked(False)
            self.api_check.blockSignals(False)

    def _stop_api(self):
        if self.api_server:
            self.api_server = None
            self.api_thread = None
            self._set_api_state(False, "")
            self._log("✓ API 服务已停止")

    # ============================================================
    # 日志与状态（线程安全，通过信号转发）
    # ============================================================

    def _log(self, message: str):
        """线程安全的日志（通过信号转发到主线程）"""
        self.signals.log.emit(message)

    def _append_log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f'<span style="color:{self._log_color()}">[{timestamp}] {message}</span>')
        self.log_text.moveCursor(QTextCursor.End)

    def _log_color(self) -> str:
        return self.theme.current['text']

    def _set_status(self, text: str, color_key: str = 'secondary'):
        """线程安全：请求更新状态栏（通过信号转发到主线程）"""
        self.signals.status.emit(text, color_key)

    def _apply_status(self, text: str, color_key: str):
        """主线程槽：实际更新状态栏文字"""
        self.status_label.setText(text)

    def _set_api_state(self, running: bool, url: str):
        """线程安全：请求更新 API 状态显示"""
        self.signals.api_state.emit(running, url)

    def _apply_api_state(self, running: bool, url: str):
        """主线程槽：实际更新 API 标签"""
        self.api_label.setText(f"API：{url}" if running else "")

    # ============================================================
    # 系统托盘
    # ============================================================

    def _create_tray_icon(self) -> QIcon:
        """加载应用图标（PNG），找不到则回退到代码生成"""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.png')
        if os.path.exists(icon_path):
            return QIcon(icon_path)

        # fallback：代码生成简易图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor('#5b8def')))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
        painter.setBrush(QBrush(QColor('#22c55e')))
        painter.drawEllipse(14, 28, 12, 12)
        painter.setBrush(QBrush(QColor('#f59e0b')))
        painter.drawEllipse(30, 28, 12, 12)
        painter.setBrush(QBrush(QColor('#ef4444')))
        painter.drawEllipse(46, 28, 12, 12)
        painter.end()
        return QIcon(pixmap)

    def _set_window_icon(self):
        """设置窗口图标"""
        self.setWindowIcon(self._create_tray_icon())

    def _init_tray(self):
        """初始化系统托盘图标"""
        self._tray_quit_confirmed = False  # 标记是否确认退出
        self._tray_icon = QSystemTrayIcon(self._create_tray_icon(), self)
        self._tray_icon.setToolTip("AI 指示灯控制器")

        # 托盘菜单
        menu = QMenu()
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self._show_from_tray)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self._quit_from_tray)
        menu.addAction(quit_action)

        self._tray_icon.setContextMenu(menu)
        # 双击托盘图标恢复窗口
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()

    def _on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self):
        """从托盘恢复窗口"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

    def _quit_from_tray(self):
        """从托盘菜单退出"""
        self._tray_quit_confirmed = True
        self._tray_icon.hide()
        self.close()

    def _minimize_to_tray(self):
        """最小化到系统托盘"""
        self.hide()
        self._tray_icon.showMessage(
            "AI 指示灯控制器",
            "程序已最小化到系统托盘，双击图标可恢复窗口",
            QSystemTrayIcon.Information,
            2000
        )

    # ============================================================
    # 关闭事件：弹出选择对话框（退出 / 最小化到托盘 / 取消）
    # ============================================================

    def closeEvent(self, event):
        # 如果是托盘菜单触发的退出，直接清理
        if getattr(self, '_tray_quit_confirmed', False):
            self._cleanup_and_quit()
            event.accept()
            return

        # 弹出选择对话框
        msg = QMessageBox(self)
        msg.setWindowTitle("关闭确认")
        msg.setText("您想要完全退出程序，还是最小化到系统托盘继续运行？")
        msg.setIcon(QMessageBox.Question)

        btn_quit = msg.addButton("退出程序", QMessageBox.RejectRole)
        btn_tray = msg.addButton("最小化到托盘", QMessageBox.AcceptRole)
        btn_cancel = msg.addButton("取消", QMessageBox.RejectRole)
        msg.setDefaultButton(btn_tray)

        msg.exec_()

        if msg.clickedButton() == btn_quit:
            self._cleanup_and_quit()
            event.accept()
        elif msg.clickedButton() == btn_tray:
            event.ignore()
            self._minimize_to_tray()
        else:
            # 取消
            event.ignore()

    def _cleanup_and_quit(self):
        """清理资源后退出"""
        if self.serial_handler.is_connected:
            self.serial_handler.disconnect()
        if self.api_server:
            self._stop_api()
        if hasattr(self, '_tray_icon'):
            self._tray_icon.hide()


# ============================================================
# 入口
# ============================================================

def main():
    import sys
    app = QApplication(sys.argv)
    # 默认字体
    app.setFont(QFont(FONT_FAMILY, 10))
    window = AIIndicatorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
