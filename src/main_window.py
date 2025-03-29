import sys
import os
import logging
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QTimeEdit, QListWidget, 
                              QListWidgetItem, QSystemTrayIcon, QMenu, QMessageBox, 
                              QFormLayout, QSpinBox, QApplication, QFrame, 
                              QTextEdit, QCheckBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtGui import QIcon, QAction, QCloseEvent

# 修改导入方式以支持打包
try:
    # 正常导入方式
    from src.reminder_screen import ReminderScreen, play_initial_sound
    from src.config_manager import ConfigManager
except ImportError:
    # 打包后导入方式
    try:
        from . import reminder_screen
        from .reminder_screen import ReminderScreen, play_initial_sound
        from .config_manager import ConfigManager
    except ImportError:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.append(current_dir)
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            import src.reminder_screen
            from src.reminder_screen import ReminderScreen, play_initial_sound
            from src.config_manager import ConfigManager
        except ImportError:
            # 最后尝试直接导入
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import reminder_screen
            from reminder_screen import ReminderScreen, play_initial_sound
            from config_manager import ConfigManager

# 获取logger
logger = logging.getLogger("ClassScreenReminder.MainWindow")

class MainWindow(QMainWindow):
    """主应用窗口类"""
    
    def __init__(self, config_manager):
        super().__init__()  # 使用默认窗口风格，保留Windows动画
        self.config_manager = config_manager
        self.reminders = self.config_manager.load_reminders()
        self.reminder_screen = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(10000)  # 每10秒检查一次提醒
        
        # 添加上次提醒时间记录，防止同一分钟内重复触发
        self.last_reminder_time = ""
        
        self.setup_ui()
        self.setup_tray()
        
        # 加载设置
        self.minimize_to_tray = self.config_manager.get_setting("minimize_to_tray", True)
        self.start_with_windows = self.config_manager.get_setting("start_with_windows", False)
        
        # 初始化自启动状态
        self.update_autostart_status()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("屏幕提醒")
        self.setMinimumSize(700, 550)  # 增加窗口尺寸以适应控件
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 标题
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 12)
        
        title_label = QLabel("屏幕提醒设置")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        main_layout.addWidget(title_frame)
        
        # 主体区域使用水平布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # 左侧 - 提醒列表区域
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        list_label = QLabel("已设置的提醒:")
        list_label.setObjectName("sectionLabel")
        left_layout.addWidget(list_label)
        
        self.reminder_list = QListWidget()
        self.reminder_list.setObjectName("reminderList")
        self.reminder_list.setMinimumHeight(400)  # 增加高度
        self.reminder_list.setMinimumWidth(300)   # 设置最小宽度
        left_layout.addWidget(self.reminder_list)
        
        # 操作按钮布局
        list_buttons_layout = QHBoxLayout()
        list_buttons_layout.setSpacing(8)
        
        self.edit_button = QPushButton("编辑选中")
        self.edit_button.setObjectName("actionButton")
        self.edit_button.clicked.connect(self.edit_reminder)
        list_buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除提醒")
        self.delete_button.setObjectName("secondaryButton")
        self.delete_button.clicked.connect(self.delete_reminder)
        list_buttons_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(list_buttons_layout)
        content_layout.addWidget(left_panel)
        
        # 右侧 - 添加新提醒区域
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        add_title = QLabel("添加新提醒")
        add_title.setObjectName("sectionLabel")
        right_layout.addWidget(add_title)
        
        # 添加新提醒表单
        new_reminder_frame = QFrame()
        new_reminder_frame.setObjectName("newReminderFrame")
        new_reminder_layout = QVBoxLayout(new_reminder_frame)
        new_reminder_layout.setContentsMargins(16, 16, 16, 16)
        new_reminder_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 时间编辑器
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setObjectName("timeEdit")
        form_layout.addRow("提醒时间:", self.time_edit)
        
        # 持续时间调整
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 60)
        self.duration_spinbox.setValue(10)
        self.duration_spinbox.setSuffix(" 秒")
        self.duration_spinbox.setObjectName("durationSpinBox")
        form_layout.addRow("显示时长:", self.duration_spinbox)
        
        # 添加声音设置复选框
        self.sound_checkbox = QCheckBox("播放提醒声音")
        self.sound_checkbox.setChecked(True)
        self.sound_checkbox.setObjectName("soundCheckBox")
        form_layout.addRow("声音设置:", self.sound_checkbox)
        
        # 星期选择组
        weekday_group = QGroupBox("启用的星期")
        weekday_group.setObjectName("weekdayGroup")
        weekday_layout = QGridLayout(weekday_group)
        weekday_layout.setSpacing(8)
        weekday_layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建星期复选框
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.weekday_checkboxes = []
        
        # 每行放置4个复选框，更紧凑
        for i, name in enumerate(weekday_names):
            row = i // 4
            col = i % 4
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)  # 默认选中
            self.weekday_checkboxes.append(checkbox)
            weekday_layout.addWidget(checkbox, row, col)
        
        form_layout.addRow("星期设置:", weekday_group)
        
        # 使用QTextEdit替换QLineEdit以支持多行输入
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("输入提醒消息...\n可输入多行，每行将显示为单独的消息")
        self.message_edit.setObjectName("messageEdit")
        self.message_edit.setMinimumHeight(80)  # 设置最小高度
        self.message_edit.setMaximumHeight(120)  # 设置最大高度
        # 简化样式
        self.message_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                padding: 10px 10px 10px 12px;
                background-color: white;
                color: #333333;
                font-size: 14px;
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            }
            QTextEdit:focus {
                border-color: #0078d4;
                border-left-width: 3px;
            }
        """)
        form_layout.addRow("提醒消息:", self.message_edit)
        
        new_reminder_layout.addLayout(form_layout)
        
        # 添加和测试按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # 左侧空白
        button_layout.addStretch()
        
        self.add_button = QPushButton("添加提醒")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_reminder)
        button_layout.addWidget(self.add_button)
        
        self.test_button = QPushButton("测试提醒")
        self.test_button.setObjectName("actionButton")
        self.test_button.clicked.connect(self.test_reminder)
        button_layout.addWidget(self.test_button)
        
        new_reminder_layout.addLayout(button_layout)
        right_layout.addWidget(new_reminder_frame)
        
        # 开机自启动选项
        auto_start_layout = QHBoxLayout()
        auto_start_layout.setContentsMargins(5, 5, 5, 5)
        
        self.autostart_checkbox = QCheckBox("开机自动启动")
        self.autostart_checkbox.setChecked(self.config_manager.get_setting("start_with_windows", False))
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        auto_start_layout.addWidget(self.autostart_checkbox)
        
        auto_start_layout.addStretch()
        right_layout.addLayout(auto_start_layout)
        
        content_layout.addWidget(right_panel)
        
        # 设置内容比例 (左:右 = 4:6)
        content_layout.setStretch(0, 4)
        content_layout.setStretch(1, 6)
        
        main_layout.addLayout(content_layout)
        
        # 底部状态区域
        status_bar = QLabel("应用会在后台自动运行，检查提醒并显示在屏幕上")
        status_bar.setObjectName("statusLabel")
        status_bar.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(status_bar)
        
        # 更新提醒列表
        self.update_reminder_list()
    
    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 使用根目录的图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.ico")
        self.tray_icon.setIcon(QIcon(icon_path))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def closeEvent(self, event: QCloseEvent):
        """最小化到托盘"""
        if self.minimize_to_tray and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def close_application(self):
        """彻底关闭应用"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def show_from_tray(self):
        """从托盘显示窗口"""
        self.showNormal()
        self.activateWindow()  # 在Windows上激活窗口并设置焦点
    
    def tray_icon_activated(self, reason):
        """处理托盘图标点击事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()
    
    def update_reminder_list(self):
        """更新提醒列表显示"""
        self.reminder_list.clear()
        
        # 星期缩写
        weekday_abbrs = ["一", "二", "三", "四", "五", "六", "日"]
        
        for reminder in self.reminders:
            time_str = reminder["time"]
            message = reminder["message"]
            lines_count = message.count('\n') + 1
            
            # 在列表中只显示消息的第一行，如果有多行则添加行数信息
            if "\n" in message:
                first_line = message.split("\n")[0]
                display_message = f"{first_line}... ({lines_count}行)"
            else:
                display_message = message
            
            duration = reminder["duration"]
            
            # 显示声音状态
            sound_status = "有声音" if reminder.get("play_sound", True) else "静音"
            
            # 显示星期
            weekdays = reminder.get("weekdays", [True] * 7)
            weekday_str = ""
            for i, enabled in enumerate(weekdays):
                if enabled:
                    weekday_str += weekday_abbrs[i]
            
            weekday_display = f"[{weekday_str}]" if weekday_str else "[无]"
            
            item = QListWidgetItem(f"{time_str} {weekday_display} - {display_message} ({duration}秒) [{sound_status}]")
            self.reminder_list.addItem(item)
    
    def add_reminder(self):
        """添加新提醒"""
        time_str = self.time_edit.time().toString("HH:mm")
        message = self.message_edit.toPlainText().strip()
        duration = self.duration_spinbox.value()
        play_sound = self.sound_checkbox.isChecked()
        
        # 获取选中的星期
        weekdays = [checkbox.isChecked() for checkbox in self.weekday_checkboxes]
        
        if not message:
            QMessageBox.warning(self, "警告", "请输入提醒消息")
            return
        
        # 添加到提醒列表
        reminder = {
            "time": time_str,
            "message": message,
            "duration": int(duration),  # 确保duration是整数
            "play_sound": play_sound,   # 添加声音设置
            "weekdays": weekdays        # 添加星期设置
        }
        
        self.reminders.append(reminder)
        
        # 保存到配置
        self.config_manager.save_reminders(self.reminders)
        
        # 更新UI
        self.update_reminder_list()
        self.message_edit.clear()
    
    def delete_reminder(self):
        """删除选中的提醒"""
        current_row = self.reminder_list.currentRow()
        if current_row >= 0:
            # 获取当前选中的提醒信息
            reminder = self.reminders[current_row]
            time_str = reminder["time"]
            message = reminder["message"].split('\n')[0]  # 只显示第一行
            
            # 显示确认对话框
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除以下提醒吗？\n时间: {time_str}\n内容: {message}", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.reminders[current_row]
                self.config_manager.save_reminders(self.reminders)
                self.update_reminder_list()
    
    def test_reminder(self):
        """测试提醒显示效果"""
        # 获取当前时间和测试消息
        current_time = datetime.now().strftime("%H:%M")
        message = self.message_edit.toPlainText().strip()
        if not message:
            message = "测试提醒内容"
        
        duration = self.duration_spinbox.value()
        play_sound = self.sound_checkbox.isChecked()
        
        if self.reminder_screen:
            self.reminder_screen.close()
            self.reminder_screen = None
        
        # 创建新的提醒屏幕对象，会在初始化时播放声音
        self.reminder_screen = ReminderScreen(message, int(duration), play_sound)
        self.reminder_screen.show()
    
    def check_reminders(self):
        """检查是否有到期的提醒"""
        current_time = datetime.now().strftime("%H:%M")
        
        # 获取当前是星期几 (0是周一，6是周日)
        current_weekday = datetime.now().weekday()
        
        # 防止同一分钟内重复触发提醒
        if current_time == self.last_reminder_time:
            return
        
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                # 检查当前星期是否启用
                weekdays = reminder.get("weekdays", [True] * 7)
                if not weekdays[current_weekday]:
                    # 当前星期未启用此提醒，跳过
                    continue
                
                # 记录当前提醒时间，避免重复触发
                self.last_reminder_time = current_time
                
                # 关闭现有提醒（如果有）
                if self.reminder_screen:
                    self.reminder_screen.close()
                    self.reminder_screen = None
                
                # 确保duration是整数
                duration = int(reminder.get("duration", 10))
                message = reminder["message"]
                play_sound = reminder.get("play_sound", True)  # 获取声音设置
                
                # 创建新的提醒屏幕，根据设置决定是否播放声音
                self.reminder_screen = ReminderScreen(message, duration, play_sound)
                self.reminder_screen.show()
                
                # 找到了匹配的提醒，退出循环
                break
    
    def update_autostart_status(self):
        """更新开机自启动状态"""
        # 获取注册表自启动项路径
        if sys.platform == 'win32':
            try:
                import winreg
                # 打开注册表
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
                # 尝试读取注册表值
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        value, _ = winreg.QueryValueEx(key, "ClassScreenReminder")
                        exists = True
                except FileNotFoundError:
                    exists = False
                
                # 更新配置和UI
                if exists != self.start_with_windows:
                    self.start_with_windows = exists
                    self.config_manager.set_setting("start_with_windows", exists)
                    if hasattr(self, 'autostart_checkbox'):
                        self.autostart_checkbox.setChecked(exists)
            except Exception as e:
                logger.error(f"更新自启动状态出错: {e}")
    
    def toggle_autostart(self, state):
        """切换开机自启动状态"""
        enable = bool(state)
        
        if sys.platform == 'win32':
            try:
                import winreg
                # 获取应用程序路径
                app_path = f'"{sys.executable}"'
                if getattr(sys, 'frozen', False):
                    # PyInstaller打包后的路径
                    app_path = f'"{sys.executable}"'
                else:
                    # 开发环境路径
                    main_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
                    app_path = f'"{sys.executable}" "{main_script}"'
                
                # 打开注册表
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
                
                if enable:
                    # 添加到自启动
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "ClassScreenReminder", 0, winreg.REG_SZ, app_path)
                else:
                    # 从自启动中移除
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, "ClassScreenReminder")
                    except FileNotFoundError:
                        pass  # 如果键不存在，则不需要删除
                
                # 保存设置
                self.start_with_windows = enable
                self.config_manager.set_setting("start_with_windows", enable)
                
            except Exception as e:
                logger.error(f"设置自启动出错: {e}")
                QMessageBox.warning(self, "错误", f"设置开机自启动失败: {str(e)}")
                # 恢复复选框状态
                self.autostart_checkbox.setChecked(not enable)
                return
    
    def edit_reminder(self):
        """编辑选中的提醒"""
        current_row = self.reminder_list.currentRow()
        if current_row >= 0:
            reminder = self.reminders[current_row]
            
            # 设置界面值为当前选中的提醒
            self.time_edit.setTime(QTime.fromString(reminder["time"], "HH:mm"))
            self.message_edit.setText(reminder["message"])
            self.duration_spinbox.setValue(reminder["duration"])
            self.sound_checkbox.setChecked(reminder.get("play_sound", True))
            
            # 设置星期复选框
            weekdays = reminder.get("weekdays", [True] * 7)
            for i, checkbox in enumerate(self.weekday_checkboxes):
                checkbox.setChecked(weekdays[i] if i < len(weekdays) else True)
            
            # 删除当前提醒
            del self.reminders[current_row]
            # 更新界面
            self.update_reminder_list()
            
            # 提示用户
            QMessageBox.information(self, "编辑提醒", 
                                 "已加载选中的提醒到编辑区域，\n修改后点击「添加提醒」按钮保存。")