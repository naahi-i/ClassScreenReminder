from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QComboBox, QSlider)
from PySide6.QtCore import Qt

def create_wallpaper_page(main_window):
    """创建壁纸设置页面"""
    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(15)
    
    # 添加壁纸设置区域到专用页面
    _add_wallpaper_settings(main_window, page_layout)
    
    return page

def _add_wallpaper_settings(main_window, parent_layout):
    """添加壁纸设置区域"""
    wallpaper_frame = QFrame()
    wallpaper_frame.setObjectName("newReminderFrame")
    wallpaper_layout = QVBoxLayout(wallpaper_frame)
    wallpaper_layout.setContentsMargins(16, 16, 16, 16)
    wallpaper_layout.setSpacing(15)

    # 区域选择下拉框
    area_layout = QHBoxLayout()
    area_label = QLabel("选择区域:")
    area_label.setMinimumWidth(80)
    area_layout.addWidget(area_label)
    
    main_window.area_combo = QComboBox()
    main_window.area_combo.setObjectName("areaCombo")
    main_window.area_combo.addItem("中间区域", "main")
    main_window.area_combo.addItem("左侧区域", "left")
    main_window.area_combo.addItem("上部区域", "top")
    main_window.area_combo.addItem("装饰区域", "accent")
    main_window.area_combo.currentIndexChanged.connect(main_window.on_area_changed)
    area_layout.addWidget(main_window.area_combo)
    
    wallpaper_layout.addLayout(area_layout)
    
    # 预览和路径显示
    preview_layout = QVBoxLayout()
    preview_layout.setSpacing(5)
    
    main_window.wallpaper_preview = QLabel("无背景图片")
    main_window.wallpaper_preview.setObjectName("wallpaperPreview")
    main_window.wallpaper_preview.setAlignment(Qt.AlignCenter)
    main_window.wallpaper_preview.setMinimumHeight(180)
    main_window.wallpaper_preview.setStyleSheet("""
        QLabel#wallpaperPreview {
            background-color: #f5f5f5;
            border: 1px dashed #d0d0d0;
            border-radius: 4px;
            padding: 8px;
        }
    """)
    preview_layout.addWidget(main_window.wallpaper_preview)
    
    main_window.path_label = QLabel("未选择图片")
    main_window.path_label.setObjectName("pathLabel")
    main_window.path_label.setWordWrap(True)
    main_window.path_label.setAlignment(Qt.AlignCenter)
    preview_layout.addWidget(main_window.path_label)
    
    # 添加透明度滑块
    opacity_layout = QHBoxLayout()
    opacity_label = QLabel("遮罩透明度:")
    opacity_label.setMinimumWidth(80)
    opacity_layout.addWidget(opacity_label)
    
    # 创建滑块
    opacity_slider = QSlider(Qt.Horizontal)
    opacity_slider.setObjectName("opacitySlider")
    opacity_slider.setRange(0, 100)
    opacity_slider.setTickPosition(QSlider.TicksBelow)
    opacity_slider.setTickInterval(10)
    opacity_layout.addWidget(opacity_slider)
    
    # 创建标签显示当前值
    opacity_value_label = QLabel("30%")
    opacity_value_label.setObjectName("opacityValueLabel")
    opacity_value_label.setMinimumWidth(40)
    opacity_layout.addWidget(opacity_value_label)
    
    # 保存对象引用
    main_window.opacity_slider = opacity_slider
    main_window.opacity_value_label = opacity_value_label
    
    # 设置默认值 - 直接设置不触发事件
    opacity_slider.blockSignals(True)
    opacity_slider.setValue(30)
    opacity_slider.blockSignals(False)
    
    # 连接值变化后立即更新标签显示
    def update_opacity_label(value):
        opacity_value_label.setText(f"{value}%")
    opacity_slider.valueChanged.connect(update_opacity_label)
    
    # 将滑块控件传递给壁纸管理器UI，这会连接信号
    main_window.wallpaper_manager_ui.set_opacity_slider(opacity_slider)
    
    preview_layout.addLayout(opacity_layout)
    wallpaper_layout.addLayout(preview_layout)
    
    # 操作按钮
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(10)
    
    select_button = QPushButton("选择背景图片")
    select_button.setObjectName("primaryButton")
    select_button.clicked.connect(main_window.select_area_wallpaper)
    buttons_layout.addWidget(select_button)
    
    clear_button = QPushButton("清除当前背景")
    clear_button.setObjectName("actionButton")
    clear_button.clicked.connect(main_window.clear_area_wallpaper)
    buttons_layout.addWidget(clear_button)
    
    clear_all_button = QPushButton("清除所有背景")
    clear_all_button.setObjectName("secondaryButton")
    clear_all_button.clicked.connect(main_window.clear_all_wallpapers)
    buttons_layout.addWidget(clear_all_button)
    
    wallpaper_layout.addLayout(buttons_layout)
    
    parent_layout.addWidget(wallpaper_frame)
