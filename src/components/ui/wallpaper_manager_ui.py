import os
from PySide6.QtWidgets import QFileDialog, QMessageBox, QSlider
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt

class WallpaperManagerUI:
    """壁纸管理界面相关功能"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_builder = main_window.ui_builder
        self.wallpaper_manager = main_window.wallpaper_manager
        self._updating_ui = False  # 添加标志防止循环更新
    
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
        try:
            area = self.main_window.area_combo.currentData()
            if not area:
                return
                
            # 更新壁纸预览和滑块
            path = self.wallpaper_manager.get_wallpaper(area)
            
            # 确保滑块状态正确 - 有壁纸时启用，无壁纸时禁用
            if hasattr(self.main_window, 'opacity_slider'):
                # 修复：正确转换为布尔值，而不是直接传递字符串
                has_wallpaper = bool(path and os.path.exists(path))
                self.main_window.opacity_slider.setEnabled(has_wallpaper)
            
            self.update_wallpaper_preview(area)
        except Exception as e:
            import traceback
            print(f"区域变更出错: {e}")
            traceback.print_exc()
    
    def update_wallpaper_preview(self, area):
        """更新壁纸预览显示"""
        self._updating_ui = True  # 设置标志，防止UI更新触发数据更新
        try:
            path = self.wallpaper_manager.get_wallpaper(area)
            opacity = self.wallpaper_manager.get_wallpaper_opacity(area)
            
            # 检查路径是否有效
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # 创建透明效果预览
                    base_pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # 创建一个新的图像以显示遮罩效果
                    result_pixmap = QPixmap(base_pixmap.size())
                    result_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(result_pixmap)
                    # 先绘制原始壁纸
                    painter.drawPixmap(0, 0, base_pixmap)
                    
                    # 再绘制遮罩层，透明度为设定值
                    color = QColor("#0B5394")  # 蓝色遮罩，与ColorBlock匹配
                    color.setAlphaF(opacity / 100.0)  # 转换为0-1范围
                    painter.fillRect(0, 0, base_pixmap.width(), base_pixmap.height(), color)
                    painter.end()
                    
                    self.main_window.wallpaper_preview.setPixmap(result_pixmap)
                    
                    # 更新路径和透明度信息显示
                    slider_value = 100 - opacity  # 反转值来显示透明度
                    self.main_window.path_label.setText(f"{path} (遮罩透明度: {slider_value}%)")
                    
                    # 更新透明度滑块位置，注意此处可能循环调用，需要阻断信号
                    if hasattr(self.main_window, 'opacity_slider'):
                        self.main_window.opacity_slider.blockSignals(True)
                        self.main_window.opacity_slider.setValue(slider_value)
                        # 立即更新标签显示
                        if hasattr(self.main_window, 'opacity_value_label'):
                            self.main_window.opacity_value_label.setText(f"{slider_value}%")
                        self.main_window.opacity_slider.blockSignals(False)
                        
                        # 确保滑块启用
                        self.main_window.opacity_slider.setEnabled(True)
                    return
            
            # 没有设置壁纸或加载失败
            self.main_window.wallpaper_preview.setText("无背景图片")
            self.main_window.wallpaper_preview.setPixmap(QPixmap())
            self.main_window.path_label.setText("未选择图片")
            
            # 禁用透明度滑块
            if hasattr(self.main_window, 'opacity_slider'):
                self.main_window.opacity_slider.setEnabled(False)
        finally:
            self._updating_ui = False  # 重置标志
    
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
                # 设置新壁纸时，启用滑块
                if hasattr(self.main_window, 'opacity_slider'):
                    self.main_window.opacity_slider.setEnabled(True)
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
    
    def on_opacity_changed(self, value):
        """处理透明度滑块值变化"""
        # 如果UI正在更新，忽略此事件
        if self._updating_ui:
            return
            
        try:
            # 获取当前选中的区域
            area = self.main_window.area_combo.currentData()
            if not area:
                return
                
            # 检查该区域是否有壁纸
            path = self.wallpaper_manager.get_wallpaper(area)
            if not path or not os.path.exists(path):
                # 如果当前区域没有壁纸，则不更新透明度
                return
                
            # 应用并保存新的透明度值（100-value 是遮罩的不透明度）
            saved_opacity = 100 - value  # 反转值
            
            # 直接保存透明度设置
            self.wallpaper_manager.set_wallpaper_opacity(area, saved_opacity)
            
            # 更新标签显示
            if hasattr(self.main_window, 'opacity_value_label'):
                self.main_window.opacity_value_label.setText(f"{value}%")
                
            # 只更新当前区域的预览，避免影响其他区域
            self._update_preview_only(area, saved_opacity)
        except Exception as e:
            import traceback
            print(f"透明度调整出错: {e}")
            traceback.print_exc()

    def _update_preview_only(self, area, opacity):
        """仅更新预览图，不调整滑块值"""
        path = self.wallpaper_manager.get_wallpaper(area)
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # 创建透明效果预览
                base_pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 创建一个新的图像以显示遮罩效果
                result_pixmap = QPixmap(base_pixmap.size())
                result_pixmap.fill(Qt.transparent)
                
                painter = QPainter(result_pixmap)
                painter.drawPixmap(0, 0, base_pixmap)
                
                # 应用遮罩
                color = QColor("#0B5394")
                color.setAlphaF(opacity / 100.0)
                painter.fillRect(0, 0, base_pixmap.width(), base_pixmap.height(), color)
                painter.end()
                
                self.main_window.wallpaper_preview.setPixmap(result_pixmap)
                
                # 仅更新路径文本
                slider_value = 100 - opacity
                self.main_window.path_label.setText(f"{path} (遮罩透明度: {slider_value}%)")

    def set_opacity_slider(self, slider):
        """设置透明度滑块控件引用"""
        try:
            # 先解除信号连接，避免初始化时触发不必要的更新
            if hasattr(self.main_window, 'opacity_slider') and self.main_window.opacity_slider:
                try:
                    self.main_window.opacity_slider.valueChanged.disconnect()
                except:
                    pass
            
            self.main_window.opacity_slider = slider
            
            # 连接值变化信号
            slider.valueChanged.connect(self.main_window.on_opacity_changed)
            
            # 初始化滑块值和状态
            area = self.main_window.area_combo.currentData()
            if area:
                # 获取该区域的壁纸和透明度
                path = self.wallpaper_manager.get_wallpaper(area)
                opacity = self.wallpaper_manager.get_wallpaper_opacity(area)
                
                # 检查路径是否有效，修复布尔类型参数错误
                has_wallpaper = bool(path and os.path.exists(path))
                slider.setEnabled(has_wallpaper)
                
                # 设置滑块初始值
                slider_value = 100 - opacity  # 反转值
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                
                # 确保标签显示正确
                if hasattr(self.main_window, 'opacity_value_label'):
                    self.main_window.opacity_value_label.setText(f"{slider_value}%")
        except Exception as e:
            import traceback
            print(f"设置透明度滑块出错: {e}")
            traceback.print_exc()