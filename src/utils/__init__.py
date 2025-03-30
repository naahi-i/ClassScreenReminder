# 确保子模块能被正确导入
from . import sound_manager
from . import reminder_manager
from . import wallpaper_manager
from . import autostart_manager
from . import resource_manager
from . import card_manager

# 导出常用功能
from .sound_manager import play_initial_sound, initialize_sound
from .resource_manager import get_resource_path, resource_exists, create_default_resources, get_icon_path

__all__ = [
    'sound_manager',
    'reminder_manager',
    'wallpaper_manager',
    'autostart_manager',
    'resource_manager',
    'card_manager',
    'play_initial_sound',
    'initialize_sound',
    'get_resource_path',
    'resource_exists',
    'create_default_resources',
    'get_icon_path'
]
