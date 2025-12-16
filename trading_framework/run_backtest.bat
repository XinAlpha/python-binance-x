@echo off
REM Windows批处理脚本 - 一键运行回测
echo ========================================
echo  币安合约交易框架 - 自动回测
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python未安装或未添加到PATH
    echo 请安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo √ Python环境正常
echo.

echo [2/3] 安装依赖包...
echo 正在安装: python-binance pandas numpy pyyaml
python -m pip install python-binance pandas numpy pyyaml -q --disable-pip-version-check
if errorlevel 1 (
    echo X 依赖安装失败
    pause
    exit /b 1
)
echo √ 依赖安装完成
echo.

echo [3/3] 开始回测...
echo.
python run_backtest.py
echo.

if errorlevel 1 (
    echo.
    echo X 回测执行失败
    echo 请检查错误信息
) else (
    echo.
    echo ========================================
    echo  回测完成！
    echo ========================================
)

echo.
pause
