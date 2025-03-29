import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_executable():
    """使用PyInstaller创建可执行文件"""
    print("开始构建exe文件...")
    
    # 确保资源文件夹存在
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # 检查声音文件是否存在
    sound_file = os.path.join(resources_dir, "attend_class.wav")
    if not os.path.exists(sound_file):
        print(f"警告: 声音文件不存在: {sound_file}")
        print("将创建一个空的声音文件，请在打包前替换为真实的声音文件")
        # 创建一个空的声音文件作为占位符
        with open(sound_file, 'wb') as f:
            f.write(b'')
    
    # 检查图标文件是否存在
    icon_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if not os.path.exists(icon_file):
        print(f"警告: 图标文件不存在: {icon_file}")
        print("打包将使用默认图标，如需自定义请添加icon.ico文件")
    
    # 构建命令
    pyinstaller_cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--name=ClassScreenReminder",
        "--windowed",  # 无控制台窗口
        "--add-data=resources;resources",  # 添加资源文件夹
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtMultimedia"
    ]
    
    # 如果图标存在，添加图标参数
    if os.path.exists(icon_file):
        pyinstaller_cmd.append(f"--icon={icon_file}")
        
    # 添加主脚本
    pyinstaller_cmd.append("main.py")
    
    # 运行PyInstaller
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("构建失败！")
        print("错误信息:")
        print(result.stderr)
        return False
    
    print("构建成功！")
    
    # 输出位置
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "ClassScreenReminder")
    print(f"可执行文件已生成: {os.path.join(dist_dir, 'ClassScreenReminder.exe')}")
    
    # 创建一个简单的启动器批处理文件，方便用户使用
    create_launcher(dist_dir)
    
    return True

def create_launcher(dist_dir):
    """创建一个简单的启动器批处理文件"""
    launcher_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "启动屏幕提醒工具.bat")
    
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('echo 正在启动屏幕提醒工具...\n')
        f.write('start "" "%~dp0ClassScreenReminder\\ClassScreenReminder.exe"\n')
        f.write('exit\n')
    
    print(f"已创建启动器: {launcher_path}")

if __name__ == "__main__":
    if create_executable():
        print("\n打包完成! 你可以将dist文件夹复制到其他设备使用")
        print("在目标设备上双击 '启动屏幕提醒工具.bat' 文件来运行应用程序")
