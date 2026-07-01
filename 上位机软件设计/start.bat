@echo off
chcp 65001 > nul
echo ================================================
echo          AI指示灯控制器 - 启动程序
echo ================================================
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [信息] 检查依赖包...
python -c "import serial, flask" > nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [成功] 依赖包安装完成
)

echo.
echo [信息] 正在启动AI指示灯控制器...
echo.
python main.py

pause
