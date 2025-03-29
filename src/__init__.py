"""
src包初始化文件
使src成为一个Python包
"""
# 确保子模块可以正确导入
from src.reminder_screen import ReminderScreen
from src.config_manager import ConfigManager
from src.main_window import MainWindow

__all__ = ['ReminderScreen', 'ConfigManager', 'MainWindow']
