"""
AI指示灯 - 主程序入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import AIIndicatorGUI
import tkinter as tk


def main():
    """主函数"""
    root = tk.Tk()
    app = AIIndicatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
