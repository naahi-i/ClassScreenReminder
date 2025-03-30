import logging
from datetime import datetime
from PySide6.QtCore import QTime, QObject, Signal

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ReminderManager")

class ReminderManager(QObject):
    """提醒管理器，处理提醒的添加、编辑、删除和检查"""
    
    # 定义信号
    reminder_added = Signal()
    reminder_deleted = Signal(int)  # 参数为被删除的提醒索引
    reminder_edited = Signal(int)   # 参数为被编辑的提醒索引
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.reminders = self.config_manager.load_reminders()
        self.last_reminder_time = ""
        self.wallpaper_path = self.config_manager.get_wallpaper_path()
    
    def get_all_reminders(self):
        """获取所有提醒"""
        return self.reminders
    
    def add_reminder(self, time_str, message, duration, play_sound, weekdays):
        """添加新提醒"""
        # 确保必填项不为空
        if not message:
            return False, "提醒消息不能为空"
        
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
        
        # 发出信号
        self.reminder_added.emit()
        
        return True, "提醒已添加"
    
    def delete_reminder(self, index):
        """删除提醒"""
        if 0 <= index < len(self.reminders):
            del self.reminders[index]
            self.config_manager.save_reminders(self.reminders)
            self.reminder_deleted.emit(index)
            return True, "提醒已删除"
        return False, "无效的提醒索引"
    
    def get_reminder(self, index):
        """获取指定索引的提醒"""
        if 0 <= index < len(self.reminders):
            return self.reminders[index]
        return None
    
    def check_reminders(self):
        """检查是否有到期的提醒"""
        current_time = datetime.now().strftime("%H:%M")
        current_weekday = datetime.now().weekday()  # 0是周一，6是周日
        
        # 防止同一分钟内重复触发提醒
        if current_time == self.last_reminder_time:
            return None
        
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                # 检查当前星期是否启用
                weekdays = reminder.get("weekdays", [True] * 7)
                if not weekdays[current_weekday]:
                    # 当前星期未启用此提醒，跳过
                    continue
                
                # 记录当前提醒时间，避免重复触发
                self.last_reminder_time = current_time
                
                # 返回匹配的提醒
                return reminder
        
        return None
    
    def create_time_from_string(self, time_str):
        """从字符串创建QTime对象"""
        return QTime.fromString(time_str, "HH:mm")
    
    def format_reminder_for_display(self, reminder):
        """格式化提醒用于显示"""
        time_str = reminder["time"]
        message = reminder["message"]
        duration = reminder["duration"]
        play_sound = reminder.get("play_sound", True)
        weekdays = reminder.get("weekdays", [True] * 7)
        
        lines_count = message.count('\n') + 1
        
        # 在列表中只显示消息的第一行，如果有多行则添加行数信息
        if "\n" in message:
            first_line = message.split("\n")[0]
            display_message = f"{first_line}... ({lines_count}行)"
        else:
            display_message = message
        
        # 星期缩写
        weekday_abbrs = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_str = ""
        for i, enabled in enumerate(weekdays):
            if enabled:
                weekday_str += weekday_abbrs[i]
        
        weekday_display = f"[{weekday_str}]" if weekday_str else "[无]"
        sound_status = "有声音" if play_sound else "静音"
        
        return f"{time_str} {weekday_display} - {display_message} ({duration}秒) [{sound_status}]"
    
    def get_wallpaper_path(self):
        """获取壁纸路径"""
        return self.wallpaper_path
    
    def set_wallpaper_path(self, path):
        """设置壁纸路径"""
        self.wallpaper_path = path
        self.config_manager.set_wallpaper_path(path)
