import os
from datetime import datetime
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QGuiApplication, QColor

from .ui_components import ColorBlock, LightEffectBlock
from .card_ui import Card

class ReminderUI:
    """负责提醒屏幕的UI组件创建与初始化"""
    
    def __init__(self, parent):
        self.parent = parent
        self.message = parent.message
        self.wallpapers = parent.wallpapers
        
        # 保存UI组件
        self.backdrop = None
        self.block_a = None
        self.block_b = None
        self.block_c = None
        self.accent_line = None
        self.time_label = None
        self.message_container = None
        self.message_decoration = None
        self.hint_label = None
        self.cards = []  # 存储名片组件列表
        
        # 计算尺寸
        self.screen_size = QGuiApplication.primaryScreen().size()
        self.block_a_width = self.screen_size.width() // 5
    
    def setup_ui(self):
        """设置UI界面"""
        # 设置窗口属性
        self.parent.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.parent.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置窗口全屏
        self.parent.setGeometry(0, 0, self.screen_size.width(), self.screen_size.height())
        
        # 创建主要组件
        self._create_background_layers()
        self._create_time_display()
        self._create_message_display()
        self._create_hint_label()
    
    def _create_background_layers(self):
        """创建背景层和色块"""
        # 创建背景模糊遮罩层
        self.backdrop = ColorBlock("rgba(0, 25, 50, 0.2)", self.parent, radius=0, opacity=0.2)
        self.backdrop.setGeometry(0, 0, 0, self.screen_size.height())
        
        # 创建色块B（底层，深蓝色，带圆角）
        opacity_b = 0.85
        self.block_b = ColorBlock("#0B5394", self.parent, radius=5, opacity=opacity_b)
        self.block_b.setGeometry(0, 0, 0, self.screen_size.height())
        
        # 如果有主区域壁纸，设置背景图片
        if "main" in self.wallpapers and os.path.exists(self.wallpapers["main"]):
            self.block_b.set_background_image(self.wallpapers["main"])
            # 使用壁纸透明度设置
            if "main_opacity" in self.wallpapers:
                self.block_b.color.setAlphaF(self.wallpapers["main_opacity"])
            else:
                self.block_b.color.setAlphaF(0.7)
        
        # 创建色块A（左侧，上层，更深的蓝色）
        opacity_a = 0.95
        self.block_a = ColorBlock("#073763", self.parent, radius=5, opacity=opacity_a)
        
        # 如果有左侧区域壁纸，设置背景图片
        if "left" in self.wallpapers and os.path.exists(self.wallpapers["left"]):
            self.block_a.set_background_image(self.wallpapers["left"])
            # 使用壁纸透明度设置
            if "left_opacity" in self.wallpapers:
                self.block_a.color.setAlphaF(self.wallpapers["left_opacity"])
            else:
                self.block_a.color.setAlphaF(0.7)
        
        # 设置几何尺寸，初始高度为0用于动画效果
        self.block_a.setGeometry(0, 0, self.block_a_width, 0)
        self.block_a.raise_()  # 确保位于上层
        
        # 创建色块C（中间层，湖蓝色）
        opacity_c = 0.90
        self.block_c = ColorBlock("#8EACCD", self.parent, radius=5, opacity=opacity_c)
        self.block_c.setGeometry(self.screen_size.width(), 0, 0, self.screen_size.height() // 2)
        
        # 如果有上部区域壁纸，设置背景图片
        if "top" in self.wallpapers and os.path.exists(self.wallpapers["top"]):
            self.block_c.set_background_image(self.wallpapers["top"])
            # 使用壁纸透明度设置
            if "top_opacity" in self.wallpapers:
                self.block_c.color.setAlphaF(self.wallpapers["top_opacity"])
            else:
                self.block_c.color.setAlphaF(0.7)
        
        self.block_c.stackUnder(self.block_a)  # 确保层级正确
        
        # 创建装饰条
        opacity_accent = 0.9
        self.accent_line = LightEffectBlock("#4FC3F7", self.parent, radius=4, opacity=opacity_accent)
        
        # 如果有装饰区域壁纸，设置背景图片
        if "accent" in self.wallpapers and os.path.exists(self.wallpapers["accent"]):
            self.accent_line.set_background_image(self.wallpapers["accent"])
            # 使用壁纸透明度设置
            if "accent_opacity" in self.wallpapers:
                self.accent_line.color.setAlphaF(self.wallpapers["accent_opacity"])
            else:
                self.accent_line.color.setAlphaF(0.7)
        
        self.accent_line.setGeometry(self.screen_size.width(), self.screen_size.height() // 2 - 7, 0, 14)
        self.accent_line.raise_()
        
        # 在创建色块A后添加名片
        self.display_cards()
    
    def display_cards(self):
        """显示展示片，左侧对齐排列"""
        if not hasattr(self.parent, 'card_manager') or self.parent.card_manager is None:
            return
            
        cards_data = self.parent.card_manager.get_all_cards()
        
        # 基础设置
        start_y = 50  # 起始Y坐标
        spacing = 16  # 卡片间距
        left_margin = 20  # 左侧边距
        
        for i, card_data in enumerate(cards_data):
            card = Card(card_data, self.block_a)
            
            # 计算卡片需要的宽度 (基于内容)
            card.adjustSize()
            
            # 检查是否只有图片，无文字信息
            name = card_data.get("name", "")
            title = card_data.get("title", "")
            has_text_info = bool(name.strip() or title.strip())
            
            # 根据是否有文本内容设置不同的宽度
            if has_text_info:
                # 正常卡片
                text_length = max(len(name), len(title))
                card_width = min(self.block_a_width - 50, 86 + min(14 * text_length, 250) + 42)
            else:
                # 纯图片卡片，使用正方形尺寸
                card_width = 110
            
            card_height = card.sizeHint().height()
            
            # 设置初始位置（在屏幕外）
            card.setGeometry(-300, start_y, card_width, card_height)
            
            # 错位启动动画以匹配色块动画风格
            base_delay = 580  # 调整基础延迟
            delay = base_delay + i * 150  # 每个卡片延迟递增，类似色块错位效果
            
            QTimer.singleShot(delay, lambda c=card, sx=-300, ex=left_margin, y=start_y: 
                            c.start_enter_animation(sx, ex, y))
            
            # 更新下一张卡片的起始位置
            start_y += card_height + spacing
            
            self.cards.append(card)

    def start_cards_exit_animation(self):
        """开始名片退场动画"""
        for i, card in enumerate(self.cards):
            # 错位启动退场动画，使用更短的间隔
            QTimer.singleShot(i * 180, lambda c=card: 
                            c.start_exit_animation(c.x(), -400))
    
    def _create_time_display(self):
        """创建时间显示"""
        current_time = datetime.now().strftime("%H:%M")
        
        # 时间容器尺寸和位置
        time_width = self.screen_size.width() * 2 // 5
        time_height = 190
        time_x = self.block_a_width + (self.screen_size.width() - self.block_a_width - time_width) // 2
        time_y = self.screen_size.height() // 4 - time_height // 2
        
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
        glow.setBlurRadius(20)
        glow.setColor(QColor(255, 255, 255, 200))
        glow.setOffset(0, 0)
        self.time_label.setGraphicsEffect(glow)
        
        self.time_label.raise_()
    
    def _create_message_display(self):
        """创建消息显示区域"""
        # 计算消息区域尺寸和位置
        message_width = self.screen_size.width() * 3 // 5
        message_height = 300
        message_x = (self.screen_size.width() - message_width) // 2 + 50
        message_y = self.screen_size.height() * 3 // 5
        
        # 创建透明容器
        self.message_container = QFrame(self.block_b)
        self.message_container.setGeometry(message_x, message_y, message_width, message_height)
        self.message_container.setStyleSheet("background-color: transparent; border: none;")
        
        # 创建垂直布局
        message_layout = QVBoxLayout(self.message_container)
        message_layout.setContentsMargins(35, 5, 20, 5)
        message_layout.setSpacing(12)
        
        # 创建左侧装饰条
        decoration_width = 8
        self.message_decoration = ColorBlock("#2196F3", self.message_container, radius=4, opacity=0.9)
        self.message_decoration.setGeometry(0, 0, decoration_width, message_height)
        self.message_decoration.raise_()
        
        # 处理多行消息
        message_lines = self.message.split('\n')
        
        # 为每行消息创建标签
        for i, line in enumerate(message_lines):
            msg_label = QLabel(line, self.message_container)
            msg_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            msg_label.setStyleSheet(f"""
                color: white;
                font-size: {48 if len(message_lines) <= 2 else 42}px;
                font-weight: 600;
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
    
    def _create_hint_label(self):
        """创建提示标签"""
        self.hint_label = QLabel("双击或按ESC键关闭", self.parent)
        self.hint_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.hint_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
            letter-spacing: 0.5px;
            padding: 24px;
            background-color: transparent;
        """)
        self.hint_label.setGeometry(0, 0, self.screen_size.width(), self.screen_size.height())
