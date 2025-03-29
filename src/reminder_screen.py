"""
提醒全屏显示类 - 处理全屏提醒动画和显示
"""
import os
import logging
import time
from datetime import datetime
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QUrl
from PySide6.QtGui import QGuiApplication, QColor, QPainter, QPainterPath, QBrush
from PySide6.QtMultimedia import QSoundEffect

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ReminderScreen")

# 全局声音对象，防止垃圾回收
_global_sound = None
_global_timer = None
_sound_is_initialized = False  # 跟踪声音是否已初始化
_last_play_time = 0  # 上次播放时间
_is_second_sound_playing = False  # 跟踪是否正在播放第二个声音

def initialize_sound():
    """初始化全局声音对象（应在应用启动时调用）"""
    global _global_sound, _sound_is_initialized
    
    if _sound_is_initialized:
        return True
    
    try:
        # 创建声音对象
        sound_effect = QSoundEffect()
        
        # 获取声音文件路径
        sound_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "resources", 
            "attend_class.wav"
        )
        
        # 检查文件是否存在
        if os.path.exists(sound_path):
            sound_effect.setSource(QUrl.fromLocalFile(sound_path))
            sound_effect.setVolume(1.0)
            
            # 强制加载但不播放
            sound_effect.setLoopCount(0)  # 不循环播放
            
            # 保存对象到全局变量，防止被垃圾回收
            _global_sound = sound_effect
            _sound_is_initialized = True
            
            print("声音资源初始化成功")
            return True
        else:
            print(f"找不到声音文件: {sound_path}")
            logger.warning(f"找不到声音文件: {sound_path}")
            return False
    except Exception as e:
        print(f"初始化声音时出错：{e}")
        logger.error(f"初始化声音时出错：{e}")
        return False

def play_initial_sound():
    """播放第一组声音（避免重复播放）"""
    global _global_sound, _global_timer, _last_play_time, _is_second_sound_playing
    
    # 如果声音没有初始化，先初始化
    if not _sound_is_initialized:
        if not initialize_sound():
            return False
    
    # 检查是否太频繁播放（至少间隔1秒）
    current_time = time.time()
    if current_time - _last_play_time < 1.0 and not _is_second_sound_playing:
        print(f"播放太频繁，忽略此次播放请求")
        return False
    
    try:
        if _global_sound and _global_sound.isLoaded():
            # 记录播放时间
            _last_play_time = current_time
            
            # 确保没有正在播放的声音
            if _global_sound.isPlaying() and not _is_second_sound_playing:
                _global_sound.stop()
            
            # 播放第一次声音
            _global_sound.play()
            
            # 设置标志，表示接下来将播放第二个声音
            _is_second_sound_playing = True
            
            # 定时器延迟800毫秒播放第二次声音
            if _global_timer:
                _global_timer.stop()
            
            _global_timer = QTimer()
            _global_timer.setSingleShot(True)
            
            # 创建独立函数处理第二次播放
            def play_second():
                global _is_second_sound_playing
                try:
                    if _global_sound and _global_sound.isLoaded():
                        _global_sound.play()
                        # 播放完第二个声音后，重置标志
                        _is_second_sound_playing = False
                except Exception as e:
                    print(f"播放第二次声音时出错：{e}")
                    _is_second_sound_playing = False
            
            _global_timer.timeout.connect(play_second)
            _global_timer.start(400)  # 800毫秒间隔
            
            return True
        else:
            print("全局声音对象未加载")
            return False
    except Exception as e:
        print(f"播放初始声音时出错：{e}")
        logger.error(f"播放初始声音时出错：{e}")
        _is_second_sound_playing = False
        return False

class ColorBlock(QFrame):
    """自定义颜色块组件，支持圆角和半透明效果"""
    def __init__(self, color, parent=None, radius=0, opacity=1.0):
        super().__init__(parent)
        self.color = QColor(color)
        self.color.setAlphaF(opacity)  # 设置透明度
        self.radius = radius
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        """重写绘制事件以支持圆角矩形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        
        painter.setClipPath(path)
        painter.fillPath(path, QBrush(self.color))
        
        super().paintEvent(event)

class LightEffectBlock(QFrame):
    """装饰条组件"""
    def __init__(self, color, parent=None, radius=0, opacity=1.0):
        super().__init__(parent)
        self.color = QColor(color)
        self.color.setAlphaF(opacity)
        self.radius = radius
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        """重写绘制事件以支持圆角矩形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        
        painter.setClipPath(path)
        painter.fillPath(path, QBrush(self.color))
        
        super().paintEvent(event)

class ReminderScreen(QWidget):
    """全屏提醒窗口类"""
    
    def __init__(self, message, duration=10):
        # 在创建窗口前先播放声音
        play_initial_sound()
        
        super().__init__()
        # 支持多条消息（通过换行符分隔）
        self.message = message
        
        # 确保duration是整数并且大于0
        try:
            self.duration = max(1, int(duration))
        except (ValueError, TypeError):
            logger.warning(f"无效的显示时长: {duration}，使用默认值10秒")
            self.duration = 10
        
        # 保存所有动画，方便后续引用
        self.enter_animations = {}
        self.exit_animations = {}
        
        # 重复播放计时器
        self.sound_repeat_timer = QTimer(self)
        self.sound_repeat_timer.timeout.connect(self.play_sound_group)
        self.sound_repeat_timer.start(4000)  # 每4秒播放一组
        
        self.setup_ui()
        self.start_animations()
        
        # 定时关闭
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.start_close_animation)
        self.close_timer.setSingleShot(True)
        self.close_timer.start(self.duration * 1000)  # 转换为毫秒
    
    def play_sound_group(self):
        """播放一组提示音（两次连续播放）- 使用全局声音对象"""
        # 每次调用此方法时，都尝试播放一组声音
        global _is_second_sound_playing
        
        # 确保不是在播放第二个声音
        if not _is_second_sound_playing:
            play_initial_sound()  # 复用初始播放逻辑
    
    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取屏幕尺寸并设置窗口全屏
        screen_size = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        
        # 计算色块A的宽度 - 将在动画中使用
        self.block_a_width = screen_size.width() // 5
        
        # 创建背景模糊遮罩层 - 蓝色系
        self.backdrop = ColorBlock("rgba(0, 25, 50, 0.2)", self, radius=0, opacity=0.2)
        self.backdrop.setGeometry(0, 0, 0, screen_size.height())
        
        # 创建色块B（底层，深蓝色，带圆角）
        self.block_b = ColorBlock("#0B5394", self, radius=5, opacity=0.95)  # 高级蓝
        self.block_b.setGeometry(0, 0, 0, screen_size.height())  # 初始宽度为0
        
        # 创建色块A（左侧五分之一，上层，更深的蓝色，带圆角）
        self.block_a = ColorBlock("#073763", self, radius=5, opacity=0.95)  # 深蓝色
        self.block_a.setGeometry(0, 0, self.block_a_width, 0)  # 初始高度为0
        self.block_a.raise_()  # 确保色块A位于上层
        
        # 创建色块C（中间层，湖蓝色，带圆角）
        self.block_c = ColorBlock("#8EACCD", self, radius=5, opacity=0.90)  # 湖蓝色
        self.block_c.setGeometry(screen_size.width(), 0, 0, screen_size.height() // 2)  # 初始宽度为0
        self.block_c.stackUnder(self.block_a)  # 确保色块C在A下B上
        
        # 创建装饰条 - 亮蓝色
        self.accent_line = LightEffectBlock("#4FC3F7", self, radius=4, opacity=0.9)  # 亮蓝色
        self.accent_line.setGeometry(screen_size.width(), screen_size.height() // 2 - 7, 0, 14)
        self.accent_line.raise_()
        
        # 创建时间显示 - 简化时间强调元素
        current_time = datetime.now().strftime("%H:%M")  # 去掉秒数
        
        # 时间容器和强调背景 - 简洁设计
        time_width = screen_size.width() * 2 // 5  # 宽度适中
        time_height = 190
        time_x = self.block_a_width + (screen_size.width() - self.block_a_width - time_width) // 2
        time_y = screen_size.height() // 4 - time_height // 2
        
        # 创建时间标签 - 使用阴影效果替代text-shadow
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
        
        # 创建文字内容 - 调整提示消息位置和样式
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
        
        # 创建左侧装饰条 - 简洁的蓝色竖条
        decoration_width = 8
        self.message_decoration = ColorBlock("#2196F3", self.message_container, radius=4, opacity=0.9)
        self.message_decoration.setGeometry(0, 0, decoration_width, message_height)
        self.message_decoration.raise_()
        
        # 处理多行消息
        message_lines = self.message.split('\n')
        
        # 动态创建多个标签以支持多行，加粗字体但稍微减小尺寸
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
        
        # 添加提示信息 - 简洁样式
        self.hint_label = QLabel("点击任意位置或按ESC键关闭", self)
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
        """开始入场动画(使用错位效果，但更加平滑)"""
        screen_size = QGuiApplication.primaryScreen().size()
        
        # 背景模糊层淡入
        anim_backdrop = QPropertyAnimation(self.backdrop, b"geometry")
        anim_backdrop.setDuration(800)
        anim_backdrop.setStartValue(QRect(0, 0, 0, screen_size.height()))
        anim_backdrop.setEndValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_backdrop.setEasingCurve(QEasingCurve.OutQuint)  # 更平滑的缓动
        
        # 色块A从顶部向底部延伸 - 使用更平滑的动画曲线
        anim_a = QPropertyAnimation(self.block_a, b"geometry")
        anim_a.setDuration(1100)
        anim_a.setStartValue(QRect(0, 0, self.block_a_width, 0))
        anim_a.setEndValue(QRect(0, 0, self.block_a_width, screen_size.height()))
        anim_a.setEasingCurve(QEasingCurve.OutQuint)  # 更平滑的缓动
        
        # 色块B从左向右延伸
        anim_b = QPropertyAnimation(self.block_b, b"geometry")
        anim_b.setDuration(1200)
        anim_b.setStartValue(QRect(0, 0, 0, screen_size.height()))
        anim_b.setEndValue(QRect(0, 0, screen_size.width(), screen_size.height()))
        anim_b.setEasingCurve(QEasingCurve.OutQuart)  # 更平滑的缓动
        
        # 色块C从右向左延展到色块A的右边界
        anim_c = QPropertyAnimation(self.block_c, b"geometry")
        anim_c.setDuration(1100)
        anim_c.setStartValue(QRect(screen_size.width(), 0, 0, screen_size.height() // 2))
        anim_c.setEndValue(QRect(self.block_a_width, 0, screen_size.width() - self.block_a_width, screen_size.height() // 2))
        anim_c.setEasingCurve(QEasingCurve.OutQuint)  # 更平滑的缓动
        
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
        
        # 启动动画序列
        anim_backdrop.start()  # 先启动背景
        
        # 使用错位效果启动其他动画
        QTimer.singleShot(150, lambda: self.enter_animations['a'].start())
        QTimer.singleShot(350, lambda: self.enter_animations['b'].start())
        QTimer.singleShot(600, lambda: self.enter_animations['c'].start())
        QTimer.singleShot(800, lambda: self.enter_animations['accent'].start())
    
    def start_close_animation(self):
        """开始退场动画(优化后的交错效果，更加平滑)"""
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
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        self.close_timer.stop()
        self.sound_repeat_timer.stop()  # 停止声音重复播放
        self.start_close_animation()
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.close_timer.stop()
            self.sound_repeat_timer.stop()  # 停止声音重复播放
            self.start_close_animation()
        super().keyPressEvent(event)