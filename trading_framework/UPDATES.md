# 框架更新说明

## 最新更新 (2025-12-17)

### 1. 动态策略加载功能

已修复策略加载系统，现在支持通过配置文件动态切换策略。

#### 修改的文件：

1. **utils/strategy_loader.py** (新增)
   - 创建了统一的策略加载器
   - 支持所有6种策略的动态加载
   - 提供清晰的错误提示

2. **run_backtest.py** (已修复)
   - 移除了硬编码的MA策略参数显示
   - 改为通用的策略参数显示
   - 实现动态策略加载

3. **main.py** (已修复)
   - 使用 `load_strategy()` 替代硬编码导入
   - 支持所有模式（回测、实盘、账户查询）

#### 使用方法：

只需修改 `config/config.yaml` 中的策略名称和参数：

```yaml
strategy:
  name: "rsi"  # 可选: ma_crossover, rsi, bollinger_bands, grid_trading, macd, breakout_pullback
  params:
    rsi_period: 14
    oversold: 30
    overbought: 70
    stop_loss: 0.02
    take_profit: 0.03
```

### 2. 可用的策略列表

| 策略名称 | 配置名 | 适用市场 |
|---------|--------|----------|
| 均线交叉 | ma_crossover | 趋势市场 |
| RSI超买超卖 | rsi | 震荡市场 |
| 布林带突破 | bollinger_bands | 全市场 |
| 网格交易 | grid_trading | 震荡市场 |
| MACD趋势 | macd | 趋势市场 |
| 突破回踩 | breakout_pullback | 趋势市场 |

---

## 网络连接问题解决方案

### 问题：连接 Binance API 超时

**错误信息：**
```
HTTPSConnectionPool(host='api.binance.com', port=443): Max retries exceeded with url: /api/v3/ping
(Caused by ConnectTimeoutError)
```

### 解决方案：

#### 方案1：使用代理（推荐）

如果在中国大陆，可能需要配置代理访问 Binance API。

修改 `utils/data_fetcher.py`，在 Client 初始化时添加代理：

```python
from binance.client import Client

# 添加代理配置
proxies = {
    'http': 'http://127.0.0.1:7890',  # 替换为你的代理地址
    'https': 'http://127.0.0.1:7890'
}

self.client = Client(
    api_key=api_key,
    api_secret=api_secret,
    testnet=testnet,
    requests_params={'proxies': proxies, 'timeout': 30}  # 添加这行
)
```

#### 方案2：使用本地历史数据文件

如果无法访问 Binance API，可以下载历史数据文件进行回测。

1. 从 Binance 下载历史数据：https://data.binance.vision/
2. 将数据保存到 `data/` 目录
3. 修改 `utils/data_fetcher.py` 添加本地数据读取功能

#### 方案3：增加超时时间

修改 `utils/data_fetcher.py`，增加连接超时时间：

```python
self.client = Client(
    api_key=api_key,
    api_secret=api_secret,
    testnet=testnet,
    requests_params={'timeout': 60}  # 增加到60秒
)
```

#### 方案4：使用币安中国镜像（如果可用）

某些地区可能有本地镜像服务器，可以咨询币安客服获取。

---

## 测试步骤

### 1. 测试策略导入

```bash
cd trading_framework
python test_all_strategies.py
```

应该看到所有6个策略都成功导入和初始化。

### 2. 测试回测（需要网络）

```bash
python run_backtest.py
```

如果遇到网络问题，请参考上面的"网络连接问题解决方案"。

### 3. 测试不同策略

修改 `config/config.yaml`：

```yaml
# 测试 RSI 策略
strategy:
  name: "rsi"
  params:
    rsi_period: 14
    oversold: 30
    overbought: 70
```

然后运行：
```bash
python run_backtest.py
```

---

## 文件结构

```
trading_framework/
├── config/
│   └── config.yaml              # 配置文件（修改策略名称和参数）
├── strategies/
│   ├── base_strategy.py         # 策略基类
│   ├── ma_crossover_strategy.py # 均线交叉策略
│   ├── rsi_strategy.py          # RSI策略
│   ├── bollinger_bands_strategy.py # 布林带策略
│   ├── grid_trading_strategy.py # 网格策略
│   ├── macd_strategy.py         # MACD策略
│   └── breakout_pullback_strategy.py # 突破回踩策略
├── utils/
│   ├── data_fetcher.py          # 数据获取器（可能需要配置代理）
│   ├── strategy_loader.py       # 策略加载器（新增）
│   └── indicators.py            # 技术指标库
├── backtest/
│   └── backtest_engine.py       # 回测引擎
├── live_trading/
│   └── live_executor.py         # 实盘执行器
├── main.py                      # 主程序入口（已修复）
├── run_backtest.py              # 快速回测脚本（已修复）
├── test_all_strategies.py       # 策略测试工具
├── STRATEGIES.md                # 策略详细文档
├── strategies_summary.txt       # 策略快速参考
└── UPDATES.md                   # 本文件
```

---

## 下一步建议

### 如果无法连接 Binance API：

1. 配置网络代理（推荐方案1）
2. 或者下载历史数据文件进行离线回测（方案2）

### 如果可以连接：

1. 运行 `test_all_strategies.py` 确认所有策略正常
2. 运行 `run_backtest.py` 进行回测
3. 尝试切换不同策略测试
4. 根据回测结果调整参数
5. 模拟交易验证
6. 小额实盘测试

---

## 常见问题

### Q: 如何切换策略？
A: 只需修改 `config/config.yaml` 中的 `strategy.name` 字段。

### Q: 如何自定义策略参数？
A: 修改 `config/config.yaml` 中的 `strategy.params` 字段。

### Q: 网络连接超时怎么办？
A: 参考本文档的"网络连接问题解决方案"部分。

### Q: 如何添加新策略？
A:
1. 在 `strategies/` 目录创建新策略文件
2. 继承 `BaseStrategy` 类
3. 在 `utils/strategy_loader.py` 的 `strategy_map` 中注册
4. 更新 `strategies/__init__.py`

---

## 技术支持

- 详细策略说明：查看 [STRATEGIES.md](STRATEGIES.md)
- 快速参考：查看 [strategies_summary.txt](strategies_summary.txt)
- Python-Binance 文档：https://python-binance.readthedocs.io/

---

祝交易顺利！🚀
