#!/usr/bin/env python3
"""
回测演示脚本 - 展示回测结果的示例输出
用于在无法连接API时演示框架功能
"""
import time
import random

print("\n" + "=" * 60)
print("回测演示模式".center(60))
print("=" * 60)
print()

print("注意：这是演示输出，展示回测功能的效果")
print("实际运行时会使用真实的市场数据")
print()

time.sleep(1)

# 模拟配置信息
print("配置信息：")
print("-" * 60)
print("交易对: BTCUSDT")
print("K线周期: 1h")
print("初始资金: $10,000")
print("回测时间: 2024-01-01 至 2024-12-01")
print("策略: 均线交叉策略")
print("短期均线: 10")
print("长期均线: 30")
print("止损: 2%")
print("止盈: 4%")
print()

time.sleep(1)

# 模拟数据获取
print("正在获取历史数据...")
for i in range(3):
    time.sleep(0.5)
    print(f"  下载进度: {(i+1)*33}%")

print("✓ 数据加载完成: 7920 根K线")
print("  时间范围: 2024-01-01 00:00:00 至 2024-12-01 23:00:00")
print()

time.sleep(1)

# 模拟回测过程
print("正在运行回测...")
print("-" * 60)
trades = [
    ("2024-01-15 10:00", "BUY", 42500.00),
    ("2024-01-18 14:00", "SELL", 43800.00, 1300.00, 3.06),
    ("2024-02-03 09:00", "BUY", 41200.00),
    ("2024-02-05 15:00", "SELL", 40950.00, -250.00, -0.61),
    ("2024-03-10 11:00", "BUY", 48300.00),
    ("2024-03-12 16:00", "SELL", 50200.00, 1900.00, 3.93),
    ("2024-04-22 08:00", "BUY", 52100.00),
    ("2024-04-23 13:00", "SELL", 51000.00, -1100.00, -2.11),
    ("2024-05-14 10:00", "BUY", 56800.00),
    ("2024-05-17 14:00", "SELL", 58900.00, 2100.00, 3.70),
    ("2024-06-05 09:00", "BUY", 60200.00),
    ("2024-06-08 11:00", "SELL", 62500.00, 2300.00, 3.82),
    ("2024-07-19 12:00", "BUY", 64100.00),
    ("2024-07-20 15:00", "SELL", 62900.00, -1200.00, -1.87),
    ("2024-08-11 10:00", "BUY", 58700.00),
    ("2024-08-14 13:00", "SELL", 60100.00, 1400.00, 2.38),
    ("2024-09-22 11:00", "BUY", 62300.00),
    ("2024-09-25 16:00", "SELL", 64800.00, 2500.00, 4.01),
    ("2024-10-08 09:00", "BUY", 66900.00),
    ("2024-10-11 14:00", "SELL", 69500.00, 2600.00, 3.89),
]

for i, trade in enumerate(trades[:10], 1):
    time.sleep(0.3)
    if len(trade) == 3:
        print(f"  [{i}] {trade[0]} - {trade[1]} at ${trade[2]:.2f}")
    else:
        print(f"  [{i}] {trade[0]} - {trade[1]} at ${trade[2]:.2f} | PnL: ${trade[3]:.2f} ({trade[4]:.2f}%)")

print(f"\n  处理中... (共分析 {len(trades)} 笔交易)")
time.sleep(1)
print()

# 显示回测结果
print("=" * 60)
print("回测结果".center(60))
print("=" * 60)
print()

print("资金变化：")
print("-" * 60)
print(f"初始资金:       $10,000.00")
print(f"最终资金:       $12,850.00")
print(f"总收益:         $2,850.00")
print(f"总收益率:       28.50%")
print()

print("交易统计：")
print("-" * 60)
print(f"总交易次数:     10")
print(f"盈利交易:       7")
print(f"亏损交易:       3")
print(f"胜率:           70.00%")
print()

print("盈亏分析：")
print("-" * 60)
print(f"平均盈利:       $1,885.71")
print(f"平均亏损:       $850.00")
print(f"盈亏比:         2.22")
print(f"最大单笔盈利:   $2,600.00")
print(f"最大单笔亏损:   $1,200.00")
print()

print("风险指标：")
print("-" * 60)
print(f"最大回撤:       -6.80%")
print(f"夏普比率:       2.15")
print(f"收益回撤比:     4.19")
print()

print("=" * 60)
print()

print("✓ 回测完成！")
print()
print("这是演示输出，实际使用时会基于真实市场数据计算")
print()
print("运行真实回测的步骤：")
print("1. 确保安装所有依赖：pip install python-binance pandas numpy pyyaml")
print("2. 运行回测脚本：python run_backtest.py")
print("3. 或使用完整版本：python main.py backtest")
print()
print("=" * 60)
