# 币安合约交易框架

一个功能完整的 Python 交易框架，支持回测、模拟交易和实盘交易。基于 python-binance 库开发。

## 功能特性

- ✅ **策略回测** - 完整的历史数据回测功能
- ✅ **模拟交易** - 使用币安测试网进行模拟交易
- ✅ **实盘交易** - 支持实盘自动交易
- ✅ **技术指标** - 内置常用技术指标 (MA, RSI, MACD, 布林带等)
- ✅ **风险管理** - 止损止盈、仓位管理
- ✅ **多策略支持** - 易于扩展的策略框架
- ✅ **完整日志** - 详细的交易日志记录

## 项目结构

```
trading_framework/
├── config/
│   └── config.yaml              # 配置文件
├── strategies/
│   ├── base_strategy.py         # 策略基类
│   └── ma_crossover_strategy.py # 均线交叉策略示例
├── backtest/
│   └── backtest_engine.py       # 回测引擎
├── live_trading/
│   └── live_executor.py         # 实盘执行器
├── utils/
│   ├── data_fetcher.py          # 数据获取
│   ├── indicators.py            # 技术指标
│   └── logger.py                # 日志配置
└── main.py                      # 主程序入口
```

## 安装依赖

```bash
# 安装 python-binance
pip install python-binance

# 安装其他依赖
pip install pandas numpy pyyaml
```

## 配置说明

编辑 `config/config.yaml` 文件：

```yaml
# API配置
api:
  api_key: "your_api_key_here"        # 填入您的 API Key
  api_secret: "your_api_secret_here"  # 填入您的 API Secret
  testnet: true                        # true=测试网, false=实盘

# 交易配置
trading:
  symbol: "BTCUSDT"        # 交易对
  interval: "1h"           # K线周期
  leverage: 10             # 杠杆倍数
  initial_capital: 10000   # 初始资金
  max_position_size: 0.5   # 最大仓位比例(50%)

# 策略配置
strategy:
  name: "ma_crossover"
  params:
    ma_short: 10          # 短期均线
    ma_long: 30           # 长期均线
    stop_loss: 0.02       # 止损 2%
    take_profit: 0.04     # 止盈 4%

# 回测配置
backtest:
  start_date: "2024-01-01"
  end_date: "2024-12-01"
```

## 使用方法

### 1. 回测模式

```bash
# 运行回测
python main.py backtest

# 使用自定义配置文件
python main.py backtest --config my_config.yaml
```

回测会输出详细的性能指标：
- 总收益率
- 胜率
- 最大回撤
- 夏普比率
- 交易明细

### 2. 查看账户信息

```bash
# 查看账户余额和持仓
python main.py account
```

### 3. 模拟交易（测试网）

```bash
# 确保 config.yaml 中 testnet: true
python main.py live
```

### 4. 实盘交易

```bash
# 修改 config.yaml 中 testnet: false
# 谨慎操作！建议先在测试网充分测试
python main.py live
```

## 创建自定义策略

继承 `BaseStrategy` 类并实现必要的方法：

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        # 初始化您的参数

    def should_enter_long(self, df, current_index):
        # 实现做多条件
        return True/False

    def should_enter_short(self, df, current_index):
        # 实现做空条件
        return True/False

    def should_exit_long(self, df, current_index):
        # 实现平多条件
        return True/False

    def should_exit_short(self, df, current_index):
        # 实现平空条件
        return True/False

    def calculate_signals(self, df):
        # 计算技术指标和信号
        return df
```

## 示例：均线交叉策略

内置的均线交叉策略逻辑：
- **做多信号**：短期均线上穿长期均线（金叉）
- **平多/做空信号**：短期均线下穿长期均线（死叉）
- **风险控制**：支持止损和止盈

## 回测结果示例

```
============================================================
                    BACKTEST RESULTS
============================================================

Initial Capital:     $10,000.00
Final Capital:       $12,500.00
Total Return:        25.00%
Total PnL:           $2,500.00

────────────────────────────────────────────────────────────

Total Trades:        15
Winning Trades:      9
Losing Trades:       6
Win Rate:            60.00%

────────────────────────────────────────────────────────────

Average Win:         $450.00
Average Loss:        $200.00
Profit Factor:       2.25

────────────────────────────────────────────────────────────

Max Drawdown:        -8.50%
Sharpe Ratio:        1.85

============================================================
```

## 风险提示

⚠️ **重要提示**：

1. **测试先行**：在实盘前务必充分回测和模拟交易
2. **小额起步**：实盘时从小资金开始
3. **风险自负**：加密货币交易风险极高，请谨慎操作
4. **API 安全**：妥善保管您的 API 密钥，不要分享给他人
5. **合理杠杆**：高杠杆有爆仓风险，建议谨慎使用

## 技术指标说明

框架内置以下技术指标：

- **SMA/EMA** - 移动平均线
- **RSI** - 相对强弱指标
- **MACD** - 指数平滑异同移动平均线
- **布林带** - Bollinger Bands
- **ATR** - 平均真实波幅
- **KDJ** - 随机指标
- **ADX** - 平均趋向指标
- **OBV** - 能量潮
- **VWAP** - 成交量加权平均价

所有指标可在 `utils/indicators.py` 中查看和使用。

## 获取币安 API 密钥

1. 注册币安账户：https://www.binance.com
2. 进入账户管理 -> API管理
3. 创建 API 密钥
4. 设置权限：
   - ✅ 启用合约交易
   - ✅ 启用读取
   - ❌ 禁用提现（安全起见）
5. 将 API Key 和 Secret 填入配置文件

### 测试网（推荐先使用）

币安提供免费的测试网环境：
- 测试网地址：https://testnet.binancefuture.com/
- 使用测试网可以零风险测试策略

## 常见问题

### Q: 如何修改交易对？
A: 在 `config/config.yaml` 中修改 `trading.symbol`

### Q: 如何调整策略参数？
A: 在 `config/config.yaml` 中修改 `strategy.params`

### Q: 回测数据从哪里来？
A: 使用 python-binance 从币安获取历史K线数据

### Q: 可以同时运行多个策略吗？
A: 可以，创建多个配置文件，每个策略单独运行

### Q: 如何停止实盘交易？
A: 按 `Ctrl+C` 优雅停止程序

## 进阶功能

### 添加新的技术指标

在 `utils/indicators.py` 中添加：

```python
@staticmethod
def your_indicator(data, period):
    # 计算逻辑
    return result
```

### 多周期策略

修改数据获取逻辑，同时获取多个时间周期的数据进行综合判断。

### WebSocket 实时数据

使用 python-binance 的 WebSocket 功能实现更低延迟的实时交易。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 免责声明

本框架仅供学习和研究使用。使用本框架进行实盘交易的任何损失，作者不承担任何责任。加密货币交易有风险，投资需谨慎。
