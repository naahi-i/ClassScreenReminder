import os
import sys
import logging
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QCloseEvent

# 修改导入方式以支持新的目录结构
try:
    # 包内导入
    from .components.reminder_screen import ReminderScreen
    from .components.ui_builder import MainWindowUI
    from .components.ui.audio_manager_ui import AudioManagerUI
    from .components.ui.wallpaper_manager_ui import WallpaperManagerUI
    from .components.ui.tray_manager import TrayManager
    from .components.ui.reminder_manager_ui import ReminderManagerUI
    from .components.ui.card_manager_ui import CardManagerUI
    from .utils.reminder_manager import ReminderManager
    from .utils.autostart_manager import get_autostart_status, set_autostart
    from .config_manager import ConfigManager
    from .utils.wallpaper_manager import WallpaperManager
    from .utils.card_manager import CardManager
except ImportError:
    # 打包后或直接运行时的导入
    try:
        # 确保src目录在路径中
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        # 尝试从绝对路径导入
        from src.components.reminder_screen import ReminderScreen
        from src.components.ui_builder import MainWindowUI
        from src.components.ui.audio_manager_ui import AudioManagerUI
        from src.components.ui.wallpaper_manager_ui import WallpaperManagerUI
        from src.components.ui.tray_manager import TrayManager
        from src.components.ui.reminder_manager_ui import ReminderManagerUI
        from src.components.ui.card_manager_ui import CardManagerUI
        from src.utils.reminder_manager import ReminderManager
        from src.utils.autostart_manager import get_autostart_status, set_autostart
        from src.config_manager import ConfigManager
        from src.utils.wallpaper_manager import WallpaperManager
        from src.utils.card_manager import CardManager
    except ImportError as e:
        print(f"导入错误: {e}")
        sys.exit(1)

# 获取logger
logger = logging.getLogger("ClassScreenReminder.MainWindow")

class MainWindow(QMainWindow):
    """主应用窗口类"""
    
    def __init__(self, config_manager):
        super().__init__()  # 使用默认窗口风格，保留Windows动画
        self.config_manager = config_manager
        
        # 初始化各管理器
        self.reminder_manager = ReminderManager(config_manager)
        self.wallpaper_manager = WallpaperManager(config_manager)
        self.card_manager = CardManager(config_manager)
        
        # 当前显示的提醒屏幕
        self.reminder_screen = None
        
        # 初始化UI构建器
        self.ui_builder = MainWindowUI(self)
        
        # 初始化各UI组件管理器
        self.tray_manager = TrayManager(self)
        self.audio_manager_ui = AudioManagerUI(self)
        self.wallpaper_manager_ui = WallpaperManagerUI(self)
        self.reminder_manager_ui = ReminderManagerUI(self)
        self.card_manager_ui = CardManagerUI(self)
        
        # 设置检查提醒的定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(10000)  # 每10秒检查一次提醒
        
        # 加载设置
        self.minimize_to_tray = True  # 强制设置为True
        self.start_with_windows = self.config_manager.get_setting("start_with_windows", True)  # 默认True
        self.startup_minimized = self.config_manager.get_startup_minimized()
        
        # 设置UI
        self.ui_builder.setup_ui()
        
        # 更新提醒列表
        self.reminder_manager_ui.update_reminder_list()
        
        # 确保初始自启动状态正确
        if self.start_with_windows:
            set_autostart(True)
        self.update_autostart_status()
        
        # 更新音频路径显示
        self.audio_manager_ui.update_audio_path_display()
    
    def closeEvent(self, event: QCloseEvent):
        """最小化到托盘"""
        if self.minimize_to_tray and self.tray_manager.is_visible():
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def check_reminders(self):
        """检查是否有到期的提醒"""
        reminder = self.reminder_manager.check_reminders()
        
        if reminder:
            # 关闭现有提醒（如果有）
            if self.reminder_screen:
                self.reminder_screen.close()
                self.reminder_screen = None
            
            # 确保duration是整数
            duration = int(reminder.get("duration", 10))
            message = reminder["message"]
            play_sound = reminder.get("play_sound", True)  # 获取声音设置
            
            # 获取所有区域的壁纸
            wallpapers = self.wallpaper_manager.get_all_wallpapers()
            
            # 创建新的提醒屏幕，传入名片管理器
            self.reminder_screen = ReminderScreen(message, duration, play_sound, wallpapers, self.card_manager)
            self.reminder_screen.show()
    
    def update_autostart_status(self):
        """更新开机自启动状态"""
        # 获取自启动状态
        exists = get_autostart_status()
        
        # 更新配置和UI
        if exists != self.start_with_windows:
            self.start_with_windows = exists
            self.config_manager.set_setting("start_with_windows", exists)
            if hasattr(self, 'autostart_checkbox'):
                self.autostart_checkbox.setChecked(exists)
    
    def toggle_autostart(self, state):
        """切换开机自启动状态"""
        enable = bool(state)
        
        if set_autostart(enable):
            # 保存设置
            self.start_with_windows = enable
            self.config_manager.set_setting("start_with_windows", enable)
        else:
            self.ui_builder.show_warning("错误", "设置开机自启动失败")
            # 恢复复选框状态
            self.autostart_checkbox.setChecked(not enable)
    
    def on_menu_changed(self, menu_id):
        """处理菜单切换事件"""
        if menu_id in self.ui_builder.content_pages:
            self.content_stack.setCurrentIndex(self.ui_builder.content_pages[menu_id])
    
    def on_startup_minimized_changed(self, checked):
        """处理启动时最小化设置变更"""
        self.config_manager.set_startup_minimized(checked)
    
    # 以下是代理方法，将调用转发到对应的UI管理类
    
    # 托盘相关
    def close_application(self):
        self.tray_manager.close_application()
        
    def show_from_tray(self):
        self.tray_manager.show_from_tray()
    
    # 音频相关
    def select_custom_audio(self):
        self.audio_manager_ui.select_custom_audio()
    
    def reset_default_audio(self):
        self.audio_manager_ui.reset_default_audio()
    
    def play_test_sound(self):
        self.audio_manager_ui.play_test_sound()
    
    def update_audio_path_display(self):
        self.audio_manager_ui.update_audio_path_display()
    
    # 壁纸相关
    def select_wallpaper(self):
        self.wallpaper_manager_ui.select_wallpaper()
    
    def clear_wallpaper(self):
        self.wallpaper_manager_ui.clear_wallpaper()
    
    def on_area_changed(self, index):
        self.wallpaper_manager_ui.on_area_changed(index)
    
    def update_wallpaper_preview(self, area):
        self.wallpaper_manager_ui.update_wallpaper_preview(area)
    
    def select_area_wallpaper(self):
        self.wallpaper_manager_ui.select_area_wallpaper()
    
    def clear_area_wallpaper(self):
        self.wallpaper_manager_ui.clear_area_wallpaper()
    
    def clear_all_wallpapers(self):
        self.wallpaper_manager_ui.clear_all_wallpapers()
    
    def on_opacity_changed(self, value):
        """处理壁纸透明度变更"""
        # 确保值是有效的，然后直接转发到壁纸管理UI组件
        try:
            print(f"主窗口收到透明度变更: {value}")
            
            # 确保合理范围
            valid_value = max(0, min(100, value))
            
            # 只有当值合法且管理UI组件存在时才处理
            if hasattr(self, 'wallpaper_manager_ui') and valid_value >= 0 and valid_value <= 100:
                # 转发处理
                self.wallpaper_manager_ui.on_opacity_changed(valid_value)
                
            # 强制更新标签显示当前值
            if hasattr(self, 'opacity_value_label'):
                self.opacity_value_label.setText(f"{valid_value}%")
        except Exception as e:
            import traceback
            print(f"处理透明度变化出错: {e}")
            traceback.print_exc()
    
    # 提醒相关
    def update_reminder_list(self):
        self.reminder_manager_ui.update_reminder_list()
    
    def add_reminder(self):
        self.reminder_manager_ui.add_reminder()
    
    def delete_reminder(self):
        self.reminder_manager_ui.delete_reminder()
    
    def edit_reminder(self):
        self.reminder_manager_ui.edit_reminder()
    
    def test_reminder(self):
        self.reminder_manager_ui.test_reminder()
    
    def reset_form(self):
        self.reminder_manager_ui.reset_form()
    
    # 名片相关
    def add_card(self):
        self.card_manager_ui.add_card()
    
    def edit_card(self):
        self.card_manager_ui.edit_card()
    
    def delete_card(self):
        self.card_manager_ui.delete_card()