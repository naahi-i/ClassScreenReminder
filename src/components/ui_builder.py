import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTimeEdit, QListWidget, QFormLayout, 
                              QSpinBox, QFrame, QTextEdit, QCheckBox, QGroupBox, 
                              QGridLayout, QMessageBox, QFileDialog, QComboBox,
                              QTabWidget, QMenu, QStackedWidget)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QIcon, QPixmap, QAction

from .ui_components import SidebarMenu
from PySide6.QtGui import QPainter, QPainterPath

class MainWindowUI:
    """主窗口UI构建器，负责创建和设置UI组件"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.weekday_checkboxes = []
        self.content_pages = {}
    
    def setup_ui(self):
        """设置用户界面"""
        self.main_window.setWindowTitle("屏幕提醒")
        self.main_window.setMinimumSize(900, 600)  # 增加窗口尺寸以适应新的布局
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icon.ico")
        if os.path.exists(icon_path):
            self.main_window.setWindowIcon(QIcon(icon_path))
        
        # 创建中央部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.main_window.setCentralWidget(central_widget)
        
        # 主布局 - 水平布局，左侧菜单，右侧内容
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏菜单
        self._create_sidebar_menu(main_layout)
        
        # 创建内容区域容器
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # 添加标题
        self._add_title_section(content_layout)
        
        # 创建堆叠部件用于切换不同页面
        self.main_window.content_stack = QStackedWidget()
        content_layout.addWidget(self.main_window.content_stack)
        
        # 创建不同功能页面
        self._create_reminders_page()
        self._create_wallpaper_page()
        self._create_settings_page()
        
        # 将内容容器添加到主布局
        main_layout.addWidget(content_container)
        
        # 设置内容比例 (左:右 = 2:8)
        main_layout.setStretch(0, 2)
        main_layout.setStretch(1, 8)

    def _create_sidebar_menu(self, parent_layout):
        """创建侧边栏菜单"""
        # 定义菜单项目
        menu_items = [
            ("reminders", "提醒管理", True),
            ("wallpapers", "背景图片", False),
            ("settings", "应用设置", False)
        ]
        
        # 创建侧边栏
        self.main_window.sidebar = SidebarMenu()
        
        # 添加菜单项
        for menu_id, text, is_active in menu_items:
            self.main_window.sidebar.add_menu_item(menu_id, text, is_active)
        
        # 添加弹性空间
        self.main_window.sidebar.add_spacer()
        
        # 添加关于菜单项
        self.main_window.sidebar.add_menu_item("about", "关于", False)
        
        # 连接菜单变化信号
        self.main_window.sidebar.menuChanged.connect(self.main_window.on_menu_changed)
        
        parent_layout.addWidget(self.main_window.sidebar)

    def _add_title_section(self, parent_layout):
        """添加标题部分"""
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 15)
        
        title_label = QLabel("屏幕提醒设置")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        parent_layout.addWidget(title_frame)
    
    def _create_reminders_page(self):
        """创建提醒管理页面"""
        page = QWidget()
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(20)
        
        # 创建左侧面板 - 提醒列表区域
        left_panel = self._create_left_panel()
        page_layout.addWidget(left_panel)
        
        # 创建右侧面板 - 添加新提醒区域
        right_panel = self._create_right_panel()
        page_layout.addWidget(right_panel)
        
        # 设置内容比例 (左:右 = 4:6)
        page_layout.setStretch(0, 4)
        page_layout.setStretch(1, 6)
        
        # 添加到堆叠部件
        self.main_window.content_stack.addWidget(page)
        self.content_pages["reminders"] = 0  # 保存页面索引
    
    def _create_wallpaper_page(self):
        """创建壁纸设置页面"""
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(15)
        
        # 添加壁纸设置区域到专用页面
        self._add_wallpaper_settings(page_layout)
        
        # 添加到堆叠部件
        self.main_window.content_stack.addWidget(page)
        self.content_pages["wallpapers"] = 1  # 保存页面索引
    
    def _create_settings_page(self):
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
        self.main_window.autostart_checkbox = QCheckBox("开机时自动启动应用")
        self.main_window.autostart_checkbox.setChecked(True)
        self.main_window.autostart_checkbox.toggled.connect(self.main_window.toggle_autostart)
        settings_layout.addWidget(self.main_window.autostart_checkbox)
        
        # 添加启动时最小化选项
        self.main_window.startup_minimized_checkbox = QCheckBox("启动时最小化到系统托盘")
        self.main_window.startup_minimized_checkbox.setChecked(self.main_window.startup_minimized)
        self.main_window.startup_minimized_checkbox.toggled.connect(self.main_window.on_startup_minimized_changed)
        settings_layout.addWidget(self.main_window.startup_minimized_checkbox)
        
        # 弹性空间
        settings_layout.addStretch(1)
        
        page_layout.addWidget(settings_frame)
        
        # 添加到堆叠部件
        self.main_window.content_stack.addWidget(page)
        self.content_pages["settings"] = 2  # 保存页面索引
        
        # 创建关于页面
        about_page = self._create_about_page()
        self.main_window.content_stack.addWidget(about_page)
        self.content_pages["about"] = 3  # 保存页面索引

    def _create_about_page(self):
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
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icon.ico")
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
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
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

    def _create_left_panel(self):
        """创建左侧面板 - 提醒列表区域"""
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        list_label = QLabel("已设置的提醒:")
        list_label.setObjectName("sectionLabel")
        left_layout.addWidget(list_label)
        
        self.main_window.reminder_list = QListWidget()
        self.main_window.reminder_list.setObjectName("reminderList")
        self.main_window.reminder_list.setMinimumHeight(400)  # 增加高度
        self.main_window.reminder_list.setMinimumWidth(300)   # 设置最小宽度
        left_layout.addWidget(self.main_window.reminder_list)
        
        # 操作按钮布局
        list_buttons_layout = QHBoxLayout()
        list_buttons_layout.setSpacing(8)
        
        self.main_window.edit_button = QPushButton("编辑选中")
        self.main_window.edit_button.setObjectName("actionButton")
        self.main_window.edit_button.clicked.connect(self.main_window.edit_reminder)
        list_buttons_layout.addWidget(self.main_window.edit_button)
        
        self.main_window.delete_button = QPushButton("删除提醒")
        self.main_window.delete_button.setObjectName("secondaryButton")
        self.main_window.delete_button.clicked.connect(self.main_window.delete_reminder)
        list_buttons_layout.addWidget(self.main_window.delete_button)
        
        left_layout.addLayout(list_buttons_layout)
        
        return left_panel
    
    def _create_right_panel(self):
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
        self._add_form_controls(form_layout)
        
        right_layout.addWidget(form_frame)
        
        # 添加表单按钮
        self._add_buttons(right_layout)
        
        return right_panel
    
    def _add_wallpaper_settings(self, parent_layout):
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
        
        self.main_window.area_combo = QComboBox()
        self.main_window.area_combo.setObjectName("areaCombo")
        self.main_window.area_combo.addItem("中间区域", "main")
        self.main_window.area_combo.addItem("左侧区域", "left")
        self.main_window.area_combo.addItem("上部区域", "top")
        self.main_window.area_combo.addItem("装饰区域", "accent")
        self.main_window.area_combo.currentIndexChanged.connect(self.main_window.on_area_changed)
        area_layout.addWidget(self.main_window.area_combo)
        
        wallpaper_layout.addLayout(area_layout)
        
        # 预览和路径显示
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(5)
        
        self.main_window.wallpaper_preview = QLabel("无背景图片")
        self.main_window.wallpaper_preview.setObjectName("wallpaperPreview")
        self.main_window.wallpaper_preview.setAlignment(Qt.AlignCenter)
        self.main_window.wallpaper_preview.setMinimumHeight(180)
        self.main_window.wallpaper_preview.setStyleSheet("""
            QLabel#wallpaperPreview {
                background-color: #f5f5f5;
                border: 1px dashed #d0d0d0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        preview_layout.addWidget(self.main_window.wallpaper_preview)
        
        self.main_window.path_label = QLabel("未选择图片")
        self.main_window.path_label.setObjectName("pathLabel")
        self.main_window.path_label.setWordWrap(True)
        self.main_window.path_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.main_window.path_label)
        
        wallpaper_layout.addLayout(preview_layout)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        select_button = QPushButton("选择背景图片")
        select_button.setObjectName("primaryButton")
        select_button.clicked.connect(self.main_window.select_area_wallpaper)
        buttons_layout.addWidget(select_button)
        
        clear_button = QPushButton("清除当前背景")
        clear_button.setObjectName("actionButton")
        clear_button.clicked.connect(self.main_window.clear_area_wallpaper)
        buttons_layout.addWidget(clear_button)
        
        clear_all_button = QPushButton("清除所有背景")
        clear_all_button.setObjectName("secondaryButton")
        clear_all_button.clicked.connect(self.main_window.clear_all_wallpapers)
        buttons_layout.addWidget(clear_all_button)
        
        wallpaper_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(wallpaper_frame)
    
    def _add_form_controls(self, form_layout):
        """添加表单控件"""
        # 时间编辑器
        self.main_window.time_edit = QTimeEdit()
        self.main_window.time_edit.setDisplayFormat("HH:mm")
        self.main_window.time_edit.setTime(QTime.currentTime())
        self.main_window.time_edit.setObjectName("timeEdit")
        form_layout.addRow("提醒时间:", self.main_window.time_edit)
        
        # 持续时间调整
        self.main_window.duration_spinbox = QSpinBox()
        self.main_window.duration_spinbox.setRange(1, 60)
        self.main_window.duration_spinbox.setValue(10)
        self.main_window.duration_spinbox.setSuffix(" 秒")
        self.main_window.duration_spinbox.setObjectName("durationSpinBox")
        form_layout.addRow("显示时长:", self.main_window.duration_spinbox)
        
        # 添加声音设置复选框
        self.main_window.sound_checkbox = QCheckBox("播放提醒声音")
        self.main_window.sound_checkbox.setChecked(True)
        self.main_window.sound_checkbox.setObjectName("soundCheckBox")
        form_layout.addRow("声音设置:", self.main_window.sound_checkbox)
        
        # 星期选择组
        weekday_group = QGroupBox("启用的星期")
        weekday_group.setObjectName("weekdayGroup")
        weekday_layout = QGridLayout(weekday_group)
        weekday_layout.setSpacing(8)
        weekday_layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建星期复选框
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.weekday_checkboxes = []
        
        # 每行放置4个复选框，更紧凑
        for i, name in enumerate(weekday_names):
            row = i // 4
            col = i % 4
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)  # 默认选中
            self.weekday_checkboxes.append(checkbox)
            weekday_layout.addWidget(checkbox, row, col)
        
        form_layout.addRow("星期设置:", weekday_group)
        self.main_window.weekday_checkboxes = self.weekday_checkboxes
        
        # 使用QTextEdit替换QLineEdit以支持多行输入
        self.main_window.message_edit = QTextEdit()
        self.main_window.message_edit.setPlaceholderText("输入提醒消息...\n可输入多行，每行将显示为单独的消息")
        self.main_window.message_edit.setObjectName("messageEdit")
        self.main_window.message_edit.setMinimumHeight(80)  # 设置最小高度
        self.main_window.message_edit.setMaximumHeight(120)  # 设置最大高度
        # 简化样式
        self.main_window.message_edit.setStyleSheet("""
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
        form_layout.addRow("提醒消息:", self.main_window.message_edit)
    
    def _add_buttons(self, parent_layout):
        """添加按钮区域"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 添加提醒按钮
        self.main_window.add_button = QPushButton("添加提醒")
        self.main_window.add_button.setObjectName("primaryButton")
        self.main_window.add_button.clicked.connect(self.main_window.add_reminder)
        buttons_layout.addWidget(self.main_window.add_button)
        
        # 测试提醒按钮
        self.main_window.test_button = QPushButton("测试效果")
        self.main_window.test_button.setObjectName("actionButton")
        self.main_window.test_button.clicked.connect(self.main_window.test_reminder)
        buttons_layout.addWidget(self.main_window.test_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """显示消息对话框"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec()
    
    def show_warning(self, title, message):
        """显示警告对话框"""
        return self.show_message(title, message, QMessageBox.Warning)
    
    def show_question(self, title, message, buttons=QMessageBox.Yes | QMessageBox.No, default_button=QMessageBox.No):
        """显示询问对话框"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(default_button)
        return msg_box.exec()
