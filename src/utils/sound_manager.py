import os
import time
import logging
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

# 获取logger
logger = logging.getLogger("ClassScreenReminder.SoundManager")

# 全局声音变量
_global_sound = None
_sound_is_initialized = False
_last_play_time = 0
_is_second_sound_playing = False

def initialize_sound():
    """初始化全局声音对象"""
    global _global_sound, _sound_is_initialized
    
    if _sound_is_initialized:
        return True
    
    try:
        # 修正声音文件路径 - 现在需要向上两级目录才能找到resources目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)  # src目录
        root_dir = os.path.dirname(parent_dir)     # 项目根目录
        
        sound_path = os.path.join(root_dir, "resources", "attend_class.wav")
        
        # 添加日志输出，帮助诊断问题
        logger.info(f"尝试加载声音文件: {sound_path}")
        
        # 检查文件是否存在
        if os.path.exists(sound_path):
            sound_effect = QSoundEffect()
            sound_effect.setSource(QUrl.fromLocalFile(sound_path))
            sound_effect.setVolume(1.0)
            sound_effect.setLoopCount(0)
            
            _global_sound = sound_effect
            _sound_is_initialized = True
            logger.info("声音文件加载成功")
            return True
        else:
            logger.warning(f"找不到声音文件: {sound_path}")
            
            # 尝试其他可能的路径
            alternative_paths = [
                os.path.join(root_dir, "resources", "attend_class.wav"),
                os.path.join(parent_dir, "resources", "attend_class.wav"),
                os.path.join(current_dir, "resources", "attend_class.wav")
            ]
            
            for path in alternative_paths:
                logger.info(f"尝试替代路径: {path}")
                if os.path.exists(path):
                    sound_effect = QSoundEffect()
                    sound_effect.setSource(QUrl.fromLocalFile(path))
                    sound_effect.setVolume(1.0)
                    sound_effect.setLoopCount(0)
                    
                    _global_sound = sound_effect
                    _sound_is_initialized = True
                    logger.info(f"在替代路径找到声音文件: {path}")
                    return True
            
            return False
    except Exception as e:
        logger.error(f"初始化声音时出错：{e}")
        return False

def play_initial_sound():
    """播放提醒声音组合"""
    global _global_sound, _last_play_time, _is_second_sound_playing
    
    # 如果声音没有初始化，先初始化
    if not _sound_is_initialized and not initialize_sound():
        return False
    
    # 检查是否太频繁播放
    current_time = time.time()
    if current_time - _last_play_time < 1.0 and not _is_second_sound_playing:
        return False
    
    try:
        if not _global_sound or not _global_sound.isLoaded():
            return False
            
        # 记录播放时间
        _last_play_time = current_time
        
        # 确保没有正在播放的声音
        if _global_sound.isPlaying() and not _is_second_sound_playing:
            _global_sound.stop()
        
        # 播放第一次声音
        _global_sound.play()
        
        # 设置标志，表示接下来将播放第二个声音
        _is_second_sound_playing = True
        
        # 延迟播放第二次声音
        QTimer.singleShot(300, play_second_sound)
        
        return True
    except Exception as e:
        logger.error(f"播放初始声音时出错：{e}")
        _is_second_sound_playing = False
        return False

def play_second_sound():
    """播放第二次声音"""
    global _global_sound, _is_second_sound_playing
    try:
        if _global_sound and _global_sound.isLoaded():
            _global_sound.play()
        _is_second_sound_playing = False
    except Exception as e:
        logger.debug(f"播放第二次声音时出错：{e}")
        _is_second_sound_playing = False