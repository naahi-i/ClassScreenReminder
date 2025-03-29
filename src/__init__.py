# 确保子模块能被正确导入
try:
    from . import reminder_screen
    from . import config_manager
    from . import main_window
    
    from .reminder_screen import ReminderScreen, play_initial_sound, initialize_sound
    from .config_manager import ConfigManager
    from .main_window import MainWindow
except ImportError:
    pass

__all__ = ['ReminderScreen', 'ConfigManager', 'MainWindow', 'play_initial_sound', 'initialize_sound']
