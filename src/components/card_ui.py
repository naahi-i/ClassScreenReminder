from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize, QPoint, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPixmap, QFont, QLinearGradient, QBrush, QPen, QPalette

class Card(QFrame):
    """高级展示卡片UI组件"""
    
    def __init__(self, card_data, parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self.hover_effect = False  # 是否启用悬停效果
        self.is_animating = False  # 动画状态标记
        self.cached_pixmap = None  # 缓存绘制结果
        
        # 初始化动画对象
        self.enter_animation = None
        self.exit_animation = None
        
        # 预先计算一次大小，减少动画过程中的计算
        self.setup_ui()
        
        # 预渲染背景以提高性能
        self.update_cached_background()
    
    def setup_ui(self):
        """设置卡片UI"""
        self.setObjectName("card")
        
        # 使用现代化阴影和圆角效果，改回白色底色
        self.setStyleSheet("""
            QFrame#card {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        # 启用阴影效果需要的设置
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 使用水平布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 15, 12)
        main_layout.setSpacing(15)  # 增加间距
        
        # 添加左侧图片
        image_container = QFrame()
        image_container.setFixedSize(86, 86)  # 稍微增大容器
        image_container.setStyleSheet("background: transparent;")
        
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setAlignment(Qt.AlignCenter)
        
        image_label = QLabel()
        image_size = 80  # 图片大小
        
        # 如果有图片，加载图片; 否则创建默认图片
        if "image_path" in self.card_data and self.card_data["image_path"]:
            pixmap = QPixmap(self.card_data["image_path"])
            if not pixmap.isNull():
                # 创建圆形或方形图片
                is_round = self.card_data.get("is_round", True)
                
                # 先缩放图片填充方式
                scaled_pixmap = pixmap.scaled(image_size, image_size, 
                                            Qt.KeepAspectRatioByExpanding, 
                                            Qt.SmoothTransformation)
                
                # 计算中心裁剪区域
                width, height = scaled_pixmap.width(), scaled_pixmap.height()
                x_offset = (width - image_size) // 2 if width > image_size else 0
                y_offset = (height - image_size) // 2 if height > image_size else 0
                
                # 裁剪中心区域
                cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, 
                                                min(width, image_size), 
                                                min(height, image_size))
                
                if is_round:
                    # 创建圆形图片
                    rounded_pixmap = QPixmap(image_size, image_size)
                    rounded_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # 创建圆形裁剪区域
                    path = QPainterPath()
                    path.addEllipse(0, 0, image_size, image_size)
                    painter.setClipPath(path)
                    
                    # 先绘制边框
                    pen = QPen(QColor(200, 200, 200, 120), 2)
                    painter.setPen(pen)
                    painter.drawEllipse(1, 1, image_size-2, image_size-2)
                    
                    # 绘制裁剪后的图片
                    painter.drawPixmap(0, 0, cropped_pixmap)
                    painter.end()
                    
                    image_label.setPixmap(rounded_pixmap)
                else:
                    # 使用方形图片，但添加圆角效果
                    rounded_pixmap = QPixmap(image_size, image_size)
                    rounded_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # 创建圆角矩形裁剪区域
                    path = QPainterPath()
                    corner_radius = 12  # 增大圆角半径
                    path.addRoundedRect(0, 0, image_size, image_size, corner_radius, corner_radius)
                    painter.setClipPath(path)
                    
                    # 先绘制边框
                    pen = QPen(QColor(200, 200, 200, 120), 2)
                    painter.setPen(pen)
                    painter.drawRoundedRect(1, 1, image_size-2, image_size-2, corner_radius, corner_radius)
                    
                    # 绘制裁剪后的图片
                    painter.drawPixmap(0, 0, cropped_pixmap)
                    painter.end()
                    
                    image_label.setPixmap(rounded_pixmap)
        else:
            # 创建默认占位图，使用更优雅的颜色
            is_round = self.card_data.get("is_round", True)
            
            # 创建一个空白透明Pixmap
            default_pixmap = QPixmap(image_size, image_size)
            default_pixmap.fill(Qt.transparent)
            
            painter = QPainter(default_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 创建一个柔和的渐变背景
            gradient = QLinearGradient(0, 0, image_size, image_size)
            gradient.setColorAt(0, QColor(100, 149, 237))  # 淡蓝色
            gradient.setColorAt(1, QColor(65, 105, 225))   # 皇家蓝
            
            # 根据形状绘制不同的背景
            if is_round:
                # 绘制圆形
                path = QPainterPath()
                path.addEllipse(0, 0, image_size, image_size)
                painter.setClipPath(path)
                
                # 绘制渐变背景
                painter.fillPath(path, QBrush(gradient))
                
                # 绘制边框
                pen = QPen(QColor(200, 200, 200, 120), 2)
                painter.setPen(pen)
                painter.drawEllipse(1, 1, image_size-2, image_size-2)
            else:
                # 绘制圆角矩形
                corner_radius = 15
                path = QPainterPath()
                path.addRoundedRect(0, 0, image_size, image_size, corner_radius, corner_radius)
                painter.setClipPath(path)
                
                # 绘制渐变背景
                painter.fillPath(path, QBrush(gradient))
                
                # 绘制边框
                pen = QPen(QColor(200, 200, 200, 120), 2)
                painter.setPen(pen)
                painter.drawRoundedRect(1, 1, image_size-2, image_size-2, corner_radius, corner_radius)
            
            # 绘制首字母
            name = self.card_data.get("name", "")
            display_char = name[0].upper() if name else "?"
            
            # 设置字体
            font = QFont()
            font.setFamily("Segoe UI")
            font.setPixelSize(32)
            font.setBold(True)
            painter.setFont(font)
            
            # 文字颜色
            painter.setPen(Qt.white)
            
            # 居中绘制文字
            painter.drawText(default_pixmap.rect(), Qt.AlignCenter, display_char)
            painter.end()
            
            image_label.setPixmap(default_pixmap)
            
        # 设置图片标签固定大小并添加到布局
        image_label.setFixedSize(image_size, image_size)
        image_layout.addWidget(image_label)
        main_layout.addWidget(image_container)
        
        # 右侧文字布局
        text_container = QFrame()
        text_container.setStyleSheet("background: transparent;")
        
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        # 添加名称标签 (自动换行)
        name = self.card_data.get("name", "")
        title_text = self.card_data.get("title", "")
        
        # 检查是否只有图片，无文字信息
        has_text_info = bool(name.strip() or title_text.strip())
        
        if has_text_info:
            # 处理常规卡片，包含文字信息
            name_label = QLabel(name)
            name_label.setWordWrap(True)
            name_label.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #333;
                font-family: 'Segoe UI', sans-serif;
            """)
            text_layout.addWidget(name_label)
            
            # 如果有子标题，添加子标题 (自动换行)
            if title_text:
                title_label = QLabel(title_text)
                title_label.setWordWrap(True)
                title_label.setStyleSheet("""
                    font-size: 14px; 
                    color: #666;
                    font-family: 'Segoe UI', sans-serif;
                """)
                text_layout.addWidget(title_label)
            
            # 增加文本右侧弹性空间
            text_layout.addStretch(1)
            main_layout.addWidget(text_container)
            
            # 关键：使文本部分能够拉伸，图片部分固定
            main_layout.setStretch(0, 0)  # 图片区域不拉伸
            main_layout.setStretch(1, 1)  # 文本区域可拉伸
        else:
            # 纯图片卡片，优化显示样式：移除右侧空间，图片居中
            # 中心对齐图片
            image_label.setAlignment(Qt.AlignCenter)
            main_layout.setAlignment(Qt.AlignCenter)
            
            # 增大纯图片卡片的尺寸
            image_container.setFixedSize(100, 100)  # 增大容器尺寸
            image_label.setFixedSize(95, 95)  # 增大图片尺寸
            
            # 移除右侧拉伸区域，使卡片变为正方形风格
            main_layout.setContentsMargins(8, 8, 8, 8)
            
            # 让主布局居中
            self.setStyleSheet("""
                QFrame#card {
                    background-color: rgba(255, 255, 255, 0.95);
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    padding: 5px;
                }
            """)
        
        # 设置卡片策略 - 自动调整宽度和优先高度
        self.setSizePolicy(
            QSizePolicy.Expanding,      # 水平策略：扩展
            QSizePolicy.Preferred       # 垂直策略：首选高度
        )
        
        # 强制立即计算布局
        self.updateGeometry()
        self.adjustSize()
    
    def update_cached_background(self):
        """预渲染背景到缓存，提高动画性能"""
        if self.width() <= 0 or self.height() <= 0:
            return
        
        self.cached_pixmap = QPixmap(self.size())
        self.cached_pixmap.fill(Qt.transparent)
        
        painter = QPainter(self.cached_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 确保抗锯齿开启
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # 增加平滑渲染
        
        # 绘制背景
        rect = self.rect()
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)
        
        # 填充白色背景
        painter.fillPath(path, QBrush(QColor(255, 255, 255, 245)))
        
        # 绘制边框高光
        pen = QPen(QColor(200, 200, 200, 100), 1)
        painter.setPen(pen)
        painter.drawRoundedRect(1, 1, rect.width()-2, rect.height()-2, 14, 14)
        painter.end()
    
    def resizeEvent(self, event):
        """重写大小变化事件，更新缓存"""
        super().resizeEvent(event)
        self.update_cached_background()
    
    def paintEvent(self, event):
        """自定义绘制事件，添加高级效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 确保抗锯齿开启
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # 增加平滑渲染
        
        # 使用缓存的背景以提高动画性能
        if self.cached_pixmap and not self.cached_pixmap.isNull():
            painter.drawPixmap(0, 0, self.cached_pixmap)
        else:
            # 回退到直接绘制（仅在缓存不可用时）
            rect = self.rect()
            
            # 创建圆角路径
            path = QPainterPath()
            path.addRoundedRect(rect, 15, 15)
            
            # 填充白色背景
            painter.fillPath(path, QBrush(QColor(255, 255, 255, 245)))
            
            # 绘制边框高光
            pen = QPen(QColor(200, 200, 200, 100), 1)
            painter.setPen(pen)
            painter.drawRoundedRect(1, 1, rect.width()-2, rect.height()-2, 14, 14)
        
        # 调用父类方法确保子控件正确绘制
        super().paintEvent(event)
    
    def prepare_for_animation(self):
        """为动画做准备，预先计算大小和缓存背景"""
        # 确保大小已计算
        self.adjustSize()
        # 更新缓存
        self.update_cached_background()
        # 设置动画状态
        self.is_animating = True
    
    def start_enter_animation(self, start_x, end_x, y_pos):
        """开始入场动画"""
        # 提前准备动画
        self.prepare_for_animation()
        
        # 获取当前大小，避免动画中重新计算
        current_height = self.height()
        current_width = self.width()
        
        # 预先设置初始位置，避免闪烁
        self.setGeometry(start_x, y_pos, current_width, current_height)
        
        # 配置动画
        self.enter_animation = QPropertyAnimation(self, b"geometry")
        self.enter_animation.setDuration(850)  # 调整持续时间与色块相似
        self.enter_animation.setStartValue(QRect(start_x, y_pos, current_width, current_height))
        self.enter_animation.setEndValue(QRect(end_x, y_pos, current_width, current_height))
        self.enter_animation.setEasingCurve(QEasingCurve.OutQuint)  # 使用与色块一致的缓动曲线
        
        # 动画完成后重置状态
        self.enter_animation.finished.connect(self.animation_finished)
        
        # 直接启动，不需要小延迟
        self.enter_animation.start()
    
    def start_exit_animation(self, start_x, end_x):
        """开始退场动画"""
        self.is_animating = True
        
        current_geometry = self.geometry()
        self.exit_animation = QPropertyAnimation(self, b"geometry")
        self.exit_animation.setDuration(700)  # 调整持续时间
        self.exit_animation.setStartValue(current_geometry)
        self.exit_animation.setEndValue(QRect(end_x, current_geometry.y(), current_geometry.width(), current_geometry.height()))
        self.exit_animation.setEasingCurve(QEasingCurve.InQuint)  # 使用与色块一致的缓动曲线
        self.exit_animation.finished.connect(self.deleteLater)
        self.exit_animation.start()
    
    def animation_finished(self):
        """动画完成后的回调"""
        self.is_animating = False
        self.update()  # 确保最终状态正确绘制
    
    def sizeHint(self):
        """提供尺寸提示以便布局正确计算"""
        name = self.card_data.get("name", "")
        title = self.card_data.get("title", "")
        
        # 检查是否只有图片，无文字信息
        has_text_info = bool(name.strip() or title.strip())
        
        if has_text_info:
            # 常规卡片尺寸
            # 计算文本宽度 (估算值)
            text_length = max(len(name), len(title))
            # 较长的文本需要更宽的空间
            text_width = min(15 * text_length, 350)  # 限制最大宽度
            
            # 图片宽度 + 文本宽度 + 间距 + 边距
            width = 86 + text_width + 15 + 27
            
            # 根据是否有标题调整高度
            height = 110 if title else 90
        else:
            # 纯图片卡片 - 增大尺寸
            width = 130
            height = 130
        
        return QSize(width, height)
    
    def minimumSizeHint(self):
        """提供最小尺寸提示"""
        # 检查是否只有图片，无文字信息
        name = self.card_data.get("name", "")
        title_text = self.card_data.get("title", "")
        has_text_info = bool(name.strip() or title_text.strip())
        
        if has_text_info:
            return QSize(220, 90)  # 常规卡片最小尺寸
        else:
            return QSize(120, 120)  # 增大纯图片卡片最小尺寸
