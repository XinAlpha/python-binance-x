#!/usr/bin/env python3
"""
网络连接测试工具 - 测试是否能正常访问 Binance API
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("Binance API 连接测试".center(70))
print("=" * 70)
print()

# 测试导入
print("1. 测试模块导入...")
try:
    import yaml
    from binance.client import Client
    from utils.data_fetcher import DataFetcher
    print("   ✓ 所有模块导入成功")
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    print("\n请先安装依赖: pip install -r requirements.txt")
    sys.exit(1)

print()

# 加载配置
print("2. 加载配置文件...")
try:
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("   ✓ 配置文件加载成功")

    network_config = config.get('network', {})
    proxy = network_config.get('proxy')
    timeout = network_config.get('timeout', 30)

    if proxy:
        print(f"   使用代理: {proxy}")
    else:
        print("   不使用代理")

    print(f"   连接超时: {timeout}秒")
except Exception as e:
    print(f"   ✗ 配置文件加载失败: {e}")
    sys.exit(1)

print()

# 测试连接
print("3. 测试 Binance API 连接...")
print("   尝试连接 api.binance.com...")

try:
    data_fetcher = DataFetcher(
        proxy=proxy,
        timeout=timeout
    )
    print("   ✓ DataFetcher 初始化成功")
except Exception as e:
    print(f"   ✗ DataFetcher 初始化失败: {e}")
    sys.exit(1)

print()

# 测试获取服务器时间
print("4. 测试获取服务器时间...")
try:
    server_time = data_fetcher.client.get_server_time()
    import datetime
    server_dt = datetime.datetime.fromtimestamp(server_time['serverTime'] / 1000)
    print(f"   ✓ 服务器时间: {server_dt}")
except Exception as e:
    print(f"   ✗ 获取服务器时间失败: {e}")
    print()
    print("=" * 70)
    print("连接失败！可能的原因:".center(70))
    print("=" * 70)
    print()
    print("1. 网络问题")
    print("   - 检查网络连接是否正常")
    print("   - 尝试在浏览器访问 https://www.binance.com")
    print()
    print("2. 需要配置代理（中国大陆用户）")
    print("   - 编辑 config/config.yaml")
    print("   - 设置 network.proxy 为你的代理地址")
    print("   - 例如: proxy: \"http://127.0.0.1:7890\"")
    print()
    print("3. 防火墙或安全软件阻止")
    print("   - 检查防火墙设置")
    print("   - 暂时关闭安全软件测试")
    print()
    print("4. 增加超时时间")
    print("   - 编辑 config/config.yaml")
    print("   - 设置 network.timeout: 60")
    print()
    sys.exit(1)

print()

# 测试获取市场数据
print("5. 测试获取市场数据...")
symbol = config['trading']['symbol']
try:
    price = data_fetcher.get_current_price(symbol)
    print(f"   ✓ {symbol} 当前价格: ${price:,.2f}")
except Exception as e:
    print(f"   ✗ 获取价格失败: {e}")
    sys.exit(1)

print()

# 测试获取历史K线
print("6. 测试获取历史K线（最近100根）...")
try:
    df = data_fetcher.get_historical_klines(
        symbol=symbol,
        interval='1h',
        start_str='2 days ago UTC',
        limit=100
    )
    print(f"   ✓ 获取成功: {len(df)} 根K线")
    print(f"   时间范围: {df.index[0]} 至 {df.index[-1]}")
except Exception as e:
    print(f"   ✗ 获取K线失败: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✓ 所有测试通过！网络连接正常！".center(70))
print("=" * 70)
print()
print("下一步:")
print("  1. 运行策略测试: python test_all_strategies.py")
print("  2. 运行回测: python run_backtest.py")
print("  3. 查看文档: STRATEGIES.md")
print()
