import time
from PySide6.QtCore import Qt

class ReminderEventHandler:
    """负责处理提醒屏幕的鼠标和键盘事件"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def handle_mouse_press(self, event):
        """处理鼠标点击事件，实现双击关闭功能"""
        current_time = time.time()
        
        # 如果是快速双击（时间间隔小于500毫秒）
        if current_time - self.parent.last_click_time < 0.5:
            self.parent.click_count += 1
            if self.parent.click_count >= 2:  # 双击检测
                self.parent.click_count = 0
                self.parent.close_timer.stop()
                self.parent.sound_repeat_timer.stop()  # 停止声音重复播放
                self.parent.animator.start_close_animation()
        else:
            # 重置点击计数
            self.parent.click_count = 1
        
        self.parent.last_click_time = current_time
    
    def handle_key_press(self, event):
        """处理按键事件，ESC键关闭窗口"""
        if event.key() == Qt.Key_Escape:
            self.parent.close_timer.stop()
            self.parent.sound_repeat_timer.stop()  # 停止声音重复播放
            self.parent.animator.start_close_animation()
