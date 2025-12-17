#!/usr/bin/env python3
"""
测试所有策略 - 验证策略是否正常工作
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("策略测试工具".center(60))
print("=" * 60)
print()

# 测试导入
print("1. 测试策略导入...")
print("-" * 60)

strategies_info = [
    ("均线交叉策略", "MACrossoverStrategy"),
    ("RSI超买超卖策略", "RSIStrategy"),
    ("布林带突破策略", "BollingerBandsStrategy"),
    ("网格交易策略", "GridTradingStrategy"),
    ("MACD趋势策略", "MACDStrategy"),
    ("突破回踩策略", "BreakoutPullbackStrategy"),
]

imported_strategies = {}
failed_imports = []

for name_cn, class_name in strategies_info:
    try:
        if class_name == "MACrossoverStrategy":
            from strategies.ma_crossover_strategy import MACrossoverStrategy
            imported_strategies[name_cn] = MACrossoverStrategy
        elif class_name == "RSIStrategy":
            from strategies.rsi_strategy import RSIStrategy
            imported_strategies[name_cn] = RSIStrategy
        elif class_name == "BollingerBandsStrategy":
            from strategies.bollinger_bands_strategy import BollingerBandsStrategy
            imported_strategies[name_cn] = BollingerBandsStrategy
        elif class_name == "GridTradingStrategy":
            from strategies.grid_trading_strategy import GridTradingStrategy
            imported_strategies[name_cn] = GridTradingStrategy
        elif class_name == "MACDStrategy":
            from strategies.macd_strategy import MACDStrategy
            imported_strategies[name_cn] = MACDStrategy
        elif class_name == "BreakoutPullbackStrategy":
            from strategies.breakout_pullback_strategy import BreakoutPullbackStrategy
            imported_strategies[name_cn] = BreakoutPullbackStrategy

        print(f"✓ {name_cn} ({class_name})")
    except Exception as e:
        print(f"✗ {name_cn} - 导入失败: {e}")
        failed_imports.append(name_cn)

print()

# 测试策略初始化
print("2. 测试策略初始化...")
print("-" * 60)

test_configs = {
    "均线交叉策略": {
        "name": "ma_crossover",
        "params": {"ma_short": 10, "ma_long": 30, "stop_loss": 0.02, "take_profit": 0.04}
    },
    "RSI超买超卖策略": {
        "name": "rsi",
        "params": {"rsi_period": 14, "oversold": 30, "overbought": 70}
    },
    "布林带突破策略": {
        "name": "bollinger_bands",
        "params": {"bb_period": 20, "bb_std": 2.0, "mode": "mean_reversion"}
    },
    "网格交易策略": {
        "name": "grid_trading",
        "params": {"grid_num": 10, "price_range": 0.2}
    },
    "MACD趋势策略": {
        "name": "macd",
        "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}
    },
    "突破回踩策略": {
        "name": "breakout_pullback",
        "params": {"lookback_period": 20, "pullback_ratio": 0.5}
    }
}

initialized_strategies = {}
failed_inits = []

for name_cn, strategy_class in imported_strategies.items():
    try:
        config = test_configs[name_cn]
        strategy = strategy_class(config)
        initialized_strategies[name_cn] = strategy
        print(f"✓ {name_cn} - 初始化成功")
    except Exception as e:
        print(f"✗ {name_cn} - 初始化失败: {e}")
        failed_inits.append(name_cn)

print()

# 总结
print("=" * 60)
print("测试总结".center(60))
print("=" * 60)
print()

total_strategies = len(strategies_info)
success_imports = len(imported_strategies)
success_inits = len(initialized_strategies)

print(f"策略总数:         {total_strategies}")
print(f"导入成功:         {success_imports}")
print(f"初始化成功:       {success_inits}")
print()

if failed_imports:
    print("导入失败的策略:")
    for name in failed_imports:
        print(f"  ✗ {name}")
    print()

if failed_inits:
    print("初始化失败的策略:")
    for name in failed_inits:
        print(f"  ✗ {name}")
    print()

if success_inits == total_strategies:
    print("✓ 所有策略测试通过！")
    print()
    print("可用的策略:")
    for name in initialized_strategies.keys():
        print(f"  • {name}")
    print()
    print("下一步:")
    print("  1. 在 config/config.yaml 中选择策略")
    print("  2. 配置策略参数")
    print("  3. 运行回测: python run_backtest.py")
else:
    print(f"⚠ 有 {total_strategies - success_inits} 个策略测试失败")
    print("请检查错误信息并修复")

print()
print("=" * 60)
