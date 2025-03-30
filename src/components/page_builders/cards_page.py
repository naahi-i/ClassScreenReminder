from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QFrame, QSplitter)
from PySide6.QtCore import Qt

def create_cards_page(main_window):
    """创建展示片管理页面"""
    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(15)
    
    # 创建展示片管理区域
    cards_frame = QFrame()
    cards_frame.setObjectName("newReminderFrame")
    cards_layout = QVBoxLayout(cards_frame)
    cards_layout.setContentsMargins(16, 16, 16, 16)
    cards_layout.setSpacing(15)
    
    # 标题和说明
    title = QLabel("卡片管理")
    title.setObjectName("formTitle")
    cards_layout.addWidget(title)
    
    description = QLabel("在这里添加展示卡片，它们将在全屏提醒时显示在左侧区域。支持只有图片的卡片和带文字描述的卡片两种形式。")
    description.setObjectName("tipLabel")
    description.setWordWrap(True)
    cards_layout.addWidget(description)
    
    # 展示片列表
    main_window.card_list = QListWidget()
    cards_layout.addWidget(main_window.card_list)
    
    # 操作按钮
    buttons_layout = QHBoxLayout()
    
    add_button = QPushButton("添加卡片")
    add_button.setObjectName("primaryButton")
    add_button.clicked.connect(main_window.add_card)
    buttons_layout.addWidget(add_button)
    
    edit_button = QPushButton("编辑卡片")
    edit_button.setObjectName("actionButton")
    edit_button.clicked.connect(main_window.edit_card)
    buttons_layout.addWidget(edit_button)
    
    delete_button = QPushButton("删除卡片")
    delete_button.setObjectName("secondaryButton")
    delete_button.clicked.connect(main_window.delete_card)
    buttons_layout.addWidget(delete_button)
    
    cards_layout.addLayout(buttons_layout)
    
    page_layout.addWidget(cards_frame)
    
    # 更新展示片列表
    main_window.card_manager_ui.update_card_list()
    
    return page
