"""
应用图标生成器 - 用 QPainter 绘制 AI 指示灯应用图标

设计理念：
- 圆角方形蓝色渐变背景，现代扁平化
- 三个水平排列的发光圆点（绿/黄/红），直观传达"三色状态指示灯"
- 每个圆点带径向光晕，营造发光感
- 左上角高光，增加质感
"""

import sys
import os

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QRadialGradient, QLinearGradient
from PyQt5.QtCore import Qt, QPointF, QRectF


def draw_icon(size: int = 256) -> QPixmap:
    """绘制应用图标"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # ===== 1. 圆角方形背景（蓝色线性渐变）=====
    margin = size * 0.04  # 边距
    bg_rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22  # 圆角半径

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor('#6366f1'))   # 左上 - 靛蓝
    grad.setColorAt(1.0, QColor('#4338ca'))   # 右下 - 深靛蓝
    p.setBrush(QBrush(grad))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(bg_rect, radius, radius)

    # ===== 2. 左上角高光（增加质感）=====
    highlight = QRadialGradient(
        size * 0.28, size * 0.25, size * 0.4,
        size * 0.28, size * 0.25
    )
    highlight.setColorAt(0.0, QColor(255, 255, 255, 70))
    highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.setBrush(QBrush(highlight))
    p.drawRoundedRect(bg_rect, radius, radius)

    # ===== 3. 三个发光圆点（绿/黄/红）=====
    dots = [
        {'x': 0.30, 'color': QColor('#22c55e'), 'glow': QColor(34, 197, 94, 90)},   # 绿
        {'x': 0.50, 'color': QColor('#fbbf24'), 'glow': QColor(251, 191, 36, 90)},   # 黄
        {'x': 0.70, 'color': QColor('#ef4444'), 'glow': QColor(239, 68, 68, 90)},    # 红
    ]
    dot_r = size * 0.085      # 圆点半径
    glow_r = size * 0.16       # 光晕半径
    cy = size * 0.48           # 圆点中心 Y

    for dot in dots:
        cx = size * dot['x']
        # 光晕（径向渐变）
        glow_grad = QRadialGradient(cx, cy, glow_r, cx, cy)
        glow_grad.setColorAt(0.0, dot['glow'])
        glow_grad.setColorAt(1.0, QColor(dot['color'].red(), dot['color'].green(), dot['color'].blue(), 0))
        p.setBrush(QBrush(glow_grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        # 圆点本体（带微渐变）
        dot_grad = QRadialGradient(cx - dot_r * 0.3, cy - dot_r * 0.3, dot_r * 1.5, cx, cy)
        dot_grad.setColorAt(0.0, dot['color'].lighter(120))
        dot_grad.setColorAt(1.0, dot['color'].darker(110))
        p.setBrush(QBrush(dot_grad))
        p.drawEllipse(QPointF(cx, cy), dot_r, dot_r)

    # ===== 4. 底部"AI"文字（带阴影，更醒目）=====
    font = p.font()
    font.setPixelSize(int(size * 0.14))
    font.setBold(True)
    font.setWeight(75)  # Bold
    p.setFont(font)

    text_x = size * 0.5
    text_y = size * 0.78
    # 阴影
    p.setPen(QColor(0, 0, 0, 60))
    p.drawText(int(text_x + 1), int(text_y + 1), "AI")
    # 主文字
    p.setPen(QColor(255, 255, 255, 245))
    p.drawText(int(text_x), int(text_y), "AI")

    p.end()
    return pixmap


def main():
    app = QApplication(sys.argv)

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # 生成 256x256 高清图标
    icon_256 = draw_icon(256)
    png_path = os.path.join(out_dir, 'app_icon.png')
    icon_256.save(png_path, 'PNG')
    print(f"✓ PNG 图标已生成: {png_path} ({icon_256.width()}x{icon_256.height()})")

    # 生成小尺寸图标用于不同场景
    for sz in [16, 32, 48, 64, 128]:
        small = icon_256.scaled(sz, sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        small_path = os.path.join(out_dir, f'app_icon_{sz}.png')
        small.save(small_path, 'PNG')
        print(f"  → {sz}x{sz}: {small_path}")

    # 尝试生成 ICO（多尺寸）
    ico_path = os.path.join(out_dir, 'app_icon.ico')
    # PyQt5 的 QPixmap.save 对 .ico 支持有限，尝试保存
    if icon_256.save(ico_path, 'ICO'):
        print(f"✓ ICO 图标已生成: {ico_path}")
    else:
        print("⚠ ICO 直接保存失败，可使用 PNG 替代或用 Pillow 转换")

    print("\n图标设计完成！")
    print("  - 主图标: app_icon.png (256x256)")
    print("  - 窗口图标: app_icon.png")
    print("  - 托盘图标: app_icon.png")
    print("  - EXE打包: app_icon.ico")


if __name__ == '__main__':
    main()
