import os
import logging
import time
import sys
from datetime import datetime
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QGuiApplication, QColor

# 处理导入问题 - 支持直接运行此文件和作为包的一部分导入
try:
    # 尝试相对导入 (当作为包的一部分导入时)
    from ..utils.sound_manager import play_initial_sound, initialize_sound, _is_second_sound_playing
    from .ui_components import ColorBlock, LightEffectBlock
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
    except ImportError as e:
        print(f"导入错误: {e}")
        sys.exit(1)

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ReminderScreen")

class ReminderScreen(QWidget):
    """全屏提醒窗口类"""
    
    def __init__(self, message, duration=10, play_sound=True, wallpapers=None):
        super().__init__()
        self.message = message
        self.play_sound = play_sound  # 保存声音设置
        self.wallpapers = wallpapers or {}  # 保存壁纸设置，字典格式 {区域: 路径}
        
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
        
        # 保存所有动画
        self.enter_animations = {}
        self.exit_animations = {}
        
        # 添加状态标志
        self.is_closing = False
        self.is_entering = True  # 标记正在播放入场动画
        self.click_count = 0     # 点击计数
        self.last_click_time = 0 # 上次点击时间
        
        # 重复播放计时器
        self.sound_repeat_timer = QTimer(self)
        self.sound_repeat_timer.timeout.connect(self.play_sound_group)
        if self.play_sound:  # 仅在启用声音时启动计时器
            self.sound_repeat_timer.start(4000)
        
        self.setup_ui()
        self.start_animations()
        
        # 定时关闭
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.start_close_animation)
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
    
    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取屏幕尺寸并设置窗口全屏
        screen_size = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        
        # 计算色块A的宽度
        self.block_a_width = screen_size.width() // 5
        
        # 创建背景模糊遮罩层 - 不设置壁纸，只作为整体背景
        self.backdrop = ColorBlock("rgba(0, 25, 50, 0.2)", self, radius=0, opacity=0.2)
        self.backdrop.setGeometry(0, 0, 0, screen_size.height())
        
        # 创建色块B（底层，深蓝色，带圆角）- 对应主背景区域
        opacity_b = 0.85
        self.block_b = ColorBlock("#0B5394", self, radius=5, opacity=opacity_b)  # 高级蓝
        self.block_b.setGeometry(0, 0, 0, screen_size.height())  # 初始宽度为0
        
        # 如果有主区域壁纸，设置背景图片
        if "main" in self.wallpapers and os.path.exists(self.wallpapers["main"]):
            self.block_b.set_background_image(self.wallpapers["main"])
            # 当设置了壁纸时稍微增加透明度，让壁纸更明显
            self.block_b.color.setAlphaF(0.7)
        
        # 创建色块A（左侧五分之一，上层，更深的蓝色，带圆角）
        opacity_a = 0.95
        self.block_a = ColorBlock("#073763", self, radius=5, opacity=opacity_a)
        
        # 如果有左侧区域壁纸，设置背景图片
        if "left" in self.wallpapers and os.path.exists(self.wallpapers["left"]):
            self.block_a.set_background_image(self.wallpapers["left"])
            # 当设置了壁纸时稍微增加透明度
            self.block_a.color.setAlphaF(0.7)
        
        # 设置几何尺寸，初始高度为0用于动画效果
        self.block_a.setGeometry(0, 0, self.block_a_width, 0)
        self.block_a.raise_()  # 确保色块A位于上层
        
        # 创建色块C（中间层，湖蓝色，带圆角）
        opacity_c = 0.90
        self.block_c = ColorBlock("#8EACCD", self, radius=5, opacity=opacity_c)  # 湖蓝色
        self.block_c.setGeometry(screen_size.width(), 0, 0, screen_size.height() // 2)  # 初始宽度为0
        
        # 如果有中间区域壁纸，设置背景图片
        if "top" in self.wallpapers and os.path.exists(self.wallpapers["top"]):
            self.block_c.set_background_image(self.wallpapers["top"])
            # 当设置了壁纸时稍微增加透明度
            self.block_c.color.setAlphaF(0.7)
        
        self.block_c.stackUnder(self.block_a)  # 确保色块C在A下B上
        
        # 创建装饰条 - 亮蓝色
        opacity_accent = 0.9
        self.accent_line = LightEffectBlock("#4FC3F7", self, radius=4, opacity=opacity_accent)  # 亮蓝色
        
        # 如果有装饰区域壁纸，设置背景图片
        if "accent" in self.wallpapers and os.path.exists(self.wallpapers["accent"]):
            self.accent_line.set_background_image(self.wallpapers["accent"])
            # 当设置了壁纸时稍微增加透明度
            self.accent_line.color.setAlphaF(0.7)
        
        self.accent_line.setGeometry(screen_size.width(), screen_size.height() // 2 - 7, 0, 14)
        self.accent_line.raise_()
        
        # 创建时间显示
        current_time = datetime.now().strftime("%H:%M")  # 去掉秒数
        
        # 时间容器
        time_width = screen_size.width() * 2 // 5  # 宽度适中
        time_height = 190
        time_x = self.block_a_width + (screen_size.width() - self.block_a_width - time_width) // 2
        time_y = screen_size.height() // 4 - time_height // 2
        
        # 创建时间标签
        self.time_label = QLabel(current_time, self.block_c)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            color: white;
            font-size: 160px;
            font-weight: 700;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            letter-spacing: 8px;
        """)
        self.time_label.setGeometry(time_x, time_y, time_width, time_height)
        
        # 创建发光效果
        glow = QGraphicsDropShadowEffect(self.time_label)
        glow.setBlurRadius(20)  # 模糊半径
        glow.setColor(QColor(255, 255, 255, 200))  # 白色发光
        glow.setOffset(0, 0)  # 无偏移
        self.time_label.setGraphicsEffect(glow)
        
        self.time_label.raise_()
        
        # 创建文字内容
        message_width = screen_size.width() * 3 // 5
        message_height = 300
        message_x = (screen_size.width() - message_width) // 2 + 50  # 调整为更居中位置
        message_y = screen_size.height() * 3 // 5  # 调整为屏幕中下方，更居中
        
        # 创建一个透明容器用于放置消息
        self.message_container = QFrame(self.block_b)
        self.message_container.setGeometry(message_x, message_y, message_width, message_height)
        self.message_container.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        
        # 为消息容器创建垂直布局
        message_layout = QVBoxLayout(self.message_container)
        message_layout.setContentsMargins(35, 5, 20, 5)
        message_layout.setSpacing(12)  # 行间距
        
        # 创建左侧装饰条
        decoration_width = 8
        self.message_decoration = ColorBlock("#2196F3", self.message_container, radius=4, opacity=0.9)
        self.message_decoration.setGeometry(0, 0, decoration_width, message_height)
        self.message_decoration.raise_()
        
        # 处理多行消息
        message_lines = self.message.split('\n')
        
        # 动态创建多个标签以支持多行
        for i, line in enumerate(message_lines):
            msg_label = QLabel(line, self.message_container)
            msg_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            msg_label.setStyleSheet(f"""
                color: white;
                font-size: {48 if len(message_lines) <= 2 else 42}px;  /* 稍微减小字体 */
                font-weight: 600;  /* 增加粗细 */
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                letter-spacing: 1px;
                background-color: transparent;
                padding: 8px 0px;
            """)
            
            # 创建文本阴影效果
            text_shadow = QGraphicsDropShadowEffect(msg_label)
            text_shadow.setBlurRadius(2)
            text_shadow.setColor(QColor(0, 0, 0, 170))
            text_shadow.setOffset(1, 1)
            msg_label.setGraphicsEffect(text_shadow)
            
            msg_label.setWordWrap(True)
            message_layout.addWidget(msg_label)
        
        # 添加提示信息
        self.hint_label = QLabel("双击或按ESC键关闭", self)
        self.hint_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.hint_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            letter-spacing: 0.5px;
            padding: 24px;
            background-color: transparent;
        """)
        self.hint_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
    
    def start_animations(self):
        """开始入场动画"""
        screen_size = QGuiApplication.primaryScreen().size()
        
        # 背景模糊层淡入
        anim_backdrop = QPropertyAnimation(self.backdrop, b"geometry")
        anim_backdrop.setDuration(800)
        anim_backdrop.setStartValue(QRect(0, 0, 0, screen_size.height()))
        anim_backdrop.setEndValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_backdrop.setEasingCurve(QEasingCurve.OutQuint)
        
        # 色块A从顶部向底部延伸
        anim_a = QPropertyAnimation(self.block_a, b"geometry")
        anim_a.setDuration(1100)
        anim_a.setStartValue(QRect(0, 0, self.block_a_width, 0))
        anim_a.setEndValue(QRect(0, 0, self.block_a_width, screen_size.height()))
        anim_a.setEasingCurve(QEasingCurve.OutQuint)
        
        # 色块B从左向右延伸
        anim_b = QPropertyAnimation(self.block_b, b"geometry")
        anim_b.setDuration(1200)
        anim_b.setStartValue(QRect(0, 0, 0, screen_size.height()))
        anim_b.setEndValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_b.setEasingCurve(QEasingCurve.OutQuart)
        
        # 色块C从右向左延展到色块A的右边界
        anim_c = QPropertyAnimation(self.block_c, b"geometry")
        anim_c.setDuration(1100)
        anim_c.setStartValue(QRect(screen_size.width(), 0, 0, screen_size.height() // 2))
        anim_c.setEndValue(QRect(self.block_a_width, 0, screen_size.width() - self.block_a_width, screen_size.height() // 2))
        anim_c.setEasingCurve(QEasingCurve.OutQuint)
        
        # 添加装饰条动画
        anim_accent = QPropertyAnimation(self.accent_line, b"geometry")
        anim_accent.setDuration(1000)
        anim_accent.setStartValue(QRect(screen_size.width(), screen_size.height() // 2 - 7, 0, 14))
        anim_accent.setEndValue(QRect(self.block_a_width, screen_size.height() // 2 - 7, screen_size.width() - self.block_a_width, 14))
        anim_accent.setEasingCurve(QEasingCurve.OutQuint)
        
        # 保存动画对象
        self.enter_animations = {
            'backdrop': anim_backdrop,
            'a': anim_a,
            'b': anim_b,
            'c': anim_c,
            'accent': anim_accent
        }
        
        # 设置最后一个动画完成时的回调，标记入场动画完成
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
        self.is_entering = False
    
    def start_close_animation(self):
        """开始退场动画"""
        # 如果已经在关闭中，则不重复触发
        if self.is_closing:
            return
            
        # 如果入场动画还在进行中，则等待入场动画完成后再关闭
        if self.is_entering:
            # 只设置关闭定时器，不立即关闭
            QTimer.singleShot(200, self.check_and_start_close)
            return
            
        # 设置关闭状态标志
        self.is_closing = True
        
        # 停止声音定时器
        self.sound_repeat_timer.stop()
        
        screen_size = QGuiApplication.primaryScreen().size()
        
        # 色块C从当前位置收缩回屏幕右侧
        anim_c = QPropertyAnimation(self.block_c, b"geometry")
        anim_c.setDuration(800)
        anim_c.setStartValue(QRect(self.block_a_width, 0, screen_size.width() - self.block_a_width, screen_size.height() // 2))
        anim_c.setEndValue(QRect(screen_size.width(), 0, 0, screen_size.height() // 2))
        anim_c.setEasingCurve(QEasingCurve.InQuint)
        
        # 色块A从上向下收缩
        anim_a = QPropertyAnimation(self.block_a, b"geometry")
        anim_a.setDuration(900)
        anim_a.setStartValue(QRect(0, 0, self.block_a_width, screen_size.height()))
        anim_a.setEndValue(QRect(0, screen_size.height(), self.block_a_width, 0))
        anim_a.setEasingCurve(QEasingCurve.InQuint)
        
        # 色块B从左向右收缩
        anim_b = QPropertyAnimation(self.block_b, b"geometry")
        anim_b.setDuration(1000)
        anim_b.setStartValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_b.setEndValue(QRect(screen_size.width(), 0, 0, screen_size.height()))
        anim_b.setEasingCurve(QEasingCurve.InQuint)
        
        # 背景模糊层淡出
        anim_backdrop = QPropertyAnimation(self.backdrop, b"geometry")
        anim_backdrop.setDuration(1100)
        anim_backdrop.setStartValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_backdrop.setEndValue(QRect(screen_size.width(), 0, 0, screen_size.height()))
        anim_backdrop.setEasingCurve(QEasingCurve.InCubic)
        
        # 添加装饰条退出动画
        anim_accent = QPropertyAnimation(self.accent_line, b"geometry")
        anim_accent.setDuration(1500)
        anim_accent.setStartValue(QRect(self.block_a_width, screen_size.height() // 2 - 7, screen_size.width() - self.block_a_width, 14))
        anim_accent.setEndValue(QRect(screen_size.width(), screen_size.height() // 2 - 7, 0, 14))
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
        anim_backdrop.finished.connect(self.close)
        
        # 开始退出动画序列
        anim_accent.start()  # 先启动装饰条退出
        QTimer.singleShot(200, lambda: self.exit_animations['c'].start())
        QTimer.singleShot(400, lambda: self.exit_animations['a'].start())
        QTimer.singleShot(600, lambda: self.exit_animations['b'].start())
        QTimer.singleShot(800, lambda: self.exit_animations['backdrop'].start())
    
    def check_and_start_close(self):
        """检查入场动画是否完成，然后开始退场动画"""
        if not self.is_entering:
            self.start_close_animation()
        else:
            # 继续等待
            QTimer.singleShot(200, self.check_and_start_close)
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，改为双击关闭"""
        current_time = time.time()
        
        # 如果是快速双击（时间间隔小于500毫秒）
        if current_time - self.last_click_time < 0.5:
            self.click_count += 1
            if self.click_count >= 2:  # 双击检测
                self.click_count = 0
                self.close_timer.stop()
                self.sound_repeat_timer.stop()  # 停止声音重复播放
                self.start_close_animation()
        else:
            # 重置点击计数
            self.click_count = 1
        
        self.last_click_time = current_time
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        """处理按键事件，ESC仍然可以直接关闭"""
        if event.key() == Qt.Key_Escape:
            self.close_timer.stop()
            self.sound_repeat_timer.stop()  # 停止声音重复播放
            self.start_close_animation()
        super().keyPressEvent(event)