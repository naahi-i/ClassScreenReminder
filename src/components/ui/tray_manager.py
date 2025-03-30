import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction

class TrayManager:
    """系统托盘图标管理类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_tray()
    
    def setup_tray(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self.main_window)
        
        # 尝试查找应用图标
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        icon_path = os.path.join(base_dir, "icon.ico")
        
        icon = QIcon(icon_path) if os.path.exists(icon_path) else None
        
        # 如果没有找到图标文件，使用内置的系统图标
        if icon is None or icon.isNull():
            # 使用系统内置信息图标
            from PySide6.QtWidgets import QStyle
            icon = self.main_window.style().standardIcon(QStyle.SP_MessageBoxInformation)
        
        self.tray_icon.setIcon(icon)
        
        # 创建托盘菜单
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #202020;
                border: 1px solid #e1e1e1;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #202020;
            }
            QMenu::item:selected {
                background-color: rgba(0, 103, 192, 0.08);
                color: #0067C0;
            }
        """)
        
        show_action = QAction("显示窗口", self.main_window)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        exit_action = QAction("退出", self.main_window)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 设置悬停提示文本
        self.tray_icon.setToolTip("屏幕提醒工具")
        
        # 确保设置图标后再显示
        if not icon.isNull():
            self.tray_icon.show()
        else:
            print("警告: 无法设置系统托盘图标")
    
    def close_application(self):
        """彻底关闭应用"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def show_from_tray(self):
        """从托盘显示窗口"""
        self.main_window.showNormal()
        self.main_window.activateWindow()  # 在Windows上激活窗口并设置焦点
    
    def tray_icon_activated(self, reason):
        """处理托盘图标点击事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()
    
    def is_visible(self):
        """检查托盘图标是否可见"""
        return self.tray_icon.isVisible()