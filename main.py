"""
ClassScreenReminder - 课堂屏幕提醒应用
主程序入口文件
"""
import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream, Qt
from PySide6.QtMultimedia import QMediaPlayer  # 添加多媒体模块支持

from src.main_window import MainWindow
from src.config_manager import ConfigManager
from src.reminder_screen import initialize_sound  # 导入声音初始化函数

# 配置日志记录 - 简化版
logging.basicConfig(
    level=logging.ERROR,  # 只显示错误
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

def load_stylesheet(resource):
    """加载应用样式表"""
    file = QFile(resource)
    if not file.open(QFile.ReadOnly | QFile.Text):
        return ""
    stream = QTextStream(file)
    return stream.readAll()

if __name__ == "__main__":
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("ClassScreenReminder")
    
    # 设置应用图标 - 使用根目录的icon.ico
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 设置高DPI缩放 - 提高文字清晰度
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 加载风格样式表
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "style.qss")
    if os.path.exists(style_path):
        app.setStyleSheet(load_stylesheet(style_path))
    
    # 确保资源目录存在
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
        print(f"已创建资源目录: {resources_dir}")
    
    # 检查音频文件是否存在
    sound_file = os.path.join(resources_dir, "attend_class.wav")
    if not os.path.exists(sound_file):
        print(f"警告: 找不到声音文件 {sound_file}")
        print("请确保在resources目录中有attend_class.wav文件")
    else:
        # 启动时预加载声音资源
        print("预加载声音资源...")
        initialize_sound()
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 创建并显示主窗口
    main_window = MainWindow(config_manager)
    main_window.show()
    
    # 运行应用
    sys.exit(app.exec())
