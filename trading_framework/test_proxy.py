#!/usr/bin/env python3
"""
代理测试工具 - 测试不同代理端口的连接
"""
import sys
import requests

print("=" * 70)
print("代理连接测试工具".center(70))
print("=" * 70)
print()

# 常见代理端口
common_proxies = [
    ("Custom", "http://127.0.0.1:31080"),
    ("Clash", "http://127.0.0.1:7890"),
    ("V2Ray", "http://127.0.0.1:10809"),
    ("Shadowsocks", "http://127.0.0.1:1080"),
    ("Clash Verge", "http://127.0.0.1:7897"),
]

print("正在测试常见代理端口...\n")

working_proxies = []

for name, proxy in common_proxies:
    try:
        print(f"测试 {name:15s} ({proxy})... ", end="", flush=True)

        # 测试连接
        response = requests.get(
            "https://api.binance.com/api/v3/ping",
            proxies={"http": proxy, "https": proxy},
            timeout=5
        )

        if response.status_code == 200:
            print("✓ 连接成功！")
            working_proxies.append((name, proxy))
        else:
            print(f"✗ 失败 (状态码: {response.status_code})")

    except requests.exceptions.ProxyError:
        print("✗ 代理未运行")
    except requests.exceptions.Timeout:
        print("✗ 连接超时")
    except requests.exceptions.ConnectionError:
        print("✗ 连接被拒绝")
    except Exception as e:
        print(f"✗ 错误: {type(e).__name__}")

print()
print("=" * 70)

if working_proxies:
    print("✓ 找到可用的代理！".center(70))
    print("=" * 70)
    print()

    for name, proxy in working_proxies:
        print(f"  {name}: {proxy}")

    print()
    print("请将以下配置添加到 config/config.yaml:")
    print()
    print("network:")
    print(f"  proxy: \"{working_proxies[0][1]}\"")
    print("  timeout: 60")
    print()

else:
    print("✗ 未找到可用的代理".center(70))
    print("=" * 70)
    print()
    print("解决方案:")
    print()
    print("1. 确保代理软件正在运行")
    print("   - Clash / V2Ray / Shadowsocks 等")
    print()
    print("2. 检查代理软件设置")
    print("   - 查看 HTTP/HTTPS 代理端口")
    print("   - 确认允许局域网连接")
    print()
    print("3. 手动测试代理")
    print("   在浏览器设置中配置代理，访问 https://www.google.com")
    print()
    print("4. 如果你知道代理地址，手动配置 config/config.yaml:")
    print()
    print("   network:")
    print("     proxy: \"http://127.0.0.1:YOUR_PORT\"  # 替换 YOUR_PORT")
    print("     timeout: 60")
    print()

print()
print("=" * 70)
print("测试完成".center(70))
print("=" * 70)
print()

# 提供额外的诊断信息
print("💡 提示:")
print()
print("- 如果你使用 Clash，默认端口通常是 7890")
print("- 如果你使用 V2Ray，默认端口通常是 10809")
print("- 打开代理软件查看设置以确认端口号")
print("- 代理地址格式必须是: http://127.0.0.1:端口号")
print()

if not working_proxies:
    print("⚠️  无法连接到 Binance API 将导致:")
    print("   - 无法获取历史数据进行回测")
    print("   - 无法进行实盘交易")
    print("   - 需要先解决网络问题才能继续")
    print()
