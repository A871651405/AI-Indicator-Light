"""
AI指示灯 - 主程序入口（PyQt5 版）
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_qt import main


if __name__ == '__main__':
    main()
