"""
配置管理类 - 处理应用配置的保存和加载
"""
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
            os.environ.get('APPDATA', 
                          os.path.expanduser('~/.config')),
            'ClassScreenReminder'
        )
        
        # 创建配置目录(如果不存在)
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
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    
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
    
    def load_reminders(self):
        """加载提醒列表"""
        config = self.load_config()
        reminders = config.get("reminders", [])
        
        # 确保所有提醒的持续时间是整数
        for reminder in reminders:
            if "duration" in reminder:
                try:
                    reminder["duration"] = int(reminder["duration"])
                    # 确保duration至少为1秒
                    if reminder["duration"] < 1:
                        reminder["duration"] = 10
                except (ValueError, TypeError):
                    reminder["duration"] = 10
        
        return reminders
    
    def save_reminders(self, reminders):
        """保存提醒列表"""
        # 确保持续时间是整数
        for reminder in reminders:
            if "duration" in reminder:
                try:
                    reminder["duration"] = int(reminder["duration"])
                    # 确保duration至少为1秒
                    if reminder["duration"] < 1:
                        reminder["duration"] = 10
                except (ValueError, TypeError):
                    reminder["duration"] = 10
        
        config = self.load_config()
        config["reminders"] = reminders
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
    
    # 如果需要添加测试提醒，取消下面的注释
    # test_reminder = {
    #     "time": "12:00",
    #     "message": "测试提醒",
    #     "duration": 15
    # }
    # reminders.append(test_reminder)
    # config_manager.save_reminders(reminders)
    # print("已添加测试提醒")
