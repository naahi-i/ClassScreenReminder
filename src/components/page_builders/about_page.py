import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

def create_about_page(main_window):
    """创建关于页面"""
    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(15)
    
    about_frame = QFrame()
    about_frame.setObjectName("newReminderFrame")
    about_layout = QVBoxLayout(about_frame)
    about_layout.setContentsMargins(16, 16, 16, 16)
    about_layout.setSpacing(15)
    
    # 应用标志和名称
    logo_layout = QHBoxLayout()
    logo_layout.setAlignment(Qt.AlignCenter)
    
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "icon.ico")
    if os.path.exists(icon_path):
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addWidget(logo_label)
    
    about_layout.addLayout(logo_layout)
    
    app_name = QLabel("屏幕提醒工具")
    app_name.setObjectName("aboutAppName")
    app_name.setAlignment(Qt.AlignCenter)
    about_layout.addWidget(app_name)
    
    description = QLabel("全屏提醒工具，可在指定时间显示全屏提醒消息。")
    description.setWordWrap(True)
    description.setAlignment(Qt.AlignCenter)
    about_layout.addWidget(description)
    
    # 添加分隔线
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setObjectName("separator")
    about_layout.addWidget(separator)

    # 添加图片展示
    image_layout = QHBoxLayout()
    image_layout.setAlignment(Qt.AlignCenter)

    # 加载图片资源
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                             "resources", "uh.jpg")
    if os.path.exists(image_path):
        # 创建QPixmap并加载图片
        pixmap = QPixmap(image_path)
        
        # 设置合适的显示尺寸
        display_size = 450
        pixmap = pixmap.scaled(display_size, display_size, 
                              Qt.KeepAspectRatio, 
                              Qt.SmoothTransformation)
        
        # 创建圆角图片
        rounded_pixmap = QPixmap(pixmap.size())
        rounded_pixmap.fill(Qt.transparent)
        
        # 使用QPainter绘制圆角图片
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 15, 15)
        
        # 设置剪切路径并绘制原始图片
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        # 创建标签并显示圆角图片
        image_label = QLabel()
        image_label.setPixmap(rounded_pixmap)
        image_label.setStyleSheet("margin: 10px;")
        image_layout.addWidget(image_label)

    about_layout.addLayout(image_layout)
    about_layout.addStretch(1)
    
    page_layout.addWidget(about_frame)
    
    return page
