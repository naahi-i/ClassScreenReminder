import os
import logging

# 获取logger
logger = logging.getLogger("ClassScreenReminder.ResourceManager")

# 应用根目录，将在初始化时设置
_app_root_dir = None
_resources_dir = None

def init_resource_paths(app_dir=None):
    """初始化资源路径"""
    global _app_root_dir, _resources_dir
    
    if app_dir is None:
        # 如果没有指定app_dir，尝试自动检测
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    _app_root_dir = app_dir
    _resources_dir = os.path.join(_app_root_dir, "resources")
    os.makedirs(_resources_dir, exist_ok=True)
    
    return _resources_dir

def get_app_root():
    """获取应用根目录路径"""
    global _app_root_dir
    if _app_root_dir is None:
        init_resource_paths()
    return _app_root_dir

def get_resources_dir():
    """获取资源目录路径"""
    global _resources_dir
    if _resources_dir is None:
        init_resource_paths()
    return _resources_dir

def get_resource_path(filename):
    """获取资源文件的完整路径"""
    resource_path = os.path.join(get_resources_dir(), filename)
    return resource_path

def resource_exists(filename):
    """检查资源文件是否存在"""
    resource_path = get_resource_path(filename)
    return os.path.exists(resource_path)

def get_icon_path():
    """获取应用图标路径"""
    icon_path = os.path.join(get_app_root(), "icon.ico")
    if os.path.exists(icon_path):
        return icon_path
    return None

def create_default_resources():
    """创建默认资源目录和必要的默认文件"""
    resources_dir = get_resources_dir()
    
    # 检查声音文件是否存在
    sound_file = os.path.join(resources_dir, "attend_class.wav")
    if not os.path.exists(sound_file):
        # 记录日志
        logger.warning(f"声音文件未找到: {sound_file}")
        
        # 创建一个提示文件，告知用户需要添加声音文件
        readme_file = os.path.join(resources_dir, "README.txt")
        if not os.path.exists(readme_file):
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write("请在此目录放置名为 'attend_class.wav' 的声音文件，作为提醒声音。\n")
                f.write("可以使用任何WAV格式的短音效。\n")
    
    return resources_dir
