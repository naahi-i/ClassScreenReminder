import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .ui_components import SidebarMenu
from .page_builders.reminders_page import create_reminders_page
from .page_builders.wallpaper_page import create_wallpaper_page
from .page_builders.settings_page import create_settings_page
from .page_builders.about_page import create_about_page

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
        page = create_reminders_page(self.main_window)
        self.main_window.content_stack.addWidget(page)
        self.content_pages["reminders"] = 0  # 保存页面索引
        self.main_window.weekday_checkboxes = self.weekday_checkboxes
    
    def _create_wallpaper_page(self):
        """创建壁纸设置页面"""
        page = create_wallpaper_page(self.main_window)
        self.main_window.content_stack.addWidget(page)
        self.content_pages["wallpapers"] = 1  # 保存页面索引
    
    def _create_settings_page(self):
        """创建应用设置页面"""
        page = create_settings_page(self.main_window)
        self.main_window.content_stack.addWidget(page)
        self.content_pages["settings"] = 2  # 保存页面索引
        
        # 创建关于页面
        about_page = create_about_page(self.main_window)
        self.main_window.content_stack.addWidget(about_page)
        self.content_pages["about"] = 3  # 保存页面索引
    
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
