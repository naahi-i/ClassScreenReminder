from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTimeEdit, QListWidget, QFormLayout, 
                              QSpinBox, QFrame, QTextEdit, QCheckBox, QGroupBox, 
                              QGridLayout)
from PySide6.QtCore import Qt, QTime

def create_reminders_page(main_window):
    """创建提醒管理页面"""
    page = QWidget()
    page_layout = QHBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(20)
    
    # 创建左侧面板 - 提醒列表区域
    left_panel = _create_left_panel(main_window)
    page_layout.addWidget(left_panel)
    
    # 创建右侧面板 - 添加新提醒区域
    right_panel = _create_right_panel(main_window)
    page_layout.addWidget(right_panel)
    
    # 设置内容比例 (左:右 = 4:6)
    page_layout.setStretch(0, 4)
    page_layout.setStretch(1, 6)
    
    return page

def _create_left_panel(main_window):
    """创建左侧面板 - 提醒列表区域"""
    left_panel = QFrame()
    left_panel.setObjectName("leftPanel")
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(10)
    
    list_label = QLabel("已设置的提醒:")
    list_label.setObjectName("sectionLabel")
    left_layout.addWidget(list_label)
    
    main_window.reminder_list = QListWidget()
    main_window.reminder_list.setObjectName("reminderList")
    main_window.reminder_list.setMinimumHeight(400)  # 增加高度
    main_window.reminder_list.setMinimumWidth(300)   # 设置最小宽度
    left_layout.addWidget(main_window.reminder_list)
    
    # 操作按钮布局
    list_buttons_layout = QHBoxLayout()
    list_buttons_layout.setSpacing(8)
    
    main_window.edit_button = QPushButton("编辑选中")
    main_window.edit_button.setObjectName("actionButton")
    main_window.edit_button.clicked.connect(main_window.edit_reminder)
    list_buttons_layout.addWidget(main_window.edit_button)
    
    main_window.delete_button = QPushButton("删除提醒")
    main_window.delete_button.setObjectName("secondaryButton")
    main_window.delete_button.clicked.connect(main_window.delete_reminder)
    list_buttons_layout.addWidget(main_window.delete_button)
    
    left_layout.addLayout(list_buttons_layout)
    
    return left_panel

def _create_right_panel(main_window):
    """创建右侧面板 - 添加新提醒区域"""
    right_panel = QFrame()
    right_panel.setObjectName("rightPanel")
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(16)
    
    # 新提醒表单
    form_frame = QFrame()
    form_frame.setObjectName("newReminderFrame")
    form_layout = QFormLayout(form_frame)
    form_layout.setContentsMargins(16, 16, 16, 16)
    form_layout.setSpacing(15)
    form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
    form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    
    # 表单标题
    form_title = QLabel("添加新提醒")
    form_title.setObjectName("formTitle")
    form_layout.addRow(form_title)
    
    # 添加表单控件
    _add_form_controls(main_window, form_layout)
    
    right_layout.addWidget(form_frame)
    
    # 添加表单按钮
    _add_buttons(main_window, right_layout)
    
    return right_panel

def _add_form_controls(main_window, form_layout):
    """添加表单控件"""
    # 时间编辑器
    main_window.time_edit = QTimeEdit()
    main_window.time_edit.setDisplayFormat("HH:mm")
    main_window.time_edit.setTime(QTime.currentTime())
    main_window.time_edit.setObjectName("timeEdit")
    form_layout.addRow("提醒时间:", main_window.time_edit)
    
    # 持续时间调整
    main_window.duration_spinbox = QSpinBox()
    main_window.duration_spinbox.setRange(1, 60)
    main_window.duration_spinbox.setValue(10)
    main_window.duration_spinbox.setSuffix(" 秒")
    main_window.duration_spinbox.setObjectName("durationSpinBox")
    form_layout.addRow("显示时长:", main_window.duration_spinbox)
    
    # 添加声音设置复选框
    main_window.sound_checkbox = QCheckBox("播放提醒声音")
    main_window.sound_checkbox.setChecked(True)
    main_window.sound_checkbox.setObjectName("soundCheckBox")
    form_layout.addRow("声音设置:", main_window.sound_checkbox)
    
    # 星期选择组
    weekday_group = QGroupBox("启用的星期")
    weekday_group.setObjectName("weekdayGroup")
    weekday_layout = QGridLayout(weekday_group)
    weekday_layout.setSpacing(8)
    weekday_layout.setContentsMargins(10, 5, 10, 5)
    
    # 创建星期复选框
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    main_window.weekday_checkboxes = []
    
    # 每行放置4个复选框，更紧凑
    for i, name in enumerate(weekday_names):
        row = i // 4
        col = i % 4
        checkbox = QCheckBox(name)
        checkbox.setChecked(True)  # 默认选中
        main_window.weekday_checkboxes.append(checkbox)
        weekday_layout.addWidget(checkbox, row, col)
    
    form_layout.addRow("星期设置:", weekday_group)
    
    # 使用QTextEdit替换QLineEdit以支持多行输入
    main_window.message_edit = QTextEdit()
    main_window.message_edit.setPlaceholderText("输入提醒消息...\n可输入多行，每行将显示为单独的消息")
    main_window.message_edit.setObjectName("messageEdit")
    main_window.message_edit.setMinimumHeight(80)  # 设置最小高度
    main_window.message_edit.setMaximumHeight(120)  # 设置最大高度
    # 简化样式
    main_window.message_edit.setStyleSheet("""
        QTextEdit {
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            padding: 10px 10px 10px 12px;
            background-color: white;
            color: #333333;
            font-size: 14px;
            font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
        }
        QTextEdit:focus {
            border-color: #0078d4;
            border-left-width: 3px;
        }
    """)
    form_layout.addRow("提醒消息:", main_window.message_edit)

def _add_buttons(main_window, parent_layout):
    """添加按钮区域"""
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(10)
    
    # 添加提醒按钮
    main_window.add_button = QPushButton("添加提醒")
    main_window.add_button.setObjectName("primaryButton")
    main_window.add_button.clicked.connect(main_window.add_reminder)
    buttons_layout.addWidget(main_window.add_button)
    
    # 测试提醒按钮
    main_window.test_button = QPushButton("测试效果")
    main_window.test_button.setObjectName("actionButton")
    main_window.test_button.clicked.connect(main_window.test_reminder)
    buttons_layout.addWidget(main_window.test_button)
    
    parent_layout.addLayout(buttons_layout)
