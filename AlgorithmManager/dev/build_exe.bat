@echo off
REM 打包算法管理程序为可执行文件
pyinstaller --onefile --name AlgorithmManager main.py

REM 创建上级 dist 目录（如果不存在）
if not exist "..\dist" mkdir "..\dist"

REM 复制可执行文件到项目 dist
copy "dist\AlgorithmManager.exe" "..\dist\AlgorithmManager.exe"

echo 打包完成，可执行文件位于 AlgorithmManager/dist 目录
pause 