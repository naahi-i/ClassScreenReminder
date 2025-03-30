import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class WallpaperManagerUI:
    """壁纸管理界面相关功能"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_builder = main_window.ui_builder
        self.wallpaper_manager = main_window.wallpaper_manager
    
    def select_wallpaper(self):
        """选择壁纸"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "选择背景图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            # 更新配置
            self.main_window.reminder_manager.set_wallpaper_path(file_path)
            self.ui_builder.show_message("设置成功", "背景图片已设置，将在下次提醒时显示。")
    
    def clear_wallpaper(self):
        """清除壁纸"""
        self.main_window.reminder_manager.set_wallpaper_path("")
        self.ui_builder.show_message("设置成功", "背景图片已清除，将在下次提醒时恢复默认背景。")
    
    def on_area_changed(self, index):
        """区域选择变化时更新显示"""
        area = self.main_window.area_combo.currentData()
        self.update_wallpaper_preview(area)
    
    def update_wallpaper_preview(self, area):
        """更新壁纸预览显示"""
        path = self.wallpaper_manager.get_wallpaper(area)
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.main_window.wallpaper_preview.setPixmap(pixmap)
                self.main_window.path_label.setText(path)
                return
        
        # 没有设置壁纸或加载失败
        self.main_window.wallpaper_preview.setText("无背景图片")
        self.main_window.wallpaper_preview.setPixmap(QPixmap())
        self.main_window.path_label.setText("未选择图片")
    
    def select_area_wallpaper(self):
        """为当前选择的区域选择壁纸"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "选择背景图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            area = self.main_window.area_combo.currentData()
            if self.wallpaper_manager.set_wallpaper(area, file_path):
                self.update_wallpaper_preview(area)
                self.ui_builder.show_message("设置成功", f"已为 {self.main_window.area_combo.currentText()} 设置背景图片")
            else:
                self.ui_builder.show_warning("设置失败", "无法设置背景图片，请确认文件存在且可访问")
    
    def clear_area_wallpaper(self):
        """清除当前选择区域的壁纸"""
        area = self.main_window.area_combo.currentData()
        self.wallpaper_manager.clear_wallpaper(area)
        self.update_wallpaper_preview(area)
        self.ui_builder.show_message("操作成功", f"已清除 {self.main_window.area_combo.currentText()} 的背景图片")
    
    def clear_all_wallpapers(self):
        """清除所有区域的壁纸"""
        reply = self.ui_builder.show_question(
            "确认操作", 
            "确定要清除所有区域的背景图片吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.wallpaper_manager.clear_wallpaper()
            area = self.main_window.area_combo.currentData()
            self.update_wallpaper_preview(area)
            self.ui_builder.show_message("操作成功", "已清除所有区域的背景图片")