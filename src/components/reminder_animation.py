from PySide6.QtCore import QRect, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QGuiApplication

class ReminderAnimator:
    """负责提醒屏幕的所有动画效果管理"""
    
    def __init__(self, parent):
        self.parent = parent
        self.ui = parent.ui
        
        # 保存动画对象
        self.enter_animations = {}
        self.exit_animations = {}
        
        # 获取屏幕尺寸
        self.screen_size = QGuiApplication.primaryScreen().size()
    
    def start_animations(self):
        """开始入场动画"""
        # 背景模糊层淡入
        anim_backdrop = QPropertyAnimation(self.ui.backdrop, b"geometry")
        anim_backdrop.setDuration(800)
        anim_backdrop.setStartValue(QRect(0, 0, 0, self.screen_size.height()))
        anim_backdrop.setEndValue(QRect(0, 0, self.screen_size.width(), self.screen_size.height()))
        anim_backdrop.setEasingCurve(QEasingCurve.OutQuint)
        
        # 色块A从顶部向底部延伸
        anim_a = QPropertyAnimation(self.ui.block_a, b"geometry")
        anim_a.setDuration(1100)
        anim_a.setStartValue(QRect(0, 0, self.ui.block_a_width, 0))
        anim_a.setEndValue(QRect(0, 0, self.ui.block_a_width, self.screen_size.height()))
        anim_a.setEasingCurve(QEasingCurve.OutQuint)
        
        # 色块B从左向右延伸
        anim_b = QPropertyAnimation(self.ui.block_b, b"geometry")
        anim_b.setDuration(1200)
        anim_b.setStartValue(QRect(0, 0, 0, self.screen_size.height()))
        anim_b.setEndValue(QRect(0, 0, self.screen_size.width(), self.screen_size.height()))
        anim_b.setEasingCurve(QEasingCurve.OutQuart)
        
        # 色块C从右向左延展到色块A的右边界
        anim_c = QPropertyAnimation(self.ui.block_c, b"geometry")
        anim_c.setDuration(1100)
        anim_c.setStartValue(QRect(self.screen_size.width(), 0, 0, self.screen_size.height() // 2))
        anim_c.setEndValue(QRect(self.ui.block_a_width, 0, self.screen_size.width() - self.ui.block_a_width, self.screen_size.height() // 2))
        anim_c.setEasingCurve(QEasingCurve.OutQuint)
        
        # 装饰条动画
        anim_accent = QPropertyAnimation(self.ui.accent_line, b"geometry")
        anim_accent.setDuration(1000)
        anim_accent.setStartValue(QRect(self.screen_size.width(), self.screen_size.height() // 2 - 7, 0, 14))
        anim_accent.setEndValue(QRect(self.ui.block_a_width, self.screen_size.height() // 2 - 7, self.screen_size.width() - self.ui.block_a_width, 14))
        anim_accent.setEasingCurve(QEasingCurve.OutQuint)
        
        # 保存动画对象
        self.enter_animations = {
            'backdrop': anim_backdrop,
            'a': anim_a,
            'b': anim_b,
            'c': anim_c,
            'accent': anim_accent
        }
        
        # 设置最后一个动画完成时的回调
        anim_accent.finished.connect(self.on_enter_animations_finished)
        
        # 启动动画序列
        anim_backdrop.start()  # 先启动背景
        
        # 使用错位效果启动其他动画
        QTimer.singleShot(150, lambda: self.enter_animations['a'].start())
        QTimer.singleShot(350, lambda: self.enter_animations['b'].start())
        QTimer.singleShot(600, lambda: self.enter_animations['c'].start())
        QTimer.singleShot(800, lambda: self.enter_animations['accent'].start())
    
    def on_enter_animations_finished(self):
        """入场动画完成时的回调"""
        self.parent.is_entering = False
    
    def start_close_animation(self):
        """开始退场动画"""
        # 如果已经在关闭中，则不重复触发
        if self.parent.is_closing:
            return
            
        # 如果入场动画还在进行中，则等待入场动画完成后再关闭
        if self.parent.is_entering:
            # 只设置关闭定时器，不立即关闭
            QTimer.singleShot(200, self.check_and_start_close)
            return
            
        # 设置关闭状态标志
        self.parent.is_closing = True
        
        # 停止声音定时器
        self.parent.sound_repeat_timer.stop()
        
        # 先开始名片退场动画
        self.ui.start_cards_exit_animation()
        
        # 延迟一小段时间后开始其他组件的退场动画
        QTimer.singleShot(300, self.start_main_close_animation)
    
    def start_main_close_animation(self):
        """开始主要组件的退场动画"""
        # 色块C从当前位置收缩回屏幕右侧
        anim_c = QPropertyAnimation(self.ui.block_c, b"geometry")
        anim_c.setDuration(800)
        anim_c.setStartValue(QRect(self.ui.block_a_width, 0, self.screen_size.width() - self.ui.block_a_width, self.screen_size.height() // 2))
        anim_c.setEndValue(QRect(self.screen_size.width(), 0, 0, self.screen_size.height() // 2))
        anim_c.setEasingCurve(QEasingCurve.InQuint)
        
        # 色块A从上向下收缩
        anim_a = QPropertyAnimation(self.ui.block_a, b"geometry")
        anim_a.setDuration(900)
        anim_a.setStartValue(QRect(0, 0, self.ui.block_a_width, self.screen_size.height()))
        anim_a.setEndValue(QRect(0, self.screen_size.height(), self.ui.block_a_width, 0))
        anim_a.setEasingCurve(QEasingCurve.InQuint)
        
        # 色块B从左向右收缩
        anim_b = QPropertyAnimation(self.ui.block_b, b"geometry")
        anim_b.setDuration(1000)
        anim_b.setStartValue(QRect(0, 0, self.screen_size.width(), self.screen_size.height()))
        anim_b.setEndValue(QRect(self.screen_size.width(), 0, 0, self.screen_size.height()))
        anim_b.setEasingCurve(QEasingCurve.InQuint)
        
        # 背景模糊层淡出
        anim_backdrop = QPropertyAnimation(self.ui.backdrop, b"geometry")
        anim_backdrop.setDuration(1100)
        anim_backdrop.setStartValue(QRect(0, 0, self.screen_size.width(), self.screen_size.height()))
        anim_backdrop.setEndValue(QRect(self.screen_size.width(), 0, 0, self.screen_size.height()))
        anim_backdrop.setEasingCurve(QEasingCurve.InCubic)
        
        # 装饰条退出动画
        anim_accent = QPropertyAnimation(self.ui.accent_line, b"geometry")
        anim_accent.setDuration(1500)
        anim_accent.setStartValue(QRect(self.ui.block_a_width, self.screen_size.height() // 2 - 7, self.screen_size.width() - self.ui.block_a_width, 14))
        anim_accent.setEndValue(QRect(self.screen_size.width(), self.screen_size.height() // 2 - 7, 0, 14))
        anim_accent.setEasingCurve(QEasingCurve.InQuint)
        
        # 保存动画对象
        self.exit_animations = {
            'accent': anim_accent,
            'c': anim_c,
            'a': anim_a,
            'b': anim_b,
            'backdrop': anim_backdrop
        }
        
        # 设置最后一个动画结束时关闭窗口
        anim_backdrop.finished.connect(self.parent.close)
        
        # 开始退出动画序列
        anim_accent.start()  # 先启动装饰条退出
        QTimer.singleShot(200, lambda: self.exit_animations['c'].start())
        QTimer.singleShot(400, lambda: self.exit_animations['a'].start())
        QTimer.singleShot(600, lambda: self.exit_animations['b'].start())
        QTimer.singleShot(800, lambda: self.exit_animations['backdrop'].start())
    
    def check_and_start_close(self):
        """检查入场动画是否完成，然后开始退场动画"""
        if not self.parent.is_entering:
            self.start_close_animation()
        else:
            # 继续等待
            QTimer.singleShot(200, self.check_and_start_close)
