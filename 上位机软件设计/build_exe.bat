@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ================================================
echo       打包 AI指示灯控制器 为 EXE
echo ================================================
echo.

:: 使用 venv 中的 Python（PyQt5 和所有依赖都在这里）
set VENV_PYTHON="C:/Users/87165/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
set VENV_PYINSTALLER="C:/Users/87165/.workbuddy/binaries/python/envs/default/Scripts/pyinstaller.exe"

echo [信息] 检查打包环境...
%VENV_PYTHON% -c "import PyQt5; import serial; import flask" 2>nul
if errorlevel 1 (
    echo [错误] 缺少依赖！请先安装 PyQt5、pyserial、flask
    pause
    exit /b 1
)
echo [信息] 依赖检查通过

:: 切换到脚本所在目录
cd /d "%~dp0"

echo [信息] 正在打包，请稍候（可能需要 2-3 分钟）...
echo.

%VENV_PYINSTALLER% ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "AI指示灯控制器" ^
    --collect-all PyQt5 ^
    --collect-all serial ^
    --collect-all flask ^
    --hidden-import serial ^
    --hidden-import serial.tools.list_ports ^
    --hidden-import flask ^
    --hidden-import pyserial ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo.
    pause
    exit /b 1
)

echo.
echo [成功] 打包完成！
echo.
echo 可执行文件: dist\AI指示灯控制器.exe
echo.
echo 注意: dist文件夹外的文件是中间产物，可以删除
echo       - build\  (可删除)
echo       - AI指示灯控制器.spec  (可删除)
echo.

:: 拷贝图标文件到 dist 目录（供 exe 运行时调用）
if exist app_icon.png (
    copy /Y app_icon.png dist\ > nul
    echo [信息] 已复制 app_icon.png 到 dist 目录
)
if exist app_icon.ico (
    copy /Y app_icon.ico dist\ > nul
    echo [信息] 已复制 app_icon.ico 到 dist 目录
)

echo.
pause
