from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRect, QSize, Signal, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPainterPath, QBrush, QColor, QPixmap, QFont, QLinearGradient

class ColorBlock(QFrame):
    """自定义颜色块组件，支持圆角和半透明效果，可选背景图片"""
    def __init__(self, color, parent=None, radius=0, opacity=1.0, bg_image_path=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.color.setAlphaF(opacity)
        self.radius = radius
        self.bg_image = None
        self.bg_image_path = bg_image_path
        self.original_image = None  # 存储原始图像
        self.scaled_image = None    # 存储缩放后的图像
        
        if bg_image_path:
            self.load_background_image(bg_image_path)
        
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def load_background_image(self, image_path):
        """加载背景图片"""
        if image_path and image_path.strip():
            self.original_image = QPixmap(image_path)
            if not self.original_image.isNull():
                self.bg_image_path = image_path
                return True
        return False
    
    def set_background_image(self, image_path):
        """设置背景图片"""
        if self.load_background_image(image_path):
            self.update()  # 触发重绘
        else:
            self.original_image = None
            self.scaled_image = None
            self.bg_image_path = None
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        
        painter.setClipPath(path)
        
        # 如果有背景图，先绘制背景图
        if self.original_image and not self.original_image.isNull():
            # 获取当前控件的尺寸
            current_width = self.width()
            current_height = self.height()
            
            if current_width <= 0 or current_height <= 0:
                # 如果控件尺寸无效，不绘制图片
                pass
            else:
                # 计算缩放比例，使图片覆盖整个区域（裁剪模式）
                img_width = self.original_image.width()
                img_height = self.original_image.height()
                
                # 计算需要缩放的比例，选择更大的缩放比例以确保填充整个区域
                scale_x = current_width / img_width
                scale_y = current_height / img_height
                scale = max(scale_x, scale_y)  # 选择更大的缩放比例
                
                # 缩放图片
                scaled_width = int(img_width * scale)
                scaled_height = int(img_height * scale)
                
                # 在这里进行实时缩放，确保图片总是能填充整个区域
                scaled_img = self.original_image.scaled(
                    scaled_width, 
                    scaled_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # 计算绘制位置，居中显示
                x_offset = (scaled_width - current_width) // 2 if scaled_width > current_width else 0
                y_offset = (scaled_height - current_height) // 2 if scaled_height > current_height else 0
                
                # 计算目标区域
                dest_x = (current_width - scaled_width) // 2 if scaled_width < current_width else 0
                dest_y = (current_height - scaled_height) // 2 if scaled_height < current_height else 0
                
                # 绘制图片，在正确的位置并裁剪适当的区域
                painter.drawPixmap(
                    dest_x, dest_y, scaled_width, scaled_height,
                    scaled_img,
                    x_offset, y_offset, scaled_width, scaled_height
                )
        
        # 绘制颜色遮罩
        painter.fillPath(path, QBrush(self.color))
        
        super().paintEvent(event)

# LightEffectBlock类可以复用ColorBlock类，避免重复代码
LightEffectBlock = ColorBlock

class MenuButton(QPushButton):
    def __init__(self, text="", parent=None, is_active=False):
        super().__init__(parent)
        self.setText(text)
        self.is_active = is_active
        self.setCheckable(True)
        self.setChecked(is_active)
        
        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("menuButton")
        
        # 添加额外的样式
        self._update_style()
        
    def _update_style(self):
        base_style = """
            QPushButton {
                text-align: left;
                padding-left: 16px;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #202020;
                font-weight: 500;
                margin: 2px 4px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.08);
            }
            QPushButton:checked {
                background-color: rgba(98, 100, 167, 0.15);
                color: #0067C0;
                font-weight: 500;
            }
            QPushButton:checked:hover {
                background-color: rgba(98, 100, 167, 0.2);
            }
        """
        self.setStyleSheet(base_style)

class SidebarMenu(QWidget):
    menuChanged = Signal(str)  # 当菜单项改变时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarMenu")
        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 15, 10, 15)
        self.layout.setSpacing(3)
        
        self.menu_buttons = {}
        self.current_menu = None
        
        self.setStyleSheet("""
            #sidebarMenu {
                background-color: #f8f8f8;
                border-right: 1px solid #e1e1e1;
            }
        """)
    
    def add_menu_item(self, menu_id, text, is_active=False):
        """添加菜单项"""
        btn = MenuButton(text, self, is_active)
        btn.clicked.connect(lambda: self._on_menu_clicked(menu_id))
        self.layout.addWidget(btn)
        self.menu_buttons[menu_id] = btn
        
        if is_active:
            self.current_menu = menu_id
    
    def add_spacer(self):
        """添加弹性空间"""
        self.layout.addStretch(1)
    
    def _on_menu_clicked(self, menu_id):
        """处理菜单点击事件"""
        if self.current_menu != menu_id:
            # 更新所有按钮状态
            for btn_id, btn in self.menu_buttons.items():
                btn.setChecked(btn_id == menu_id)
            
            self.current_menu = menu_id
            self.menuChanged.emit(menu_id)
    
    def set_active_menu(self, menu_id):
        """设置当前活动菜单"""
        if menu_id in self.menu_buttons and self.current_menu != menu_id:
            self._on_menu_clicked(menu_id)