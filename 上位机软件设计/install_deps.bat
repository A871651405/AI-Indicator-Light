@echo off
chcp 65001 > nul
echo ================================================
echo       安装AI指示灯控制器依赖包
echo ================================================
echo.

echo [信息] 正在安装依赖包...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [错误] 依赖包安装失败！
    echo 请检查网络连接或手动运行: pip install -r requirements.txt
) else (
    echo.
    echo [成功] 依赖包安装完成！
    echo.
    echo 现在可以运行 start.bat 启动软件
)

echo.
pause
