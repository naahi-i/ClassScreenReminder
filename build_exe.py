import os
import sys
import shutil
import subprocess

def ensure_requirements():
    """确保所有必要的包都已安装"""
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    try:
        import PySide6
    except ImportError:
        print("错误: 缺少PySide6包。请先安装: pip install PySide6")
        sys.exit(1)
        
    try:
        import win32api
    except ImportError:
        print("正在安装pywin32...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])

def build_executable():
    """打包应用为文件夹"""
    print("开始打包ClassScreenReminder为可执行程序...")
    
    # 获取当前目录(应用根目录)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 清理之前的构建文件
    dist_dir = os.path.join(app_dir, "dist")
    build_dir = os.path.join(app_dir, "build")
    
    if os.path.exists(dist_dir):
        print("清理dist目录...")
        shutil.rmtree(dist_dir)
    
    if os.path.exists(build_dir):
        print("清理build目录...")
        shutil.rmtree(build_dir)
    
    # 创建包含额外文件的spec文件
    icon_path = os.path.join(app_dir, "icon.ico")
    resources_dir = os.path.join(app_dir, "resources")
    
    # 准备额外的数据文件
    datas = [
        (icon_path, '.'),
        (resources_dir, 'resources')
    ]
    
    # 构建PyInstaller命令 - 移除--onefile选项
    cmd = [
        "pyinstaller",
        "--name=ClassScreenReminder",
        "--windowed",
        f"--icon={icon_path}",
        "--clean",
        "--noconfirm"
    ]
    
    # 添加数据文件
    for src, dst in datas:
        if os.path.exists(src):
            cmd.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # 添加主脚本
    cmd.append(os.path.join(app_dir, "main.py"))
    
    # 执行打包命令
    print("正在执行PyInstaller...")
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    
if __name__ == "__main__":
    ensure_requirements()
    build_executable()
    
    input("\n按Enter键退出...")
