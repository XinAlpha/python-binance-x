# 快速开始指南

## 一键运行回测

### Windows 用户

1. 打开命令提示符 (cmd) 或 PowerShell
2. 进入项目目录：
   ```cmd
   cd trading_framework
   ```

3. 安装依赖（仅需第一次）：
   ```cmd
   pip install python-binance pandas numpy pyyaml
   ```

4. 运行回测：
   ```cmd
   python run_backtest.py
   ```

### Linux/Mac 用户

1. 打开终端
2. 进入项目目录：
   ```bash
   cd trading_framework
   ```

3. 安装依赖（仅需第一次）：
   ```bash
   pip3 install python-binance pandas numpy pyyaml
   ```

4. 运行回测：
   ```bash
   python3 run_backtest.py
   ```

---

## 预期输出

运行后您会看到类似这样的输出：

```
正在导入模块...
✓ 所有模块导入成功

正在加载配置...
✓ 配置加载成功

============================================================
                        开始回测
============================================================

交易对: BTCUSDT
K线周期: 1h
初始资金: $10,000
回测时间: 2024-01-01 至 2024-12-01
策略: ma_crossover
短期均线: 10
长期均线: 30

正在获取历史数据...
✓ 数据加载完成: 8000 根K线
  时间范围: 2024-01-01 00:00:00 至 2024-12-01 00:00:00

正在初始化策略...
✓ 策略初始化完成

正在运行回测...

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

✓ 回测完成！
```

---

## 常见问题

### Q1: 提示 "ModuleNotFoundError: No module named 'binance'"

**解决方法**：
```bash
pip install python-binance
```

### Q2: 提示 "ModuleNotFoundError: No module named 'pandas'"

**解决方法**：
```bash
pip install pandas numpy
```

### Q3: 提示 "ModuleNotFoundError: No module named 'yaml'"

**解决方法**：
```bash
pip install pyyaml
```

### Q4: 提示 "pip 不是内部或外部命令"

**解决方法**：
- Windows: 确保已安装Python，并将Python添加到系统PATH
- 下载Python: https://www.python.org/downloads/

### Q5: 回测时间太长，如何缩短？

编辑 `config/config.yaml`：
```yaml
backtest:
  start_date: "2024-10-01"  # 改为最近的日期
  end_date: "2024-12-01"
```

### Q6: 想测试其他交易对

编辑 `config/config.yaml`：
```yaml
trading:
  symbol: "ETHUSDT"  # 改为 ETHUSDT 或其他币对
```

### Q7: 如何修改策略参数？

编辑 `config/config.yaml`：
```yaml
strategy:
  params:
    ma_short: 5   # 改为5周期均线
    ma_long: 20   # 改为20周期均线
    stop_loss: 0.03    # 3%止损
    take_profit: 0.06  # 6%止盈
```

---

## 测试依赖是否安装成功

运行测试脚本：
```bash
python test_imports.py
```

应该看到所有模块都显示 ✓

---

## 下一步

### 1. 多次回测验证策略

尝试不同参数组合：
```yaml
# 激进策略
ma_short: 5
ma_long: 15

# 保守策略
ma_short: 20
ma_long: 50

# 中等策略（当前）
ma_short: 10
ma_long: 30
```

### 2. 不同时间段回测

测试策略在不同市场环境下的表现：
- 牛市：2024-01-01 至 2024-03-31
- 熊市：2024-04-01 至 2024-06-30
- 震荡：2024-07-01 至 2024-09-30

### 3. 不同交易对回测

测试策略的通用性：
- BTCUSDT（波动适中）
- ETHUSDT（波动较大）
- BNBUSDT（波动较小）

### 4. 模拟交易（测试网）

回测满意后，进行实时模拟：
```bash
python main.py live
```

确保 `config.yaml` 中 `testnet: true`

---

## 完整命令速查

```bash
# 安装依赖
pip install python-binance pandas numpy pyyaml

# 测试依赖
python test_imports.py

# 运行回测（简化版）
python run_backtest.py

# 运行回测（完整版）
python main.py backtest

# 查看账户信息
python main.py account

# 模拟交易
python main.py live

# 查看帮助
python main.py --help
```

---

## 需要帮助？

如果遇到问题，请检查：
1. ✅ Python 版本 >= 3.7
2. ✅ 所有依赖已安装
3. ✅ 在 `trading_framework` 目录下运行
4. ✅ 网络连接正常（需要访问币安API）

祝回测顺利！🚀
