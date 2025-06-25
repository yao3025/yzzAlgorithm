import os
import sys
import subprocess
import shutil
from tkinter import Tk, filedialog

# 隐藏主窗口
root = Tk()
root.withdraw()

# 选择输出安装目录
install_dir = filedialog.askdirectory(title="选择打包后 .exe 的安装目录")
if not install_dir:
    print("未选择安装目录，退出。")
    sys.exit(1)

# 计算脚本所在目录（AlgorithmManager/dev）和项目根目录
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

# 算法子目录列表（项目根目录下，以数字+下划线开头的文件夹）
alg_dirs = [d for d in os.listdir(project_root)
            if os.path.isdir(os.path.join(project_root, d)) and d[0].isdigit() and "_" in d]

# PyInstaller 打包命令参数
icon_path = os.path.join(script_dir, 'img', 'icon.png')
main_script = os.path.join(script_dir, 'main.py')

# 构建 --add-data 参数，将算法目录和 icon 包含进 exe
datas = []
# 添加 icon
if os.path.exists(icon_path):
    datas.append(f"{icon_path};img")

# PyInstaller 基本命令
cmd = [
    'pyinstaller',
    '--onefile',
    '--windowed',
    '--name', 'AlgorithmManager',
]
# 添加图标
if os.path.exists(icon_path):
    cmd += ['--icon', icon_path]
# 最后添加入口脚本
cmd.append(main_script)

print('执行打包命令:', ' '.join(cmd))
result = subprocess.run(cmd)
if result.returncode != 0:
    print('打包失败')
    sys.exit(1)

# 打包结果在 dist/AlgorithmManager.exe
dist_dir = os.path.join(script_dir, 'dist')
src_exe = os.path.join(dist_dir, 'AlgorithmManager.exe')
if os.path.exists(src_exe):
    dst_exe = os.path.join(install_dir, 'AlgorithmManager.exe')
    shutil.copy2(src_exe, dst_exe)
    print(f'打包完成，安装文件复制到 {dst_exe}')
else:
    print('未找到生成的 exe 文件')

# 清理 PyInstaller 生成的临时文件
for name in ['build', 'dist', '__pycache__', 'AlgorithmManager.spec']:
    p = os.path.join(script_dir, name)
    if os.path.isdir(p):
        shutil.rmtree(p)
    elif os.path.isfile(p):
        os.remove(p)

print('打包流程完成。') 