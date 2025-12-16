# 详细安装指南

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / Linux / MacOS
- **网络**: 需要访问币安API（可能需要科学上网）

---

## 🚀 方法一：一键安装运行（推荐）

### Windows 用户

1. **双击运行** `run_backtest.bat`

   脚本会自动：
   - ✓ 检查Python环境
   - ✓ 安装所有依赖
   - ✓ 运行回测

### Linux/Mac 用户

1. **在终端运行**：
   ```bash
   ./run_backtest.sh
   ```

   脚本会自动：
   - ✓ 检查Python环境
   - ✓ 安装所有依赖
   - ✓ 运行回测

---

## 🔧 方法二：手动安装（如果一键安装失败）

### 步骤 1：检查Python环境

打开终端/命令提示符，运行：

**Windows**:
```cmd
python --version
```

**Linux/Mac**:
```bash
python3 --version
```

应该显示 Python 3.7 或更高版本。

**如果没有安装Python**:
- 访问 https://www.python.org/downloads/
- 下载并安装最新版本
- ⚠️ Windows用户安装时勾选 "Add Python to PATH"

---

### 步骤 2：进入项目目录

```bash
cd trading_framework
```

---

### 步骤 3：检查环境

运行环境检查脚本：

**Windows**:
```cmd
python check_environment.py
```

**Linux/Mac**:
```bash
python3 check_environment.py
```

这会告诉您哪些依赖缺失。

---

### 步骤 4：安装依赖

#### 方式 A - 一键安装所有依赖（推荐）

**Windows**:
```cmd
pip install -r requirements.txt
```

**Linux/Mac**:
```bash
pip3 install -r requirements.txt
```

#### 方式 B - 逐个安装

**Windows**:
```cmd
pip install python-binance
pip install pandas
pip install numpy
pip install pyyaml
```

**Linux/Mac**:
```bash
pip3 install python-binance
pip3 install pandas
pip3 install numpy
pip3 install pyyaml
```

---

### 步骤 5：验证安装

再次运行环境检查：

```bash
python check_environment.py
```

应该显示所有依赖都已安装 ✓

---

### 步骤 6：运行回测

**方式 A - 简化版**:
```bash
python run_backtest.py
```

**方式 B - 完整版**:
```bash
python main.py backtest
```

---

## 🎭 演示模式（无需安装依赖）

如果暂时无法安装依赖，可以运行演示脚本查看效果：

```bash
python demo_backtest.py
```

这会显示回测结果的示例输出。

---

## ❓ 常见问题解决

### Q1: "python 不是内部或外部命令"

**原因**: Python未安装或未添加到系统PATH

**解决方法**:
1. 重新安装Python，勾选 "Add Python to PATH"
2. 或手动添加Python到系统环境变量

### Q2: "pip 不是内部或外部命令"

**解决方法**:
```bash
python -m pip install python-binance
```

使用 `python -m pip` 代替 `pip`

### Q3: ModuleNotFoundError: No module named 'binance'

**原因**: python-binance未安装

**解决方法**:
```bash
pip install python-binance
```

### Q4: ModuleNotFoundError: No module named 'pandas'

**解决方法**:
```bash
pip install pandas numpy
```

### Q5: ModuleNotFoundError: No module named 'yaml'

**解决方法**:
```bash
pip install pyyaml
```

### Q6: SSL证书验证失败

**原因**: 网络限制或需要科学上网

**临时解决方法**:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org python-binance
```

### Q7: 权限错误（Permission Denied）

**Linux/Mac解决方法**:
```bash
pip3 install --user python-binance pandas numpy pyyaml
```

或使用sudo（不推荐）:
```bash
sudo pip3 install python-binance pandas numpy pyyaml
```

### Q8: 回测时网络连接错误

**可能原因**:
- 币安API在某些地区被限制
- 需要科学上网

**解决方法**:
- 使用VPN或代理
- 或使用币安的其他域名（在代码中修改）

### Q9: 版本冲突

**解决方法** - 使用虚拟环境:

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📦 依赖包说明

| 包名 | 用途 | 官方文档 |
|------|------|----------|
| **python-binance** | 币安API封装 | https://python-binance.readthedocs.io/ |
| **pandas** | 数据处理 | https://pandas.pydata.org/ |
| **numpy** | 数值计算 | https://numpy.org/ |
| **pyyaml** | 配置文件解析 | https://pyyaml.org/ |

---

## 🧪 验证安装步骤

按顺序运行以下命令验证：

```bash
# 1. 检查Python版本
python --version

# 2. 检查环境
python check_environment.py

# 3. 运行演示（不需要依赖）
python demo_backtest.py

# 4. 运行真实回测（需要所有依赖）
python run_backtest.py
```

---

## 🎯 安装成功标志

当您看到以下输出时，说明安装成功：

```
============================================================
                    BACKTEST RESULTS
============================================================

Initial Capital:     $10,000.00
Final Capital:       $12,850.00
Total Return:        28.50%
...
```

---

## 💡 高级选项

### 使用虚拟环境（推荐）

虚拟环境可以避免依赖冲突：

**创建虚拟环境**:
```bash
python -m venv trading_env
```

**激活虚拟环境**:

Windows:
```cmd
trading_env\Scripts\activate
```

Linux/Mac:
```bash
source trading_env/bin/activate
```

**安装依赖**:
```bash
pip install -r requirements.txt
```

**运行回测**:
```bash
python run_backtest.py
```

**退出虚拟环境**:
```bash
deactivate
```

---

## 📞 需要帮助？

如果以上方法都无法解决问题：

1. ✅ 确认Python版本 >= 3.7
2. ✅ 确认在 `trading_framework` 目录下
3. ✅ 尝试使用虚拟环境
4. ✅ 检查网络连接
5. ✅ 查看详细错误信息

---

## ✅ 快速命令参考

```bash
# 环境检查
python check_environment.py

# 演示模式
python demo_backtest.py

# 运行回测（简化）
python run_backtest.py

# 运行回测（完整）
python main.py backtest

# 查看账户
python main.py account

# 模拟交易
python main.py live

# 查看帮助
python main.py --help
```

祝您安装顺利！🚀
