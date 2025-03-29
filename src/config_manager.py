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
                "start_with_windows": False,
                "minimize_to_tray": True
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

# 添加测试代码，便于直接运行此文件
if __name__ == "__main__":
    # 测试配置管理器
    config_manager = ConfigManager()
    reminders = config_manager.load_reminders()
    
    print(f"已加载 {len(reminders)} 个提醒:")
    for i, reminder in enumerate(reminders):
        print(f"  {i+1}. {reminder['time']} - {reminder['message']} ({reminder['duration']}秒)")
