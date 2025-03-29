"""
主窗口类 - 处理应用的主界面和系统托盘功能
"""
import sys
import os
import logging
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QTimeEdit, QLineEdit, 
                              QListWidget, QListWidgetItem, QSystemTrayIcon,
                              QMenu, QMessageBox, QFormLayout, QSpinBox,
                              QApplication, QFrame, QSizePolicy, QTextEdit)
from PySide6.QtCore import Qt, QTime, QTimer, QPoint, QSize
from PySide6.QtGui import QIcon, QAction, QCloseEvent, QMouseEvent, QCursor

from src.reminder_screen import ReminderScreen, play_initial_sound
from src.config_manager import ConfigManager

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
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("屏幕提醒")
        self.setMinimumSize(600, 500)  # 增加高度以适应多行文本输入
        
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
        
        # 提醒列表区域
        list_frame = QFrame()
        list_frame.setObjectName("listFrame")
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(10)
        
        list_label = QLabel("已设置的提醒:")
        list_label.setObjectName("sectionLabel")
        list_layout.addWidget(list_label)
        
        self.reminder_list = QListWidget()
        self.reminder_list.setObjectName("reminderList")
        self.reminder_list.setMinimumHeight(150)
        list_layout.addWidget(self.reminder_list)
        
        main_layout.addWidget(list_frame)
        
        # 更新提醒列表
        self.update_reminder_list()
        
        # 添加新提醒区域
        new_reminder_frame = QFrame()
        new_reminder_frame.setObjectName("newReminderFrame")
        new_reminder_layout = QVBoxLayout(new_reminder_frame)
        new_reminder_layout.setContentsMargins(16, 16, 16, 16)
        
        add_title = QLabel("添加新提醒")
        add_title.setObjectName("sectionLabel")
        new_reminder_layout.addWidget(add_title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setObjectName("timeEdit")
        form_layout.addRow("提醒时间:", self.time_edit)
        
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
        
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 60)
        self.duration_spinbox.setValue(10)
        self.duration_spinbox.setSuffix(" 秒")
        self.duration_spinbox.setObjectName("durationSpinBox")
        form_layout.addRow("显示时长:", self.duration_spinbox)
        
        new_reminder_layout.addLayout(form_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        # 添加空白区域实现右对齐
        button_layout.addStretch()
        
        self.add_button = QPushButton("添加提醒")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_reminder)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("删除提醒")
        self.delete_button.setObjectName("secondaryButton")
        self.delete_button.clicked.connect(self.delete_reminder)
        button_layout.addWidget(self.delete_button)
        
        self.test_button = QPushButton("测试提醒")
        self.test_button.setObjectName("actionButton")
        self.test_button.clicked.connect(self.test_reminder)
        button_layout.addWidget(self.test_button)
        
        new_reminder_layout.addLayout(button_layout)
        main_layout.addWidget(new_reminder_frame)
        
        # 底部状态
        status_bar = QLabel("应用会在后台自动运行，检查提醒并显示在屏幕上")
        status_bar.setObjectName("statusLabel")
        main_layout.addWidget(status_bar)
    
    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 使用根目录的图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "icon.ico")
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
        
        # 托盘气泡提示
        self.tray_icon.setToolTip("屏幕提醒")
        self.tray_icon.showMessage("屏幕提醒", "应用已在后台运行", QSystemTrayIcon.Information, 3000)
    
    def closeEvent(self, event: QCloseEvent):
        """重写关闭事件，实现最小化到托盘"""
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
            item = QListWidgetItem(f"{time_str} - {display_message} ({duration}秒)")
            self.reminder_list.addItem(item)
    
    def add_reminder(self):
        """添加新提醒"""
        time_str = self.time_edit.time().toString("HH:mm")
        message = self.message_edit.toPlainText().strip()
        duration = self.duration_spinbox.value()
        
        if not message:
            QMessageBox.warning(self, "警告", "请输入提醒消息")
            return
        
        # 添加到提醒列表
        reminder = {
            "time": time_str,
            "message": message,
            "duration": int(duration)  # 确保duration是整数
        }
        
        self.reminders.append(reminder)
        
        # 保存到配置
        self.config_manager.save_reminders(self.reminders)
        
        # 更新UI
        self.update_reminder_list()
        self.message_edit.clear()
        
        # 显示通知
        self.tray_icon.showMessage("提醒已添加", f"将在每天 {time_str} 显示提醒 {duration}秒", QSystemTrayIcon.Information, 2000)
    
    def delete_reminder(self):
        """删除选中的提醒"""
        current_row = self.reminder_list.currentRow()
        if current_row >= 0:
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
        
        if self.reminder_screen:
            self.reminder_screen.close()
            self.reminder_screen = None
        
        # 打印调试信息
        logger.info(f"测试提醒: 消息={message}, 时长={duration}秒")
        
        # 创建新的提醒屏幕对象，会在初始化时播放声音
        self.reminder_screen = ReminderScreen(message, int(duration))
        self.reminder_screen.show()
    
    def check_reminders(self):
        """检查是否有到期的提醒"""
        current_time = datetime.now().strftime("%H:%M")
        
        # 防止同一分钟内重复触发提醒
        if current_time == self.last_reminder_time:
            return
        
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                # 记录当前提醒时间，避免重复触发
                self.last_reminder_time = current_time
                
                # 关闭现有提醒（如果有）
                if self.reminder_screen:
                    self.reminder_screen.close()
                    self.reminder_screen = None
                
                # 确保duration是整数
                duration = int(reminder.get("duration", 10))
                message = reminder["message"]
                
                # 创建新的提醒屏幕，会在初始化时播放声音
                self.reminder_screen = ReminderScreen(message, duration)
                self.reminder_screen.show()
                
                # 找到了匹配的提醒，退出循环
                break
