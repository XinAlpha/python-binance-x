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
    print(f"策略参数: {config['strategy']['params']}")

    # 初始化数据获取器（不需要API密钥获取历史数据）
    print(f"\n正在获取历史数据...")
    network_config = config.get('network', {})
    proxy = network_config.get('proxy')
    timeout = network_config.get('timeout', 30)

    if proxy:
        print(f"  使用代理: {proxy}")

    data_fetcher = DataFetcher(
        proxy=proxy,
        timeout=timeout
    )

    # 获取历史数据
    df = data_fetcher.get_historical_klines(
        symbol=config['trading']['symbol'],
        interval=config['trading']['interval'],
        start_str=config['backtest']['start_date'],
        end_str=config['backtest']['end_date']
    )

    print(f"✓ 数据加载完成: {len(df)} 根K线")
    print(f"  时间范围: {df.index[0]} 至 {df.index[-1]}")

    # 根据配置动态加载策略
    print(f"\n正在初始化策略...")
    strategy_name = config['strategy']['name']

    # 策略映射
    strategy_map = {
        'ma_crossover': 'MACrossoverStrategy',
        'rsi': 'RSIStrategy',
        'bollinger_bands': 'BollingerBandsStrategy',
        'grid_trading': 'GridTradingStrategy',
        'macd': 'MACDStrategy',
        'breakout_pullback': 'BreakoutPullbackStrategy'
    }

    if strategy_name not in strategy_map:
        raise ValueError(f"未知策略: {strategy_name}. 可用策略: {list(strategy_map.keys())}")

    # 动态导入策略
    strategy_class_name = strategy_map[strategy_name]

    if strategy_name == 'ma_crossover':
        from strategies.ma_crossover_strategy import MACrossoverStrategy
        strategy = MACrossoverStrategy(config['strategy'])
    elif strategy_name == 'rsi':
        from strategies.rsi_strategy import RSIStrategy
        strategy = RSIStrategy(config['strategy'])
    elif strategy_name == 'bollinger_bands':
        from strategies.bollinger_bands_strategy import BollingerBandsStrategy
        strategy = BollingerBandsStrategy(config['strategy'])
    elif strategy_name == 'grid_trading':
        from strategies.grid_trading_strategy import GridTradingStrategy
        strategy = GridTradingStrategy(config['strategy'])
    elif strategy_name == 'macd':
        from strategies.macd_strategy import MACDStrategy
        strategy = MACDStrategy(config['strategy'])
    elif strategy_name == 'breakout_pullback':
        from strategies.breakout_pullback_strategy import BreakoutPullbackStrategy
        strategy = BreakoutPullbackStrategy(config['strategy'])

    print(f"✓ 策略初始化完成: {strategy_class_name}")

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
