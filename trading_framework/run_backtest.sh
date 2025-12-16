#!/bin/bash
# Linux/Mac Shell脚本 - 一键运行回测

echo "========================================"
echo "  币安合约交易框架 - 自动回测"
echo "========================================"
echo ""

# 检查Python
echo "[1/3] 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "✗ Python未安装"
    echo "请安装Python 3.7或更高版本"
    exit 1
fi

echo "✓ Python环境正常 ($($PYTHON_CMD --version))"
echo ""

# 安装依赖
echo "[2/3] 安装依赖包..."
echo "正在安装: python-binance pandas numpy pyyaml"
$PYTHON_CMD -m pip install python-binance pandas numpy pyyaml -q --disable-pip-version-check

if [ $? -eq 0 ]; then
    echo "✓ 依赖安装完成"
else
    echo "✗ 依赖安装失败"
    exit 1
fi
echo ""

# 运行回测
echo "[3/3] 开始回测..."
echo ""
$PYTHON_CMD run_backtest.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  回测完成！"
    echo "========================================"
else
    echo ""
    echo "✗ 回测执行失败"
    echo "请检查错误信息"
    exit 1
fi
