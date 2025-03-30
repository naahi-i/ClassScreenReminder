from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QCheckBox, QFrame)

def create_settings_page(main_window):
    """创建应用设置页面"""
    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(15)
    
    # 创建设置框架
    settings_frame = QFrame()
    settings_frame.setObjectName("newReminderFrame")
    settings_layout = QVBoxLayout(settings_frame)
    settings_layout.setContentsMargins(16, 16, 16, 16)
    settings_layout.setSpacing(15)
    
    # 添加应用设置选项
    info_label = QLabel("应用程序设置")
    info_label.setWordWrap(True)
    settings_layout.addWidget(info_label)
    
    # 添加开机自启动选项
    main_window.autostart_checkbox = QCheckBox("开机时自动启动应用")
    main_window.autostart_checkbox.setChecked(True)
    main_window.autostart_checkbox.toggled.connect(main_window.toggle_autostart)
    settings_layout.addWidget(main_window.autostart_checkbox)
    
    # 添加启动时最小化选项
    main_window.startup_minimized_checkbox = QCheckBox("启动时最小化到系统托盘")
    main_window.startup_minimized_checkbox.setChecked(main_window.startup_minimized)
    main_window.startup_minimized_checkbox.toggled.connect(main_window.on_startup_minimized_changed)
    settings_layout.addWidget(main_window.startup_minimized_checkbox)
    
    # 弹性空间
    settings_layout.addStretch(1)
    
    page_layout.addWidget(settings_frame)
    
    return page
