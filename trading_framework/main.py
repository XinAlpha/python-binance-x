"""
主程序入口 - 策略交易框架
"""
import sys
import yaml
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_fetcher import DataFetcher
from utils.logger import setup_logger
from utils.strategy_loader import load_strategy
from backtest.backtest_engine import BacktestEngine
from live_trading.live_executor import LiveExecutor
from binance.client import Client


def load_config(config_path='config/config.yaml'):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def run_backtest(config):
    """运行回测"""
    print("\n" + "=" * 60)
    print("STARTING BACKTEST MODE".center(60))
    print("=" * 60 + "\n")

    # 初始化数据获取器(回测不需要API密钥)
    network_config = config.get('network', {})
    data_fetcher = DataFetcher(
        proxy=network_config.get('proxy'),
        timeout=network_config.get('timeout', 30)
    )

    # 获取历史数据
    print(f"Fetching historical data for {config['trading']['symbol']}...")
    df = data_fetcher.get_historical_klines(
        symbol=config['trading']['symbol'],
        interval=config['trading']['interval'],
        start_str=config['backtest']['start_date'],
        end_str=config['backtest']['end_date']
    )

    print(f"Data loaded: {len(df)} candles from {df.index[0]} to {df.index[-1]}")

    # 初始化策略
    strategy = load_strategy(config['strategy'])

    # 初始化回测引擎
    backtest_engine = BacktestEngine(strategy, config)

    # 运行回测
    results = backtest_engine.run(df)

    # 打印结果
    backtest_engine.print_results(results)

    return results


def run_live_trading(config):
    """运行实盘/模拟交易"""
    print("\n" + "=" * 60)
    print("STARTING LIVE TRADING MODE".center(60))
    print("=" * 60 + "\n")

    mode = "TESTNET" if config['api']['testnet'] else "LIVE"
    print(f"Mode: {mode}")
    print(f"Symbol: {config['trading']['symbol']}")
    print(f"Interval: {config['trading']['interval']}")
    print(f"Strategy: {config['strategy']['name']}")
    print(f"\nPress Ctrl+C to stop\n")

    # 初始化数据获取器
    network_config = config.get('network', {})
    data_fetcher = DataFetcher(
        api_key=config['api']['api_key'],
        api_secret=config['api']['api_secret'],
        testnet=config['api']['testnet'],
        proxy=network_config.get('proxy'),
        timeout=network_config.get('timeout', 30)
    )

    # 初始化策略
    strategy = load_strategy(config['strategy'])

    # 初始化实盘执行器
    executor = LiveExecutor(strategy, config, data_fetcher)

    # 启动交易
    executor.start()


def get_account_info(config):
    """获取账户信息"""
    print("\n" + "=" * 60)
    print("ACCOUNT INFORMATION".center(60))
    print("=" * 60 + "\n")

    network_config = config.get('network', {})
    data_fetcher = DataFetcher(
        api_key=config['api']['api_key'],
        api_secret=config['api']['api_secret'],
        testnet=config['api']['testnet'],
        proxy=network_config.get('proxy'),
        timeout=network_config.get('timeout', 30)
    )

    # 获取余额
    print("Account Balance:")
    print("-" * 60)
    balances = data_fetcher.get_futures_account_balance()
    for asset, info in balances.items():
        print(f"{asset}:")
        print(f"  Available: {info['available']:.4f}")
        print(f"  Balance:   {info['balance']:.4f}")
        print(f"  PnL:       {info['unrealized_pnl']:.4f}")

    # 获取持仓
    print("\n" + "-" * 60)
    print("Current Positions:")
    print("-" * 60)
    positions = data_fetcher.get_futures_position()

    if positions:
        for pos in positions:
            print(f"\n{pos['symbol']}:")
            print(f"  Side:       {pos['position_side']}")
            print(f"  Amount:     {pos['position_amt']:.6f}")
            print(f"  Entry:      {pos['entry_price']:.2f}")
            print(f"  PnL:        ${pos['unrealized_pnl']:.2f}")
            print(f"  Leverage:   {pos['leverage']}x")
    else:
        print("No open positions")

    print("\n" + "=" * 60 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Trading Framework - Backtest & Live Trading')
    parser.add_argument('mode', choices=['backtest', 'live', 'account'],
                       help='Run mode: backtest, live, or account info')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to config file (default: config/config.yaml)')

    args = parser.parse_args()

    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}")
        print("Please create a config file or specify a valid path with --config")
        return

    # 设置日志
    logger = setup_logger(
        level=config['logging']['level'],
        log_file=config['logging'].get('file'),
        console=config['logging'].get('console', True)
    )

    # 根据模式运行
    try:
        if args.mode == 'backtest':
            run_backtest(config)

        elif args.mode == 'live':
            run_live_trading(config)

        elif args.mode == 'account':
            get_account_info(config)

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
