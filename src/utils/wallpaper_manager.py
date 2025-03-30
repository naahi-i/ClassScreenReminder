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
        self.opacities = self._load_opacities()
    
    def _load_wallpapers(self):
        """从配置中加载壁纸设置"""
        wallpapers = self.config_manager.get_setting("wallpapers", {})
        return wallpapers
    
    def _load_opacities(self):
        """从配置中加载壁纸透明度设置"""
        opacities = self.config_manager.get_setting("wallpaper_opacities", {})
        
        # 为所有区域设置默认透明度（如果不存在）
        default_opacity = 70  # 默认透明度为70%
        for area in [self.AREA_MAIN, self.AREA_LEFT, self.AREA_TOP, self.AREA_ACCENT]:
            if area not in opacities:
                opacities[area] = default_opacity
        
        return opacities
    
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
    
    def get_wallpaper_opacity(self, area=AREA_MAIN):
        """获取指定区域的壁纸遮罩透明度（0-100）"""
        # 返回透明度百分比，100表示完全不透明，0表示完全透明
        # 注意：实际使用时为遮罩透明度，所以这里是遮罩的不透明度
        return self.opacities.get(area, 70)  # 默认返回70%的不透明度
    
    def set_wallpaper_opacity(self, area, opacity):
        """设置指定区域的壁纸遮罩透明度（0-100）"""
        # 确保透明度在有效范围内
        opacity = max(0, min(100, int(opacity)))
        self.opacities[area] = opacity
        self._save_opacities()
        return True
    
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
        """获取所有壁纸设置，包括透明度"""
        result = self.wallpapers.copy()
        
        # 添加透明度信息 - 作为遮罩的不透明度
        # 创建一个新的字典来存储区域和透明度信息，避免在迭代过程中修改字典
        opacity_info = {}
        for area in result:
            # 只为有壁纸的区域添加透明度属性
            if result[area] and os.path.exists(result[area]):  # 确保路径不为空且文件存在
                # 转换为0-1范围的不透明度值
                opacity = self.get_wallpaper_opacity(area) / 100.0
                opacity_info[f"{area}_opacity"] = opacity
        
        # 将透明度信息更新到结果字典中
        result.update(opacity_info)
        
        return result
    
    def _save_wallpapers(self):
        """保存壁纸设置到配置"""
        self.config_manager.set_setting("wallpapers", self.wallpapers)
    
    def _save_opacities(self):
        """保存壁纸透明度设置到配置"""
        self.config_manager.set_setting("wallpaper_opacities", self.opacities)
