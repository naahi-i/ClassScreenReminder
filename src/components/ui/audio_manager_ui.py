import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

class AudioManagerUI:
    """处理音频管理界面相关功能"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_builder = main_window.ui_builder
    
    def select_custom_audio(self):
        """选择自定义音频文件"""
        # 从音频管理器获取支持的格式
        try:
            from src.utils.sound_manager import get_supported_formats
            supported_formats = get_supported_formats()
            
            # 构建文件过滤器字符串，包含所有支持的格式
            filters = []
            for format_key, format_desc in supported_formats.items():
                filters.append(format_desc)
            
            # 添加一个包含所有格式的选项
            all_extensions = " ".join([f"*.{fmt}" for fmt in supported_formats.keys()])
            filters.insert(0, f"所有支持的音频文件 ({all_extensions})")
            
            # 连接所有过滤器
            file_filter = ";;".join(filters)
        except Exception:
            # 默认格式
            file_filter = "音频文件 (*.wav *.mp3 *.ogg *.m4a *.aac *.flac);;Wave音频文件 (*.wav)"
        
        # 打开文件选择对话框
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.main_window,
            "选择音频文件",
            "",
            file_filter
        )
        
        if file_path:
            from src.utils.sound_manager import set_custom_audio
            
            if set_custom_audio(file_path):
                self.update_audio_path_display()
                self.ui_builder.show_message("设置成功", "已设置自定义音频，将在下一次提醒时使用。")
            else:
                self.ui_builder.show_warning("设置失败", "无法设置音频文件，请确认文件格式正确且可访问。")
    
    def reset_default_audio(self):
        """恢复默认音频设置"""
        from src.utils.sound_manager import reset_to_default_audio
        
        if reset_to_default_audio():
            self.update_audio_path_display()
            self.ui_builder.show_message("设置成功", "已恢复默认音频设置。")
        else:
            self.ui_builder.show_warning("恢复失败", "无法恢复默认音频，请确认默认音频文件存在。")
    
    def play_test_sound(self):
        """测试播放当前音效"""
        from src.utils.sound_manager import play_initial_sound
        
        if play_initial_sound():
            pass  # 播放成功无需提示
        else:
            self.ui_builder.show_warning("播放失败", "无法播放音频，请检查音频文件设置。")
    
    def update_audio_path_display(self):
        """更新音频路径显示"""
        from src.utils.sound_manager import get_current_audio_path, get_current_audio_format
        
        current_path = get_current_audio_path()
        current_format = get_current_audio_format().upper()
        
        if current_path:
            # 检查是否是默认路径
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            default_path = os.path.join(app_dir, "resources", "attend_class.wav")
            
            if os.path.normpath(current_path) == os.path.normpath(default_path):
                self.main_window.audio_path_label.setText("默认音频 (WAV)")
            else:
                # 显示路径和格式
                self.main_window.audio_path_label.setText(f"{current_path}\n({current_format})")
        else:
            self.main_window.audio_path_label.setText("未设置音频")