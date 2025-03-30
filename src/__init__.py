# 确保子模块能被正确导入
try:
    # 导入子包
    from . import components
    from . import utils
    from . import config_manager
    from . import main_window
    
    # 从子包导入常用类和函数
    from .components.reminder_screen import ReminderScreen
    from .utils.sound_manager import play_initial_sound, initialize_sound
    from .config_manager import ConfigManager
    from .main_window import MainWindow
except ImportError:
    pass

__all__ = ['ReminderScreen', 'ConfigManager', 'MainWindow', 'play_initial_sound', 'initialize_sound']
