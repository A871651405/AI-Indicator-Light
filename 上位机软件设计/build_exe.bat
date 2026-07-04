@echo off
chcp 65001 > nul
echo ================================================
echo       打包 AI指示灯控制器 为 EXE
echo ================================================
echo.

echo [信息] 正在打包，请稍候...
echo.

pyinstaller --noconfirm --onefile --windowed --name "AI指示灯控制器" --collect-all serial --collect-all flask main.py

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
echo 可执行文件位置: dist\AI指示灯控制器.exe
echo.
echo 注意: dist文件夹外的文件是中间产物，可以删除
echo       - build文件夹 (可删除)
echo       - AI指示灯控制器.spec (可删除)
echo.
pause
