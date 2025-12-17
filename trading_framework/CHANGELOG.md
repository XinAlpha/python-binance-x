# 更新日志

## [v1.1.0] - 2025-12-17

### 新增功能

#### 1. 动态策略加载系统 ✨
- 添加 `utils/strategy_loader.py` - 统一的策略加载器
- 支持通过配置文件动态切换所有6种策略
- 无需修改代码，只需修改 `config.yaml` 即可切换策略

#### 2. 网络代理支持 🌐
- `DataFetcher` 支持代理配置
- 支持自定义连接超时时间
- 在 `config.yaml` 中添加 `network` 配置段
- 适配中国大陆网络环境

#### 3. 连接测试工具 🔧
- 新增 `test_connection.py` - 网络连接诊断工具
- 自动检测网络问题并提供解决方案
- 测试 Binance API 连接和数据获取

### 修复

#### 1. 修复策略加载错误 🐛
- **问题**: `run_backtest.py` 硬编码 MA 策略参数导致其他策略无法运行
- **影响文件**:
  - `run_backtest.py` (第 47-48行，第 67行)
  - `main.py` (第 14行，第 48行，第 83行)
- **修复**:
  - 移除硬编码的 `MACrossoverStrategy` 导入
  - 使用 `load_strategy()` 动态加载策略
  - 参数显示改为通用格式

#### 2. 修复网络超时问题 ⏱️
- 添加代理配置支持
- 增加超时配置选项
- 所有网络请求统一使用配置的网络参数

### 改进

#### 1. 代码重构
- 统一策略加载逻辑
- 减少代码重复
- 提高可维护性

#### 2. 文档完善
- 添加 `UPDATES.md` - 详细更新说明
- 添加 `CHANGELOG.md` - 更新日志
- 完善网络配置说明

### 文件变更

#### 新增文件
```
utils/strategy_loader.py       # 策略加载器
test_connection.py             # 连接测试工具
UPDATES.md                     # 更新说明文档
CHANGELOG.md                   # 本文件
```

#### 修改文件
```
config/config.yaml             # 添加 network 配置段
utils/data_fetcher.py          # 添加 proxy 和 timeout 参数
main.py                        # 使用动态策略加载 + 网络配置
run_backtest.py                # 使用动态策略加载 + 网络配置
```

### 使用示例

#### 切换策略（只需修改配置文件）

```yaml
# 使用 RSI 策略
strategy:
  name: "rsi"
  params:
    rsi_period: 14
    oversold: 30
    overbought: 70
    stop_loss: 0.02
    take_profit: 0.03
```

#### 配置代理（解决网络连接问题）

```yaml
# 网络配置
network:
  proxy: "http://127.0.0.1:7890"  # 你的代理地址
  timeout: 30
```

### 测试步骤

1. **测试网络连接**
   ```bash
   python test_connection.py
   ```

2. **测试策略导入**
   ```bash
   python test_all_strategies.py
   ```

3. **运行回测**
   ```bash
   python run_backtest.py
   ```

### 兼容性

- Python 3.7+
- python-binance 1.0.32+
- 所有操作系统 (Windows, Linux, macOS)

### 已知问题

#### 网络连接超时
- **问题**: 中国大陆用户可能无法直接访问 Binance API
- **解决方案**:
  1. 配置代理
  2. 使用本地历史数据文件
  3. 增加超时时间
- **详细说明**: 查看 [UPDATES.md](UPDATES.md#网络连接问题解决方案)

### 贡献者

- Claude Sonnet 4.5 <noreply@anthropic.com>

---

## [v1.0.0] - 2025-12-17

### 初始发布

#### 核心功能
- 完整的策略交易框架
- 回测引擎
- 实盘交易执行器
- 模拟交易支持

#### 支持的策略（6种）
1. 均线交叉策略 (MA Crossover)
2. RSI超买超卖策略 (RSI Strategy)
3. 布林带突破策略 (Bollinger Bands Strategy)
4. 网格交易策略 (Grid Trading Strategy)
5. MACD趋势策略 (MACD Strategy)
6. 突破回踩策略 (Breakout Pullback Strategy)

#### 技术指标库
- SMA, EMA, RSI, MACD
- Bollinger Bands, ATR
- Stochastic, ADX
- OBV, VWAP

#### 主要功能
- 策略回测与性能分析
- Paper trading (模拟交易)
- Live trading (实盘交易)
- 风险管理 (止损/止盈)
- 仓位管理
- 完整的日志系统

#### 文档
- README.md - 项目介绍
- STRATEGIES.md - 策略详解
- strategies_summary.txt - 策略快速参考
- INSTALL_GUIDE.md - 安装指南

---

查看完整文档: [UPDATES.md](UPDATES.md) | [STRATEGIES.md](STRATEGIES.md)
