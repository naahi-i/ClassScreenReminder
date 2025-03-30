import os
import sys
import logging
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QMessageBox, QApplication, QFileDialog
from PySide6.QtCore import Qt, QTime, QTimer, QEvent, QObject, QSize, Slot, QUrl
from PySide6.QtGui import QIcon, QAction, QCloseEvent, QPixmap

# 修改导入方式以支持新的目录结构
try:
    # 包内导入
    from .components.reminder_screen import ReminderScreen
    from .components.ui_builder import MainWindowUI
    from .utils.reminder_manager import ReminderManager
    from .utils.autostart_manager import get_autostart_status, set_autostart
    from .config_manager import ConfigManager
    from .utils.wallpaper_manager import WallpaperManager
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
        from src.utils.reminder_manager import ReminderManager
        from src.utils.autostart_manager import get_autostart_status, set_autostart
        from src.config_manager import ConfigManager
        from src.utils.wallpaper_manager import WallpaperManager
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
        
        # 初始化提醒管理器
        self.reminder_manager = ReminderManager(config_manager)
        
        # 初始化UI构建器
        self.ui_builder = MainWindowUI(self)
        
        # 初始化壁纸管理器
        self.wallpaper_manager = WallpaperManager(config_manager)
        
        # 当前显示的提醒屏幕
        self.reminder_screen = None
        
        # 设置检查提醒的定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(10000)  # 每10秒检查一次提醒
        
        # 加载设置
        self.minimize_to_tray = True  # 强制设置为True
        self.start_with_windows = self.config_manager.get_setting("start_with_windows", True)  # 默认True
        self.startup_minimized = self.config_manager.get_startup_minimized()
        
        # 设置UI和托盘
        self.ui_builder.setup_ui()
        self.setup_tray()
        
        # 更新提醒列表
        self.update_reminder_list()
        
        # 确保初始自启动状态正确
        if self.start_with_windows:
            set_autostart(True)
        self.update_autostart_status()
    
    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.ico")
        self.tray_icon.setIcon(QIcon(icon_path))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #202020;
                border: 1px solid #e1e1e1;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #202020;
            }
            QMenu::item:selected {
                background-color: rgba(0, 103, 192, 0.08);
                color: #0067C0;
            }
        """)
        
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
        
        for reminder in self.reminder_manager.get_all_reminders():
            display_text = self.reminder_manager.format_reminder_for_display(reminder)
            self.reminder_list.addItem(display_text)
    
    def add_reminder(self):
        """添加新提醒"""
        time_str = self.time_edit.time().toString("HH:mm")
        message = self.message_edit.toPlainText().strip()
        duration = self.duration_spinbox.value()
        play_sound = self.sound_checkbox.isChecked()
        
        # 获取选中的星期
        weekdays = [checkbox.isChecked() for checkbox in self.weekday_checkboxes]
        
        if not message:
            self.ui_builder.show_warning("警告", "请输入提醒消息")
            return
        
        # 添加提醒
        success, msg = self.reminder_manager.add_reminder(time_str, message, duration, play_sound, weekdays)
        
        if success:
            # 更新UI
            self.update_reminder_list()
            self.message_edit.clear()
        else:
            self.ui_builder.show_warning("添加失败", msg)
    
    def delete_reminder(self):
        """删除选中的提醒"""
        current_row = self.reminder_list.currentRow()
        if current_row >= 0:
            # 获取当前选中的提醒信息
            reminder = self.reminder_manager.get_reminder(current_row)
            time_str = reminder["time"]
            message = reminder["message"].split('\n')[0]  # 只显示第一行
            
            # 显示确认对话框
            reply = self.ui_builder.show_question(
                "确认删除", 
                f"确定要删除以下提醒吗？\n时间: {time_str}\n内容: {message}"
            )
            
            if reply == QMessageBox.Yes:
                success, _ = self.reminder_manager.delete_reminder(current_row)
                if success:
                    self.update_reminder_list()
    
    def test_reminder(self):
        """测试提醒显示效果"""
        # 获取当前时间和测试消息
        message = self.message_edit.toPlainText().strip()
        if not message:
            message = "测试提醒内容"
        
        duration = self.duration_spinbox.value()
        play_sound = self.sound_checkbox.isChecked()
        
        # 获取所有区域的壁纸
        wallpapers = self.wallpaper_manager.get_all_wallpapers()
        
        if self.reminder_screen:
            self.reminder_screen.close()
            self.reminder_screen = None
        
        # 创建新的提醒屏幕对象，传入所有区域的壁纸
        self.reminder_screen = ReminderScreen(message, int(duration), play_sound, wallpapers)
        self.reminder_screen.show()
    
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
            
            # 创建新的提醒屏幕
            self.reminder_screen = ReminderScreen(message, duration, play_sound, wallpapers)
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
    
    def edit_reminder(self):
        """编辑选中的提醒"""
        current_row = self.reminder_list.currentRow()
        if current_row >= 0:
            reminder = self.reminder_manager.get_reminder(current_row)
            
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
            success, _ = self.reminder_manager.delete_reminder(current_row)
            if success:
                # 更新界面
                self.update_reminder_list()
                
                # 提示用户
                self.ui_builder.show_message("编辑提醒", 
                                     "已加载选中的提醒到编辑区域，\n修改后点击「添加提醒」按钮保存。")
    
    def select_wallpaper(self):
        """选择壁纸"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            # 更新配置
            self.reminder_manager.set_wallpaper_path(file_path)
            self.ui_builder.show_message("设置成功", "背景图片已设置，将在下次提醒时显示。")
    
    def clear_wallpaper(self):
        """清除壁纸"""
        self.reminder_manager.set_wallpaper_path("")
        self.ui_builder.show_message("设置成功", "背景图片已清除，将在下次提醒时恢复默认背景。")
    
    def on_area_changed(self, index):
        """区域选择变化时更新显示"""
        area = self.area_combo.currentData()
        self.update_wallpaper_preview(area)
    
    def update_wallpaper_preview(self, area):
        """更新壁纸预览显示"""
        path = self.wallpaper_manager.get_wallpaper(area)
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.wallpaper_preview.setPixmap(pixmap)
                self.path_label.setText(path)
                return
        
        # 没有设置壁纸或加载失败
        self.wallpaper_preview.setText("无背景图片")
        self.wallpaper_preview.setPixmap(QPixmap())
        self.path_label.setText("未选择图片")
    
    def select_area_wallpaper(self):
        """为当前选择的区域选择壁纸"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            area = self.area_combo.currentData()
            if self.wallpaper_manager.set_wallpaper(area, file_path):
                self.update_wallpaper_preview(area)
                self.ui_builder.show_message("设置成功", f"已为 {self.area_combo.currentText()} 设置背景图片")
            else:
                self.ui_builder.show_warning("设置失败", "无法设置背景图片，请确认文件存在且可访问")
    
    def clear_area_wallpaper(self):
        """清除当前选择区域的壁纸"""
        area = self.area_combo.currentData()
        self.wallpaper_manager.clear_wallpaper(area)
        self.update_wallpaper_preview(area)
        self.ui_builder.show_message("操作成功", f"已清除 {self.area_combo.currentText()} 的背景图片")
    
    def clear_all_wallpapers(self):
        """清除所有区域的壁纸"""
        reply = self.ui_builder.show_question(
            "确认操作", 
            "确定要清除所有区域的背景图片吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.wallpaper_manager.clear_wallpaper()
            area = self.area_combo.currentData()
            self.update_wallpaper_preview(area)
            self.ui_builder.show_message("操作成功", "已清除所有区域的背景图片")
    
    def on_menu_changed(self, menu_id):
        """处理菜单切换事件"""
        if menu_id in self.ui_builder.content_pages:
            self.content_stack.setCurrentIndex(self.ui_builder.content_pages[menu_id])
    
    def on_startup_minimized_changed(self, checked):
        """处理启动时最小化设置变更"""
        self.config_manager.set_startup_minimized(checked)
    
    def reset_form(self):
        """重置表单内容"""
        # 时间设为当前时间
        self.time_edit.setTime(QTime.currentTime())
        
        # 持续时间设为默认值
        self.duration_spinbox.setValue(10)
        
        # 声音设置为默认值
        self.sound_checkbox.setChecked(True)
        
        # 所有星期都选中
        for checkbox in self.weekday_checkboxes:
            checkbox.setChecked(True)
        
        # 清空消息内容
        self.message_edit.clear()
        
        # 提示用户
        self.ui_builder.show_message("操作完成", "表单已重置为默认值")