#!/usr/bin/env python3
"""
简化的回测运行脚本
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    print("正在导入模块...")
    import yaml
    import pandas as pd
    from binance.client import Client
    from utils.data_fetcher import DataFetcher
    from utils.logger import setup_logger
    from strategies.ma_crossover_strategy import MACrossoverStrategy
    from backtest.backtest_engine import BacktestEngine

    print("✓ 所有模块导入成功")

    # 加载配置
    print("\n正在加载配置...")
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✓ 配置加载成功")

    # 设置日志
    logger = setup_logger(
        level=config['logging']['level'],
        log_file=config['logging'].get('file'),
        console=config['logging'].get('console', True)
    )

    print("\n" + "=" * 60)
    print("开始回测".center(60))
    print("=" * 60)

    # 显示配置信息
    print(f"\n交易对: {config['trading']['symbol']}")
    print(f"K线周期: {config['trading']['interval']}")
    print(f"初始资金: ${config['trading']['initial_capital']:,.0f}")
    print(f"回测时间: {config['backtest']['start_date']} 至 {config['backtest']['end_date']}")
    print(f"策略: {config['strategy']['name']}")
    print(f"短期均线: {config['strategy']['params']['ma_short']}")
    print(f"长期均线: {config['strategy']['params']['ma_long']}")

    # 初始化数据获取器（不需要API密钥获取历史数据）
    print(f"\n正在获取历史数据...")
    data_fetcher = DataFetcher()

    # 获取历史数据
    df = data_fetcher.get_historical_klines(
        symbol=config['trading']['symbol'],
        interval=config['trading']['interval'],
        start_str=config['backtest']['start_date'],
        end_str=config['backtest']['end_date']
    )

    print(f"✓ 数据加载完成: {len(df)} 根K线")
    print(f"  时间范围: {df.index[0]} 至 {df.index[-1]}")

    # 初始化策略
    print(f"\n正在初始化策略...")
    strategy = MACrossoverStrategy(config['strategy'])
    print("✓ 策略初始化完成")

    # 初始化回测引擎
    print(f"\n正在运行回测...")
    backtest_engine = BacktestEngine(strategy, config)

    # 运行回测
    results = backtest_engine.run(df)

    # 打印结果
    backtest_engine.print_results(results)

    print("\n✓ 回测完成！")

except ImportError as e:
    print(f"\n✗ 导入错误: {e}")
    print("\n请安装缺少的依赖:")
    print("  pip install python-binance pandas numpy pyyaml")
    sys.exit(1)

except FileNotFoundError as e:
    print(f"\n✗ 文件未找到: {e}")
    print("\n请确保在 trading_framework 目录下运行此脚本")
    sys.exit(1)

except Exception as e:
    print(f"\n✗ 发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
