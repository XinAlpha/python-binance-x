#!/usr/bin/env python3
"""
环境检查脚本 - 检查所有依赖是否正确安装
"""
import sys
import subprocess

print("=" * 60)
print("环境检查工具".center(60))
print("=" * 60)
print()

# 检查Python版本
print("1. Python版本检查")
print("-" * 60)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

version_info = sys.version_info
if version_info.major >= 3 and version_info.minor >= 7:
    print("✓ Python版本符合要求 (>= 3.7)")
else:
    print("✗ Python版本过低，需要 >= 3.7")
    sys.exit(1)
print()

# 检查依赖包
print("2. 依赖包检查")
print("-" * 60)

required_packages = {
    'yaml': 'pyyaml',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'binance': 'python-binance'
}

missing_packages = []
installed_packages = []

for module_name, package_name in required_packages.items():
    try:
        if module_name == 'yaml':
            import yaml
        elif module_name == 'pandas':
            import pandas
        elif module_name == 'numpy':
            import numpy
        elif module_name == 'binance':
            from binance.client import Client

        print(f"✓ {package_name}")
        installed_packages.append(package_name)
    except ImportError:
        print(f"✗ {package_name} - 未安装")
        missing_packages.append(package_name)

print()

# 显示安装命令
if missing_packages:
    print("3. 缺少的依赖包")
    print("-" * 60)
    print("请运行以下命令安装缺少的包：")
    print()
    install_cmd = f"pip install {' '.join(missing_packages)}"
    print(f"  {install_cmd}")
    print()
    print("或者一键安装所有依赖：")
    print()
    print("  pip install -r requirements.txt")
    print()
    sys.exit(1)
else:
    print("3. 环境状态")
    print("-" * 60)
    print("✓ 所有依赖已安装，环境配置完成！")
    print()
    print("现在可以运行回测了：")
    print()
    print("  方法1（推荐）：python run_backtest.py")
    print("  方法2：python main.py backtest")
    print()

print("=" * 60)
print()
