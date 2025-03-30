import os
import logging
from PySide6.QtCore import QObject

logger = logging.getLogger("ClassScreenReminder.WallpaperManager")

class WallpaperManager(QObject):
    """壁纸管理器，负责不同区域壁纸的管理与保存"""
    
    # 壁纸区域常量
    AREA_MAIN = "main"       # 中间区域 (B 色块)
    AREA_LEFT = "left"       # 左侧区域 (A 色块)
    AREA_TOP = "top"         # 上侧区域
    AREA_ACCENT = "accent"   # 装饰条区域
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.wallpapers = self._load_wallpapers()
    
    def _load_wallpapers(self):
        """从配置中加载壁纸设置"""
        wallpapers = self.config_manager.get_setting("wallpapers", {})
        return wallpapers
    
    def get_wallpaper(self, area=AREA_MAIN):
        """获取指定区域的壁纸路径"""
        path = self.wallpapers.get(area, "")
        # 验证文件是否存在
        if path and not os.path.exists(path):
            logger.warning(f"壁纸文件不存在: {path}")
            path = ""
            self.wallpapers[area] = ""
        return path
    
    def set_wallpaper(self, area, path):
        """设置指定区域的壁纸"""
        if not path or os.path.exists(path):
            self.wallpapers[area] = path
            self._save_wallpapers()
            return True
        return False
    
    def clear_wallpaper(self, area=None):
        """清除指定区域或所有壁纸"""
        if area is None:
            # 清除所有壁纸
            self.wallpapers = {}
        elif area in self.wallpapers:
            # 清除指定区域的壁纸
            del self.wallpapers[area]
        self._save_wallpapers()
    
    def get_all_wallpapers(self):
        """获取所有壁纸设置"""
        return self.wallpapers.copy()
    
    def _save_wallpapers(self):
        """保存壁纸设置到配置"""
        self.config_manager.set_setting("wallpapers", self.wallpapers)
