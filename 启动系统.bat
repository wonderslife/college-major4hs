@echo off
chcp 65001 >nul
echo ========================================
echo    高考志愿填报系统 v2.0
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境！
    echo.
    echo 请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] 检查Python环境...
python --version
echo.

REM 检查依赖是否安装
echo [2/3] 检查依赖包...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包，请稍候...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
) else (
    echo 依赖包已安装 ✓
)
echo.

REM 启动系统
echo [3/3] 启动系统...
echo.
echo ========================================
echo 系统正在启动...
echo 启动成功后，浏览器将自动打开
echo 如果没有自动打开，请手动访问:
echo http://localhost:5000
echo ========================================
echo.
echo 按 Ctrl+C 可停止系统
echo.

python app_v2.py

pause
