from PySide6.QtCore import QTime, QObject
from PySide6.QtWidgets import QMessageBox

class ReminderManagerUI:
    """提醒管理界面相关功能"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_builder = main_window.ui_builder
        self.reminder_manager = main_window.reminder_manager
    
    def update_reminder_list(self):
        """更新提醒列表显示"""
        self.main_window.reminder_list.clear()
        
        for reminder in self.reminder_manager.get_all_reminders():
            display_text = self.reminder_manager.format_reminder_for_display(reminder)
            self.main_window.reminder_list.addItem(display_text)
    
    def add_reminder(self):
        """添加新提醒"""
        time_str = self.main_window.time_edit.time().toString("HH:mm")
        message = self.main_window.message_edit.toPlainText().strip()
        duration = self.main_window.duration_spinbox.value()
        play_sound = self.main_window.sound_checkbox.isChecked()
        
        # 获取选中的星期
        weekdays = [checkbox.isChecked() for checkbox in self.main_window.weekday_checkboxes]
        
        if not message:
            self.ui_builder.show_warning("警告", "请输入提醒消息")
            return
        
        # 添加提醒
        success, msg = self.reminder_manager.add_reminder(time_str, message, duration, play_sound, weekdays)
        
        if success:
            # 更新UI
            self.update_reminder_list()
            self.main_window.message_edit.clear()
        else:
            self.ui_builder.show_warning("添加失败", msg)
    
    def delete_reminder(self):
        """删除选中的提醒"""
        current_row = self.main_window.reminder_list.currentRow()
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
    
    def edit_reminder(self):
        """编辑选中的提醒"""
        current_row = self.main_window.reminder_list.currentRow()
        if current_row >= 0:
            reminder = self.reminder_manager.get_reminder(current_row)
            
            # 设置界面值为当前选中的提醒
            self.main_window.time_edit.setTime(QTime.fromString(reminder["time"], "HH:mm"))
            self.main_window.message_edit.setText(reminder["message"])
            self.main_window.duration_spinbox.setValue(reminder["duration"])
            self.main_window.sound_checkbox.setChecked(reminder.get("play_sound", True))
            
            # 设置星期复选框
            weekdays = reminder.get("weekdays", [True] * 7)
            for i, checkbox in enumerate(self.main_window.weekday_checkboxes):
                checkbox.setChecked(weekdays[i] if i < len(weekdays) else True)
            
            # 删除当前提醒
            success, _ = self.reminder_manager.delete_reminder(current_row)
            if success:
                # 更新界面
                self.update_reminder_list()
                
                # 提示用户
                self.ui_builder.show_message("编辑提醒", 
                                     "已加载选中的提醒到编辑区域，\n修改后点击「添加提醒」按钮保存。")
    
    def test_reminder(self):
        """测试提醒显示效果"""
        from src.components.reminder_screen import ReminderScreen
        
        # 获取当前时间和测试消息
        message = self.main_window.message_edit.toPlainText().strip()
        if not message:
            message = "测试提醒内容"
        
        duration = self.main_window.duration_spinbox.value()
        play_sound = self.main_window.sound_checkbox.isChecked()
        
        # 获取所有区域的壁纸
        wallpapers = self.main_window.wallpaper_manager.get_all_wallpapers()
        
        if self.main_window.reminder_screen:
            self.main_window.reminder_screen.close()
            self.main_window.reminder_screen = None
        
        # 创建新的提醒屏幕对象，传入所有区域的壁纸
        self.main_window.reminder_screen = ReminderScreen(message, int(duration), play_sound, wallpapers)
        self.main_window.reminder_screen.show()
    
    def reset_form(self):
        """重置表单内容"""
        # 时间设为当前时间
        self.main_window.time_edit.setTime(QTime.currentTime())
        
        # 持续时间设为默认值
        self.main_window.duration_spinbox.setValue(10)
        
        # 声音设置为默认值
        self.main_window.sound_checkbox.setChecked(True)
        
        # 所有星期都选中
        for checkbox in self.main_window.weekday_checkboxes:
            checkbox.setChecked(True)
        
        # 清空消息内容
        self.main_window.message_edit.clear()

        self.ui_builder.show_message("操作完成", "表单已重置为默认值")