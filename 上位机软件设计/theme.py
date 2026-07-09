"""
主题系统模块 - 定义浅色/深色双主题设计令牌与 QSS 样式生成

设计理念：
- 现代扁平化 + 轻微拟物（柔和阴影、圆角）
- 浅色主题：柔和灰底 + 白色卡片，品牌蓝强调
- 深色主题：深蓝灰底 + 深色卡片，亮蓝强调
- 运行时一键切换，QSS 全局应用
"""

from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication


# ============================================================
# 设计令牌（Design Tokens）
# ============================================================

LIGHT_THEME = {
    'name': 'light',
    # 背景层级
    'bg': '#f5f7fa',              # 主背景 - 柔和灰
    'surface': '#ffffff',          # 卡片/面板背景
    'surface_alt': '#eef1f6',      # 输入框/状态栏背景
    'surface_hover': '#e8ecf2',    # 悬停背景
    # 品牌与语义色
    'primary': '#5b8def',          # 主强调 - 现代蓝
    'primary_hover': '#4a7de0',
    'success': '#22c55e',          # 绿（空闲）
    'success_hover': '#16a34a',
    'warning': '#f59e0b',          # 黄（思考）
    'warning_hover': '#d97706',
    'danger': '#ef4444',           # 红（故障）
    'danger_hover': '#dc2626',
    'neutral': '#94a3b8',          # 中性（关闭）
    'neutral_hover': '#64748b',
    # 文字
    'text': '#1e293b',             # 主文字
    'text_secondary': '#64748b',   # 次文字
    'text_on_color': '#ffffff',    # 彩色按钮上的文字
    'text_placeholder': '#94a3b8',
    # 边框与分隔
    'border': '#e2e8f0',
    'border_focus': '#5b8def',
    # 阴影
    'shadow': 'rgba(0, 0, 0, 0.08)',
}

DARK_THEME = {
    'name': 'dark',
    # 背景层级
    'bg': '#0f172a',               # 主背景 - 深蓝灰
    'surface': '#1e293b',          # 卡片/面板背景
    'surface_alt': '#334155',      # 输入框/状态栏背景
    'surface_hover': '#3d4d63',    # 悬停背景
    # 品牌与语义色
    'primary': '#60a5fa',          # 主强调 - 亮蓝
    'primary_hover': '#7dd3fc',
    'success': '#4ade80',          # 绿
    'success_hover': '#86efac',
    'warning': '#fbbf24',          # 黄
    'warning_hover': '#fcd34d',
    'danger': '#f87171',           # 红
    'danger_hover': '#fca5a5',
    'neutral': '#64748b',          # 中性
    'neutral_hover': '#94a3b8',
    # 文字
    'text': '#f1f5f9',             # 主文字
    'text_secondary': '#94a3b8',   # 次文字
    'text_on_color': '#ffffff',    # 彩色按钮上的文字
    'text_placeholder': '#64748b',
    # 边框与分隔
    'border': '#334155',
    'border_focus': '#60a5fa',
    # 阴影
    'shadow': 'rgba(0, 0, 0, 0.4)',
}


# ============================================================
# 排版系统（Typography）
# ============================================================

FONT_FAMILY = "'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Courier New', monospace"

FONT_SIZE_XS = 11   # 辅助文字
FONT_SIZE_SM = 12   # 次要文字
FONT_SIZE_BASE = 13 # 正文
FONT_SIZE_LG = 15   # 小标题
FONT_SIZE_XL = 18   # 区块标题
FONT_SIZE_2XL = 22  # 主标题


# ============================================================
# 间距与圆角系统
# ============================================================

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
SPACE_2XL = 32

RADIUS_SM = 6       # 小按钮
RADIUS_MD = 8       # 输入框
RADIUS_LG = 12      # 卡片
RADIUS_PILL = 999   # 胶囊


# ============================================================
# QSS 样式表生成器
# ============================================================

def generate_qss(t: dict) -> str:
    """
    根据主题令牌生成完整的 QSS 样式表

    Args:
        t: 主题令牌字典（LIGHT_THEME 或 DARK_THEME）

    Returns:
        QSS 样式表字符串
    """
    return f"""
    /* ===== 全局 ===== */
    QWidget {{
        background-color: {t['bg']};
        color: {t['text']};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_BASE}px;
    }}

    /* ===== 主窗口 ===== */
    QMainWindow {{
        background-color: {t['bg']};
    }}

    /* ===== 卡片容器（QGroupBox 充当卡片） ===== */
    QGroupBox {{
        background-color: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_LG}px;
        padding: {SPACE_XL}px {SPACE_LG}px {SPACE_LG}px {SPACE_LG}px;
        margin-top: {SPACE_XL}px;
        font-size: {FONT_SIZE_LG}px;
        font-weight: 600;
        color: {t['text']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: {SPACE_LG}px;
        padding: 0 {SPACE_SM}px;
        background-color: {t['surface']};
        color: {t['primary']};
    }}

    /* ===== 普通帧容器 ===== */
    QFrame#CardFrame {{
        background-color: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_LG}px;
    }}

    /* ===== 标题标签 ===== */
    QLabel#TitleLabel {{
        font-size: {FONT_SIZE_2XL}px;
        font-weight: 700;
        color: {t['text']};
        background: transparent;
    }}
    QLabel#SubtitleLabel {{
        font-size: {FONT_SIZE_SM}px;
        color: {t['text_secondary']};
        background: transparent;
        font-family: {FONT_MONO};
    }}
    QLabel#SectionLabel {{
        font-size: {FONT_SIZE_SM}px;
        font-weight: 600;
        color: {t['text_secondary']};
        background: transparent;
    }}
    QLabel#StatusLabel {{
        font-size: {FONT_SIZE_SM}px;
        color: {t['text_secondary']};
        background: transparent;
    }}

    /* ===== 下拉框 ===== */
    QComboBox {{
        background-color: {t['surface_alt']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_MD}px;
        padding: {SPACE_SM}px {SPACE_MD}px;
        min-height: 20px;
        color: {t['text']};
    }}
    QComboBox:hover {{
        border-color: {t['primary']};
    }}
    QComboBox:focus {{
        border-color: {t['border_focus']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {t['text_secondary']};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_MD}px;
        padding: {SPACE_SM}px;
        selection-background-color: {t['primary']};
        selection-color: {t['text_on_color']};
        outline: none;
    }}

    /* ===== 按钮（通用） ===== */
    QPushButton {{
        background-color: {t['surface_alt']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_MD}px;
        padding: {SPACE_SM}px {SPACE_LG}px;
        min-height: 22px;
        color: {t['text']};
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {t['surface_hover']};
        border-color: {t['primary']};
    }}
    QPushButton:pressed {{
        background-color: {t['border']};
    }}

    /* ===== 主题色按钮（主操作） ===== */
    QPushButton#PrimaryButton {{
        background-color: {t['primary']};
        border: none;
        border-radius: {RADIUS_MD}px;
        color: {t['text_on_color']};
        font-weight: 600;
        padding: {SPACE_MD}px {SPACE_XL}px;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {t['primary_hover']};
    }}
    QPushButton#PrimaryButton:pressed {{
        background-color: {t['primary']};
    }}

    /* ===== 语义色按钮（灯光控制） ===== */
    QPushButton#GreenButton {{
        background-color: {t['success']};
        border: none;
        border-radius: {RADIUS_MD}px;
        color: {t['text_on_color']};
        font-weight: 600;
        padding: {SPACE_MD}px;
    }}
    QPushButton#GreenButton:hover {{
        background-color: {t['success_hover']};
    }}
    QPushButton#YellowButton {{
        background-color: {t['warning']};
        border: none;
        border-radius: {RADIUS_MD}px;
        color: {t['text_on_color']};
        font-weight: 600;
        padding: {SPACE_MD}px;
    }}
    QPushButton#YellowButton:hover {{
        background-color: {t['warning_hover']};
    }}
    QPushButton#RedButton {{
        background-color: {t['danger']};
        border: none;
        border-radius: {RADIUS_MD}px;
        color: {t['text_on_color']};
        font-weight: 600;
        padding: {SPACE_MD}px;
    }}
    QPushButton#RedButton:hover {{
        background-color: {t['danger_hover']};
    }}
    QPushButton#NeutralButton {{
        background-color: {t['neutral']};
        border: none;
        border-radius: {RADIUS_MD}px;
        color: {t['text_on_color']};
        font-weight: 600;
        padding: {SPACE_MD}px;
    }}
    QPushButton#NeutralButton:hover {{
        background-color: {t['neutral_hover']};
    }}

    /* ===== 图标按钮（主题切换、刷新） ===== */
    QPushButton#IconButton {{
        background-color: transparent;
        border: 1px solid {t['border']};
        border-radius: {RADIUS_PILL}px;
        padding: {SPACE_SM}px {SPACE_MD}px;
        min-width: 36px;
        font-size: {FONT_SIZE_LG}px;
    }}
    QPushButton#IconButton:hover {{
        background-color: {t['surface_hover']};
        border-color: {t['primary']};
    }}

    /* ===== 输入框 ===== */
    QLineEdit {{
        background-color: {t['surface_alt']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_MD}px;
        padding: {SPACE_SM}px {SPACE_MD}px;
        color: {t['text']};
        min-height: 20px;
    }}
    QLineEdit:focus {{
        border-color: {t['border_focus']};
    }}

    /* ===== 滑块 ===== */
    QSlider::groove:horizontal {{
        background-color: {t['surface_alt']};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background-color: {t['primary']};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background-color: {t['surface']};
        border: 2px solid {t['primary']};
        width: 16px;
        height: 16px;
        margin: -7px 0;
        border-radius: 10px;
    }}
    QSlider::handle:horizontal:hover {{
        background-color: {t['primary']};
    }}

    /* ===== 复选框 ===== */
    QCheckBox {{
        background: transparent;
        color: {t['text']};
        spacing: {SPACE_SM}px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {t['border']};
        border-radius: 4px;
        background-color: {t['surface_alt']};
    }}
    QCheckBox::indicator:hover {{
        border-color: {t['primary']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {t['primary']};
        border-color: {t['primary']};
    }}

    /* ===== 滚动文本框（日志） ===== */
    QTextEdit {{
        background-color: {t['bg']};
        border: 1px solid {t['border']};
        border-radius: {RADIUS_MD}px;
        padding: {SPACE_MD}px;
        color: {t['text']};
        font-family: {FONT_MONO};
        font-size: {FONT_SIZE_SM}px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {t['border']};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t['text_secondary']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ===== 状态栏 ===== */
    QFrame#StatusBar {{
        background-color: {t['surface_alt']};
        border-top: 1px solid {t['border']};
    }}
    """


# ============================================================
# 主题管理器
# ============================================================

class ThemeManager:
    """主题管理器 - 管理当前主题与应用 QSS"""

    def __init__(self):
        self._themes = {
            'light': LIGHT_THEME,
            'dark': DARK_THEME,
        }
        self._current = 'light'

    @property
    def current_name(self) -> str:
        return self._current

    @property
    def current(self) -> dict:
        return self._themes[self._current]

    def get(self, name: str = None) -> dict:
        """获取指定主题令牌（默认当前）"""
        return self._themes[name or self._current]

    def apply(self, app: QApplication, name: str = None):
        """
        应用主题到 QApplication

        Args:
            app: QApplication 实例
            name: 主题名 'light' 或 'dark'，默认切换到当前
        """
        if name:
            self._current = name
        tokens = self.current
        qss = generate_qss(tokens)
        app.setStyleSheet(qss)

        # 同步调色板（确保非 QSS 控件也跟随）
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(tokens['bg']))
        palette.setColor(QPalette.WindowText, QColor(tokens['text']))
        palette.setColor(QPalette.Base, QColor(tokens['surface']))
        palette.setColor(QPalette.Text, QColor(tokens['text']))
        palette.setColor(QPalette.Button, QColor(tokens['surface']))
        palette.setColor(QPalette.ButtonText, QColor(tokens['text']))
        app.setPalette(palette)

    def toggle(self, app: QApplication) -> str:
        """切换主题，返回切换后的主题名"""
        new_name = 'dark' if self._current == 'light' else 'light'
        self.apply(app, new_name)
        return new_name
