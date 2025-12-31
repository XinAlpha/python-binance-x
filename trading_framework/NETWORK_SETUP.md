# 网络连接配置指南

你遇到了 `ConnectionResetError(10054)` 错误，这说明需要配置网络代理。

## 🔧 解决方案

### 方案1：使用代理（推荐）

#### 步骤1：获取代理地址

常见的代理软件端口：
- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809`
- Shadowsocks: `http://127.0.0.1:1080`
- Clash Verge: `http://127.0.0.1:7890`

#### 步骤2：配置代理

编辑 `config/config.yaml`：

```yaml
# 网络配置
network:
  proxy: "http://127.0.0.1:7890"  # 改成你的代理地址
  timeout: 60  # 增加超时时间到60秒
```

#### 步骤3：测试连接

```bash
python test_connection.py
```

---

### 方案2：使用环境变量

如果你不想修改配置文件，可以设置环境变量：

**Windows (PowerShell):**
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
python test_connection.py
```

**Windows (CMD):**
```cmd
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
python test_connection.py
```

---

### 方案3：检查代理软件

1. **确认代理软件正在运行**
   - Clash/V2Ray/Shadowsocks 等是否已启动
   - 检查系统托盘图标

2. **查看代理端口**
   - 打开代理软件设置
   - 查看 HTTP/HTTPS 代理端口
   - 确认是否允许局域网连接

3. **测试代理是否工作**
   ```bash
   curl -x http://127.0.0.1:7890 https://www.google.com
   ```

---

### 方案4：使用系统代理

如果你的系统已经配置了代理，可以让程序使用系统代理：

1. 检查系统代理设置
   - Windows: 设置 → 网络和Internet → 代理
   - 记下代理服务器地址和端口

2. 在 `config.yaml` 中配置相同的地址

---

## 🎯 快速诊断

### 检查代理端口是否开放

**Windows:**
```powershell
netstat -an | findstr "7890"
```

如果看到 `LISTENING`，说明代理正在运行。

### 测试代理连接

创建一个简单的测试脚本 `test_proxy.py`：

```python
import requests

proxy = "http://127.0.0.1:7890"  # 改成你的代理地址

try:
    response = requests.get(
        "https://api.binance.com/api/v3/ping",
        proxies={"http": proxy, "https": proxy},
        timeout=10
    )
    print("✓ 代理连接成功！")
    print(f"状态码: {response.status_code}")
except Exception as e:
    print(f"✗ 代理连接失败: {e}")
    print("\n请检查:")
    print("1. 代理软件是否运行")
    print("2. 代理地址和端口是否正确")
    print("3. 代理是否允许访问 Binance")
```

运行测试：
```bash
python test_proxy.py
```

---

## 📋 完整配置示例

### config/config.yaml 配置示例

```yaml
# 交易框架配置文件

# API配置
api:
  api_key: "your_api_key_here"
  api_secret: "your_api_secret_here"
  testnet: true

# 网络配置 - 重要！
network:
  proxy: "http://127.0.0.1:7890"  # 使用你的代理地址
  timeout: 60  # 增加超时时间

# 交易配置
trading:
  symbol: "BTCUSDT"
  interval: "1h"
  leverage: 10
  initial_capital: 10000
  max_position_size: 0.5
  risk_per_trade: 0.02

# 策略配置
strategy:
  name: "ma_crossover"
  params:
    ma_short: 10
    ma_long: 30
    stop_loss: 0.02
    take_profit: 0.04

# 回测配置
backtest:
  start_date: "2024-01-01"
  end_date: "2024-12-01"
  commission: 0.0004
  slippage: 0.0001

# 实盘配置
live_trading:
  check_interval: 60
  max_retries: 3
  order_timeout: 30

# 日志配置
logging:
  level: "INFO"
  file: "logs/trading.log"
  console: true
```

---

## ⚠️ 常见问题

### Q1: 代理地址不确定

**A:** 检查常用端口：
```bash
# PowerShell
Test-NetConnection -ComputerName 127.0.0.1 -Port 7890
Test-NetConnection -ComputerName 127.0.0.1 -Port 10809
Test-NetConnection -ComputerName 127.0.0.1 -Port 1080
```

### Q2: 配置代理后还是连接失败

**A:** 尝试：
1. 重启代理软件
2. 检查代理软件是否允许访问 api.binance.com
3. 尝试不同的代理端口
4. 检查防火墙设置

### Q3: 没有代理软件怎么办

**A:** 可以：
1. 使用公司/学校提供的代理
2. 使用付费VPN服务
3. 等待网络环境改善后再试

### Q4: 测试时可以用其他API吗

**A:** 可以，编辑 `config.yaml` 测试其他交易所：
```yaml
trading:
  symbol: "BTCUSDT"
```

但注意：本框架专为 Binance 设计，切换交易所需要修改代码。

---

## 🚀 配置成功后

配置好代理后，按以下步骤继续：

```bash
# 1. 测试连接
python test_connection.py

# 2. 测试策略
python test_all_strategies.py

# 3. 运行回测
python run_backtest.py
```

---

## 💡 小提示

1. **代理地址格式**：必须包含 `http://` 前缀
   - ✓ 正确：`http://127.0.0.1:7890`
   - ✗ 错误：`127.0.0.1:7890`

2. **端口号**：不同软件默认端口不同，请查看软件设置

3. **本地地址**：
   - `127.0.0.1` 和 `localhost` 是等价的
   - 都指向本机

4. **代理类型**：
   - HTTP 代理：使用 `http://` 前缀
   - SOCKS5 代理：需要修改代码支持（联系开发者）

---

如果还有问题，请提供：
1. 代理软件名称和版本
2. `test_connection.py` 的完整错误信息
3. 代理软件的端口配置截图

祝配置顺利！🎉
