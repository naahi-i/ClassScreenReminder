import os
import logging
import time
import sys
from datetime import datetime
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication

# 处理导入问题 - 支持直接运行此文件和作为包的一部分导入
try:
    # 尝试相对导入 (当作为包的一部分导入时)
    from ..utils.sound_manager import play_initial_sound, initialize_sound, _is_second_sound_playing
    from .ui_components import ColorBlock, LightEffectBlock
    from .reminder_ui import ReminderUI
    from .reminder_animation import ReminderAnimator
    from .reminder_events import ReminderEventHandler
except ImportError:
    # 尝试绝对导入 (当直接运行此文件时)
    try:
        # 确保正确的导入路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        components_dir = current_dir
        src_dir = os.path.dirname(components_dir)
        root_dir = os.path.dirname(src_dir)
        
        if components_dir not in sys.path:
            sys.path.append(components_dir)
        if src_dir not in sys.path:
            sys.path.append(src_dir)
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        
        # 调整导入路径以适应新的目录结构
        from src.utils.sound_manager import play_initial_sound, initialize_sound, _is_second_sound_playing
        from src.components.ui_components import ColorBlock, LightEffectBlock
        from src.components.reminder_ui import ReminderUI
        from src.components.reminder_animation import ReminderAnimator
        from src.components.reminder_events import ReminderEventHandler
    except ImportError as e:
        print(f"导入错误: {e}")
        sys.exit(1)

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ReminderScreen")

class ReminderScreen(QWidget):
    """全屏提醒窗口类"""
    
    def __init__(self, message, duration=10, play_sound=True, wallpapers=None, card_manager=None):
        super().__init__()
        self.message = message
        self.play_sound = play_sound  # 保存声音设置
        self.wallpapers = wallpapers or {}  # 保存壁纸设置，字典格式 {区域: 路径}
        self.card_manager = card_manager   # 名片管理器
        
        # 根据设置决定是否播放声音
        if play_sound:
            # 确保声音初始化成功
            if not initialize_sound():
                logger.warning("声音初始化失败，将禁用声音提醒")
                self.play_sound = False
            else:
                play_initial_sound()
        
        # 确保duration是整数并且大于0
        try:
            self.duration = max(1, int(duration))
        except (ValueError, TypeError):
            logger.warning(f"无效的显示时长: {duration}，使用默认值10秒")
            self.duration = 10
        
        # 添加状态标志
        self.is_closing = False
        self.is_entering = True  # 标记正在播放入场动画
        self.click_count = 0     # 点击计数
        self.last_click_time = 0 # 上次点击时间
        
        # 初始化UI
        self.ui = ReminderUI(self)
        self.ui.setup_ui()
        
        # 初始化动画管理器
        self.animator = ReminderAnimator(self)
        
        # 初始化事件处理器
        self.event_handler = ReminderEventHandler(self)
        
        # 重复播放计时器
        self.sound_repeat_timer = QTimer(self)
        self.sound_repeat_timer.timeout.connect(self.play_sound_group)
        if self.play_sound:  # 仅在启用声音时启动计时器
            self.sound_repeat_timer.start(4000)
        
        # 启动入场动画
        self.animator.start_animations()
        
        # 定时关闭
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.animator.start_close_animation)
        self.close_timer.setSingleShot(True)
        self.close_timer.start(self.duration * 1000)
    
    def play_sound_group(self):
        """播放一组提示音"""
        if not self.play_sound:  # 如果禁用声音，直接返回
            return
        
        # 引用全局变量
        global _is_second_sound_playing
        # 直接使用已导入的函数，而不是重新导入
        if not _is_second_sound_playing:
            play_initial_sound()
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        self.event_handler.handle_mouse_press(event)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        self.event_handler.handle_key_press(event)