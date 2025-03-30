from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os

def create_audio_page(main_window):
    """创建音频设置页面"""
    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(15)
    
    # 添加音频设置区域到专用页面
    _add_audio_settings(main_window, page_layout)
    
    return page

def _add_audio_settings(main_window, parent_layout):
    """添加音频设置区域"""
    audio_frame = QFrame()
    audio_frame.setObjectName("newReminderFrame")
    audio_layout = QVBoxLayout(audio_frame)
    audio_layout.setContentsMargins(16, 16, 16, 16)
    audio_layout.setSpacing(15)

    # 音频说明标签
    info_label = QLabel("自定义提醒音效设置")
    info_label.setObjectName("formTitle")
    audio_layout.addWidget(info_label)
    
    description_label = QLabel("可以选择自定义的音频文件作为提醒声音，支持多种音频格式。")
    description_label.setWordWrap(True)
    description_label.setObjectName("tipLabel")
    audio_layout.addWidget(description_label)
    
    # 当前音频文件显示区域
    audio_info_layout = QVBoxLayout()
    audio_info_layout.setSpacing(5)
    
    current_audio_label = QLabel("当前音频文件:")
    audio_info_layout.addWidget(current_audio_label)
    
    main_window.audio_path_label = QLabel("默认音频")
    main_window.audio_path_label.setObjectName("pathLabel")
    main_window.audio_path_label.setWordWrap(True)
    main_window.audio_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    audio_info_layout.addWidget(main_window.audio_path_label)
    
    audio_layout.addLayout(audio_info_layout)
    
    # 操作按钮
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(10)
    
    select_button = QPushButton("选择音频文件")
    select_button.setObjectName("primaryButton")
    select_button.clicked.connect(main_window.select_custom_audio)
    buttons_layout.addWidget(select_button)
    
    play_button = QPushButton("测试播放")
    play_button.setObjectName("actionButton")
    play_button.clicked.connect(main_window.play_test_sound)
    buttons_layout.addWidget(play_button)
    
    reset_button = QPushButton("恢复默认音频")
    reset_button.setObjectName("secondaryButton")
    reset_button.clicked.connect(main_window.reset_default_audio)
    buttons_layout.addWidget(reset_button)
    
    audio_layout.addLayout(buttons_layout)
    
    # 添加说明信息
    note_label = QLabel("选择音频后会立即生效，并用于后续的所有提醒。请确保文件大小适中以避免加载延迟。")
    note_label.setWordWrap(True)
    note_label.setObjectName("tipLabel")
    audio_layout.addWidget(note_label)
    
    # 添加支持格式信息
    formats_label = QLabel("支持的音频格式: WAV、MP3、OGG、M4A、AAC、FLAC")
    formats_label.setWordWrap(True)
    formats_label.setObjectName("tipLabel")
    audio_layout.addWidget(formats_label)
    
    # 添加弹性空间
    audio_layout.addStretch(1)
    
    parent_layout.addWidget(audio_frame)
