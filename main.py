import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream, Qt

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from src.main_window import MainWindow
from src.config_manager import ConfigManager
from src.reminder_screen import initialize_sound

# 配置日志记录
log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~/.config')), 'ClassScreenReminder')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'app.log'),
    filemode='a'
)

def load_stylesheet(resource):
    """加载应用样式表"""
    file = QFile(resource)
    if not file.open(QFile.ReadOnly | QFile.Text):
        return ""
    stream = QTextStream(file)
    return stream.readAll()

def check_single_instance():
    """检查是否已有实例运行"""
    if sys.platform == 'win32':
        try:
            import win32event
            import win32api
            import winerror
            
            mutex_name = "ClassScreenReminderMutex"
            mutex = win32event.CreateMutex(None, False, mutex_name)
            return win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS
        except ImportError:
            return True
    return True

if __name__ == "__main__":
    # 检查是否已有实例在运行
    if not check_single_instance():
        sys.exit(0)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("ClassScreenReminder")
    
    # 应用根目录
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置应用图标
    icon_path = os.path.join(app_dir, "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 设置高DPI缩放
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 确保资源目录存在并加载样式表
    resources_dir = os.path.join(app_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    style_path = os.path.join(resources_dir, "style.qss")
    if os.path.exists(style_path):
        app.setStyleSheet(load_stylesheet(style_path))
    
    # 静默加载声音资源
    initialize_sound()
    
    # 初始化配置管理器并创建主窗口
    config_manager = ConfigManager()
    main_window = MainWindow(config_manager)
    main_window.show()
    
    # 运行应用
    sys.exit(app.exec())
