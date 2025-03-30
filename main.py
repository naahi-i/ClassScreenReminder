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

# 使用新的导入路径
from src.main_window import MainWindow
from src.config_manager import ConfigManager
from src.utils.sound_manager import initialize_sound

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

def create_default_resources():
    """创建默认资源"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # 检查声音文件是否存在
    sound_file = os.path.join(resources_dir, "attend_class.wav")
    if not os.path.exists(sound_file):
        # 记录日志
        logging.warning(f"声音文件未找到: {sound_file}")
        
        # 创建一个提示文件，告知用户需要添加声音文件
        readme_file = os.path.join(resources_dir, "README.txt")
        if not os.path.exists(readme_file):
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write("请在此目录放置名为 'attend_class.wav' 的声音文件，作为提醒声音。\n")
                f.write("可以使用任何WAV格式的短音效。\n")

def main():
    # 检查是否已有实例在运行
    if not check_single_instance():
        sys.exit(0)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("ClassScreenReminder")
    
    # 应用根目录
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确保资源目录和必要文件存在
    create_default_resources()
    
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
