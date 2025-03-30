import os
import sys
import logging

# 获取logger
logger = logging.getLogger("ClassScreenReminder.AutostartManager")

def get_autostart_status():
    """获取开机自启动状态"""
    if sys.platform == 'win32':
        try:
            import winreg
            # 打开注册表
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            # 尝试读取注册表值
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    value, _ = winreg.QueryValueEx(key, "ClassScreenReminder")
                    return True
            except FileNotFoundError:
                return False
        except Exception as e:
            logger.error(f"获取自启动状态出错: {e}")
    return False

def set_autostart(enable):
    """设置开机自启动"""
    if sys.platform == 'win32':
        try:
            import winreg
            # 获取应用程序路径
            app_path = f'"{sys.executable}"'
            if getattr(sys, 'frozen', False):
                # PyInstaller打包后的路径
                app_path = f'"{sys.executable}"'
            else:
                # 开发环境路径
                main_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "main.py")
                app_path = f'"{sys.executable}" "{main_script}"'
            
            # 打开注册表
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            if enable:
                # 添加到自启动
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "ClassScreenReminder", 0, winreg.REG_SZ, app_path)
                return True
            else:
                # 从自启动中移除
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, "ClassScreenReminder")
                    return True
                except FileNotFoundError:
                    pass  # 如果键不存在，则不需要删除
                return True
        except Exception as e:
            logger.error(f"设置自启动出错: {e}")
            return False
    return False
