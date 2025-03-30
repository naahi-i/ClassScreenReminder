import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream, Qt

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from src.main_window import MainWindow
from src.config_manager import ConfigManager
from src.utils.sound_manager import initialize_sound
from src.utils.resource_manager import init_resource_paths, get_resource_path, create_default_resources, get_icon_path

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

def main():
    # 检查是否已有实例在运行
    if not check_single_instance():
        sys.exit(0)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("ClassScreenReminder")
    
    # 初始化资源路径
    app_dir = os.path.dirname(os.path.abspath(__file__))
    init_resource_paths(app_dir)
    
    # 确保资源目录和必要文件存在
    create_default_resources()
    
    # 设置应用图标
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
    
    # 设置高DPI缩放
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # 加载样式表
    style_path = get_resource_path("style.qss")
    app.setStyleSheet(load_stylesheet(style_path))
    
    # 静默加载声音资源
    sound_initialized = initialize_sound()
    if not sound_initialized:
        # 显示提示对话框
        QMessageBox.warning(
            None, 
            "声音资源缺失", 
            "未找到声音文件 'attend_class.wav'。\n\n"
            "请在 resources 目录中放置此文件，以启用提醒声音功能。\n"
            "程序将继续运行，但没有声音提醒。"
        )
    
    # 初始化配置管理器并创建主窗口
    config_manager = ConfigManager()
    main_window = MainWindow(config_manager)
    
    # 如果设置了启动时最小化，则不显示主窗口
    if not config_manager.get_startup_minimized():
        main_window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
