import os
import json
import logging
from pathlib import Path

# 配置日志（当单独运行此文件时使用）
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ConfigManager")

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 获取用户配置目录
        self.app_data_dir = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~/.config')),
            'ClassScreenReminder'
        )
        
        # 创建配置目录
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # 配置文件路径
        self.config_file = os.path.join(self.app_data_dir, 'config.json')
        
        # 创建默认配置文件(如果不存在)
        if not os.path.exists(self.config_file):
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "reminders": [],
            "settings": {
                "start_with_windows": False,     # 默认开机自启动
                "minimize_to_tray": True,       # 默认关闭时最小化到托盘
                "startup_minimized": True,      # 默认启动时最小化
                "wallpaper_path": "",           # 保留旧版本兼容性
                "wallpapers": {},               # 新增多区域壁纸设置
                "theme": "light",               # 新增主题设置: light或dark
                "accent_color": "#0067C0",      # 强调色
                "custom_audio_path": ""         # 自定义音频路径
            }
        }
        
        self.save_config(default_config)
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 配置文件损坏或不存在时创建默认配置
            self.create_default_config()
            return self.load_config()
    
    def save_config(self, config):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def _sanitize_reminder_duration(self, reminder):
        """确保提醒持续时间合法"""
        if "duration" in reminder:
            try:
                reminder["duration"] = max(1, int(reminder["duration"]))
            except (ValueError, TypeError):
                reminder["duration"] = 10
        
        # 确保play_sound字段存在，默认为True
        reminder.setdefault("play_sound", True)
        
        # 确保weekdays字段存在且长度为7，默认为一周所有天都启用
        reminder["weekdays"] = (reminder.get("weekdays", [True] * 7)[:7] + [True] * 7)[:7]
        return reminder
    
    def load_reminders(self):
        """加载提醒列表"""
        config = self.load_config()
        reminders = config.get("reminders", [])
        
        # 确保所有提醒的持续时间是合法的整数
        return [self._sanitize_reminder_duration(reminder) for reminder in reminders]
    
    def save_reminders(self, reminders):
        """保存提醒列表"""
        # 确保持续时间是整数
        sanitized_reminders = [self._sanitize_reminder_duration(reminder) for reminder in reminders]
        
        config = self.load_config()
        config["reminders"] = sanitized_reminders
        self.save_config(config)
    
    def get_setting(self, key, default=None):
        """获取设置值"""
        config = self.load_config()
        return config.get("settings", {}).get(key, default)
    
    def set_setting(self, key, value):
        """设置配置项"""
        config = self.load_config()
        if "settings" not in config:
            config["settings"] = {}
        config["settings"][key] = value
        self.save_config(config)
    
    def get_wallpaper_path(self):
        """获取壁纸路径"""
        return self.get_setting("wallpaper_path", "")
    
    def set_wallpaper_path(self, path):
        """设置壁纸路径"""
        self.set_setting("wallpaper_path", path)
    
    def get_startup_minimized(self):
        """获取是否启动时最小化到系统托盘的设置"""
        return self.get_setting("startup_minimized", True)
    
    def set_startup_minimized(self, value):
        """设置是否启动时最小化到系统托盘"""
        self.set_setting("startup_minimized", bool(value))
    
    def get_minimize_to_tray(self):
        """获取关闭窗口时是否最小化到系统托盘的设置"""
        return True  # 始终返回True，强制关闭时最小化到托盘
    
    def set_minimize_to_tray(self, value):
        """设置关闭窗口时是否最小化到系统托盘"""
        self.set_setting("minimize_to_tray", bool(value))
    
    def get_theme(self):
        """获取当前主题设置"""
        return self.get_setting("theme", "light")
    
    def set_theme(self, theme):
        """设置主题"""
        if theme in ["light", "dark"]:
            self.set_setting("theme", theme)
            return True
        return False
    
    def get_accent_color(self):
        """获取强调色"""
        return self.get_setting("accent_color", "#0067C0")
    
    def set_accent_color(self, color):
        """设置强调色"""
        self.set_setting("accent_color", color)

# 添加测试代码，便于直接运行此文件
if __name__ == "__main__":
    # 测试配置管理器
    config_manager = ConfigManager()
    reminders = config_manager.load_reminders()
    
    print(f"已加载 {len(reminders)} 个提醒:")
    for i, reminder in enumerate(reminders):
        print(f"  {i+1}. {reminder['time']} - {reminder['message']} ({reminder['duration']}秒)")
