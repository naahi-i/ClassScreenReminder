from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QLineEdit, QDialog,
                              QFormLayout, QFileDialog, QCheckBox)
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QLinearGradient, QBrush, QPen, QColor
from PySide6.QtCore import Qt

class CardDialog(QDialog):
    """添加/编辑展示片对话框"""
    
    def __init__(self, parent=None, card_data=None):
        super().__init__(parent)
        self.setWindowTitle("添加展示片" if card_data is None else "编辑展示片")
        self.card_data = card_data or {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        
        # 姓名输入
        self.name_edit = QLineEdit(self.card_data.get("name", ""))
        self.name_edit.setPlaceholderText("请输入名称")
        layout.addRow("名称:", self.name_edit)
        
        # 标题/描述输入
        self.title_edit = QLineEdit(self.card_data.get("title", ""))
        self.title_edit.setPlaceholderText("请输入描述文字")
        layout.addRow("描述:", self.title_edit)
        
        # 图片路径显示和选择
        image_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit(self.card_data.get("image_path", ""))
        self.image_path_edit.setReadOnly(True)
        self.image_path_edit.setPlaceholderText("未选择图片")
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_image)
        
        image_layout.addWidget(self.image_path_edit)
        image_layout.addWidget(browse_button)
        layout.addRow("图片:", image_layout)
        
        # 图片形状选择
        self.round_checkbox = QCheckBox("使用圆形图片")
        self.round_checkbox.setChecked(self.card_data.get("is_round", True))
        layout.addRow("", self.round_checkbox)
        
        # 图片预览
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(80, 80)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border-radius: 40px;")
        
        # 如果有已设置的图片，显示预览
        if "image_path" in self.card_data and self.card_data["image_path"]:
            self.update_preview()
            
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch(1)
        layout.addRow("预览:", preview_layout)
        
        # 按钮区域
        buttons = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # 设置对话框大小
        self.setMinimumWidth(400)
    
    def browse_image(self):
        """浏览并选择图片"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("选择图片")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.image_path_edit.setText(file_paths[0])
                self.update_preview()
    
    def update_preview(self):
        """更新图片预览，应用填充裁剪效果"""
        image_path = self.image_path_edit.text()
        preview_size = 80
        
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 根据选择的形状应用不同样式
                is_round = self.round_checkbox.isChecked()
                # 重置样式
                self.preview_label.setStyleSheet("background-color: transparent;")
                
                # 先缩放图片以填充
                scaled_pixmap = pixmap.scaled(preview_size, preview_size, 
                                            Qt.KeepAspectRatioByExpanding, 
                                            Qt.SmoothTransformation)
                
                # 计算中心裁剪区域
                width, height = scaled_pixmap.width(), scaled_pixmap.height()
                x_offset = (width - preview_size) // 2 if width > preview_size else 0
                y_offset = (height - preview_size) // 2 if height > preview_size else 0
                
                # 裁剪中心区域
                cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, 
                                                min(width, preview_size), 
                                                min(height, preview_size))
                
                if is_round:
                    # 创建圆形图片
                    rounded_pixmap = QPixmap(preview_size, preview_size)
                    rounded_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # 创建圆形裁剪区域
                    path = QPainterPath()
                    path.addEllipse(0, 0, preview_size, preview_size)
                    painter.setClipPath(path)
                    
                    # 添加边框
                    pen = QPen(QColor(200, 200, 200, 120), 2)
                    painter.setPen(pen)
                    painter.drawEllipse(1, 1, preview_size-2, preview_size-2)
                    
                    # 绘制裁剪后的图片
                    painter.drawPixmap(0, 0, cropped_pixmap)
                    painter.end()
                    
                    self.preview_label.setPixmap(rounded_pixmap)
                else:
                    # 使用方形图片，但添加圆角
                    rounded_pixmap = QPixmap(preview_size, preview_size)
                    rounded_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # 创建圆角矩形裁剪区域
                    path = QPainterPath()
                    corner_radius = 12  # 增大圆角半径
                    path.addRoundedRect(0, 0, preview_size, preview_size, corner_radius, corner_radius)
                    painter.setClipPath(path)
                    
                    # 添加边框
                    pen = QPen(QColor(200, 200, 200, 120), 2)
                    painter.setPen(pen)
                    painter.drawRoundedRect(1, 1, preview_size-2, preview_size-2, corner_radius, corner_radius)
                    
                    # 绘制裁剪后的图片
                    painter.drawPixmap(0, 0, cropped_pixmap)
                    painter.end()
                    
                    self.preview_label.setPixmap(rounded_pixmap)
                
                return
                
        # 如果没有图片，显示默认占位符 - 使用渐变背景
        is_round = self.round_checkbox.isChecked()
        
        # 创建高级默认预览图
        default_pixmap = QPixmap(preview_size, preview_size)
        default_pixmap.fill(Qt.transparent)
        
        painter = QPainter(default_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, preview_size, preview_size)
        gradient.setColorAt(0, QColor(100, 149, 237))  # 淡蓝色
        gradient.setColorAt(1, QColor(65, 105, 225))   # 皇家蓝
        
        if is_round:
            # 绘制圆形
            path = QPainterPath()
            path.addEllipse(0, 0, preview_size, preview_size)
            painter.setClipPath(path)
            
            # 填充渐变
            painter.fillPath(path, QBrush(gradient))
            
            # 边框
            pen = QPen(QColor(200, 200, 200), 2)
            painter.setPen(pen)
            painter.drawEllipse(1, 1, preview_size-2, preview_size-2)
        else:
            # 绘制圆角矩形
            corner_radius = 12
            path = QPainterPath()
            path.addRoundedRect(0, 0, preview_size, preview_size, corner_radius, corner_radius)
            painter.setClipPath(path)
            
            # 填充渐变
            painter.fillPath(path, QBrush(gradient))
            
            # 边框
            pen = QPen(QColor(200, 200, 200), 2)
            painter.setPen(pen)
            painter.drawRoundedRect(1, 1, preview_size-2, preview_size-2, corner_radius, corner_radius)
        
        # 添加问号图标
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPixelSize(32)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(default_pixmap.rect(), Qt.AlignCenter, "?")
        
        painter.end()
        self.preview_label.setPixmap(default_pixmap)
    
    def get_card_data(self):
        """获取展示片数据"""
        return {
            "name": self.name_edit.text(),
            "title": self.title_edit.text(),
            "image_path": self.image_path_edit.text(),
            "is_round": self.round_checkbox.isChecked()
        }

class CardManagerUI:
    """名片管理界面"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.card_manager = main_window.card_manager
    
    def add_card(self):
        """添加新展示片"""
        dialog = CardDialog(self.main_window)
        if dialog.exec():
            card_data = dialog.get_card_data()
            self.card_manager.add_card(card_data)
            self.update_card_list()
    
    def edit_card(self):
        """编辑展示片"""
        current_row = self.main_window.card_list.currentRow()
        if current_row >= 0:
            cards = self.card_manager.get_all_cards()
            dialog = CardDialog(self.main_window, cards[current_row])
            if dialog.exec():
                card_data = dialog.get_card_data()
                self.card_manager.delete_card(current_row)
                self.card_manager.add_card(card_data)
                self.update_card_list()
    
    def delete_card(self):
        """删除展示片"""
        current_row = self.main_window.card_list.currentRow()
        if current_row >= 0:
            self.card_manager.delete_card(current_row)
            self.update_card_list()
    
    def update_card_list(self):
        """更新展示片列表显示"""
        self.main_window.card_list.clear()
        for card in self.card_manager.get_all_cards():
            display_text = f"{card['name']}" + (f" - {card['title']}" if card.get('title') else "")
            self.main_window.card_list.addItem(display_text)
