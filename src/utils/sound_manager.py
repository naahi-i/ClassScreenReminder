import os
import time
import logging
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput

# 获取logger
logger = logging.getLogger("ClassScreenReminder.SoundManager")

# 全局声音变量
_global_sound = None
_media_player = None  # 用于播放非WAV格式的音频
_audio_output = None  # 音频输出设备
_sound_is_initialized = False
_last_play_time = 0
_is_second_sound_playing = False
_current_audio_path = ""  # 存储当前使用的音频文件路径
_is_wav_format = True     # 当前是否为WAV格式

# 支持的音频格式
SUPPORTED_FORMATS = {
    "wav": "Wave音频文件 (*.wav)",
    "mp3": "MP3音频文件 (*.mp3)",
    "ogg": "Ogg Vorbis音频文件 (*.ogg)",
    "m4a": "MPEG-4音频文件 (*.m4a)",
    "aac": "AAC音频文件 (*.aac)",
    "flac": "FLAC音频文件 (*.flac)"
}

def initialize_sound():
    """初始化全局声音对象"""
    global _global_sound, _media_player, _audio_output, _sound_is_initialized, _current_audio_path, _is_wav_format
    
    if _sound_is_initialized:
        return True
    
    try:
        # 修正声音文件路径 - 现在需要向上两级目录才能找到resources目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)  # src目录
        root_dir = os.path.dirname(parent_dir)     # 项目根目录
        
        # 尝试从配置中加载自定义音频
        try:
            from ..config_manager import ConfigManager
            config = ConfigManager()
            custom_audio = config.get_setting("custom_audio_path", "")
            if custom_audio and os.path.exists(custom_audio):
                sound_path = custom_audio
                _current_audio_path = custom_audio
                logger.info(f"使用自定义音频: {sound_path}")
            else:
                sound_path = os.path.join(root_dir, "resources", "attend_class.wav")
                _current_audio_path = sound_path
                logger.info(f"使用默认音频: {sound_path}")
        except Exception as e:
            logger.error(f"加载配置时出错: {e}")
            sound_path = os.path.join(root_dir, "resources", "attend_class.wav")
            _current_audio_path = sound_path
        
        # 添加日志输出，帮助诊断问题
        logger.info(f"尝试加载声音文件: {sound_path}")
        
        # 检查文件是否存在
        if os.path.exists(sound_path):
            # 检查文件扩展名
            file_ext = os.path.splitext(sound_path)[1].lower()
            
            if file_ext == '.wav':
                # WAV格式使用QSoundEffect
                _is_wav_format = True
                sound_effect = QSoundEffect()
                sound_effect.setSource(QUrl.fromLocalFile(sound_path))
                sound_effect.setVolume(1.0)
                sound_effect.setLoopCount(0)
                
                _global_sound = sound_effect
                _sound_is_initialized = True
                logger.info("WAV格式声音文件加载成功")
            else:
                # 非WAV格式使用QMediaPlayer
                _is_wav_format = False
                _audio_output = QAudioOutput()
                _audio_output.setVolume(1.0)
                
                _media_player = QMediaPlayer()
                _media_player.setAudioOutput(_audio_output)
                _media_player.setSource(QUrl.fromLocalFile(sound_path))
                
                _sound_is_initialized = True
                logger.info(f"{file_ext}格式声音文件加载成功")
            
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
                    # WAV格式使用QSoundEffect
                    _is_wav_format = True
                    sound_effect = QSoundEffect()
                    sound_effect.setSource(QUrl.fromLocalFile(path))
                    sound_effect.setVolume(1.0)
                    sound_effect.setLoopCount(0)
                    
                    _global_sound = sound_effect
                    _sound_is_initialized = True
                    _current_audio_path = path
                    logger.info(f"在替代路径找到声音文件: {path}")
                    return True
            
            return False
    except Exception as e:
        logger.error(f"初始化声音时出错：{e}")
        return False

def play_initial_sound():
    """播放提醒声音组合"""
    global _global_sound, _media_player, _last_play_time, _is_second_sound_playing, _is_wav_format
    
    # 如果声音没有初始化，先初始化
    if not _sound_is_initialized and not initialize_sound():
        return False
    
    # 检查是否太频繁播放
    current_time = time.time()
    if current_time - _last_play_time < 1.0 and not _is_second_sound_playing:
        return False
    
    try:
        # 记录播放时间
        _last_play_time = current_time
        
        if _is_wav_format:
            # WAV格式使用QSoundEffect
            if not _global_sound or not _global_sound.isLoaded():
                return False
                
            # 确保没有正在播放的声音
            if _global_sound.isPlaying() and not _is_second_sound_playing:
                _global_sound.stop()
            
            # 播放第一次声音
            _global_sound.play()
            
            # 设置标志，表示接下来将播放第二个声音
            _is_second_sound_playing = True
            
            # 延迟播放第二次声音
            QTimer.singleShot(300, play_second_sound)
        else:
            # 非WAV格式使用QMediaPlayer
            if not _media_player:
                return False
            
            # 确保重新开始播放
            _media_player.stop()
            _media_player.play()
        
        return True
    except Exception as e:
        logger.error(f"播放初始声音时出错：{e}")
        _is_second_sound_playing = False
        return False

def play_second_sound():
    """播放第二次声音（仅WAV格式）"""
    global _global_sound, _is_second_sound_playing, _is_wav_format
    
    if not _is_wav_format:
        _is_second_sound_playing = False
        return
        
    try:
        if _global_sound and _global_sound.isLoaded():
            _global_sound.play()
        _is_second_sound_playing = False
    except Exception as e:
        logger.debug(f"播放第二次声音时出错：{e}")
        _is_second_sound_playing = False

def set_custom_audio(audio_path):
    """设置自定义音频文件"""
    global _global_sound, _media_player, _audio_output, _sound_is_initialized, _current_audio_path, _is_wav_format
    
    if not audio_path or not os.path.exists(audio_path):
        logger.error(f"音频文件不存在: {audio_path}")
        return False
    
    try:
        # 检查文件扩展名
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        if file_ext == '.wav':
            # WAV格式使用QSoundEffect
            sound_effect = QSoundEffect()
            sound_effect.setSource(QUrl.fromLocalFile(audio_path))
            sound_effect.setVolume(1.0)
            sound_effect.setLoopCount(0)
            
            # 如果加载成功，替换全局对象
            if sound_effect.isLoaded() or sound_effect.status() == QSoundEffect.Loading:
                # 停止并清理旧的播放器
                if _is_wav_format and _global_sound:
                    if _global_sound.isPlaying():
                        _global_sound.stop()
                elif not _is_wav_format and _media_player:
                    _media_player.stop()
                
                _global_sound = sound_effect
                _is_wav_format = True
                _sound_is_initialized = True
                _current_audio_path = audio_path
            else:
                logger.error(f"无法加载WAV音频文件: {audio_path}")
                return False
        else:
            # 非WAV格式使用QMediaPlayer
            if _media_player is None:
                _audio_output = QAudioOutput()
                _media_player = QMediaPlayer()
                _media_player.setAudioOutput(_audio_output)
            
            # 停止并清理旧的播放器
            if _is_wav_format and _global_sound:
                if _global_sound.isPlaying():
                    _global_sound.stop()
            elif not _is_wav_format and _media_player:
                _media_player.stop()
            
            _audio_output.setVolume(1.0)
            _media_player.setSource(QUrl.fromLocalFile(audio_path))
            
            _is_wav_format = False
            _sound_is_initialized = True
            _current_audio_path = audio_path
        
        # 保存到配置
        try:
            from ..config_manager import ConfigManager
            config = ConfigManager()
            config.set_setting("custom_audio_path", audio_path)
        except Exception as e:
            logger.error(f"保存配置时出错: {e}")
        
        logger.info(f"成功设置自定义音频: {audio_path}")
        return True
    except Exception as e:
        logger.error(f"设置自定义音频时出错: {e}")
        return False

def reset_to_default_audio():
    """重置为默认音频"""
    global _global_sound, _media_player, _sound_is_initialized, _current_audio_path, _is_wav_format
    
    try:
        # 获取默认音频路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)  # src目录
        root_dir = os.path.dirname(parent_dir)     # 项目根目录
        default_audio_path = os.path.join(root_dir, "resources", "attend_class.wav")
        
        if not os.path.exists(default_audio_path):
            logger.error(f"默认音频文件不存在: {default_audio_path}")
            return False
        
        # 创建新的声音效果对象
        sound_effect = QSoundEffect()
        sound_effect.setSource(QUrl.fromLocalFile(default_audio_path))
        sound_effect.setVolume(1.0)
        sound_effect.setLoopCount(0)
        
        # 如果加载成功，替换全局对象
        if sound_effect.isLoaded() or sound_effect.status() == QSoundEffect.Loading:
            # 停止并清理旧的播放器
            if _is_wav_format and _global_sound:
                if _global_sound.isPlaying():
                    _global_sound.stop()
            elif not _is_wav_format and _media_player:
                _media_player.stop()
            
            _global_sound = sound_effect
            _is_wav_format = True
            _sound_is_initialized = True
            _current_audio_path = default_audio_path
            
            # 清除配置中的自定义音频
            try:
                from ..config_manager import ConfigManager
                config = ConfigManager()
                config.set_setting("custom_audio_path", "")
            except Exception as e:
                logger.error(f"保存配置时出错: {e}")
            
            logger.info(f"已重置为默认音频: {default_audio_path}")
            return True
        else:
            logger.error(f"无法加载默认音频文件: {default_audio_path}")
            return False
    except Exception as e:
        logger.error(f"重置默认音频时出错: {e}")
        return False

def get_current_audio_path():
    """获取当前使用的音频文件路径"""
    global _current_audio_path
    return _current_audio_path

def get_current_audio_format():
    """获取当前音频文件格式"""
    global _current_audio_path, _is_wav_format
    
    if not _current_audio_path:
        return "wav"  # 默认格式
        
    file_ext = os.path.splitext(_current_audio_path)[1].lower().replace('.', '')
    return file_ext if file_ext else "wav"

def get_supported_formats():
    """获取支持的音频格式列表"""
    return SUPPORTED_FORMATS