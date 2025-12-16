#!/usr/bin/env python3
"""测试导入"""
import sys

print("Testing imports...")

try:
    import yaml
    print("✓ yaml")
except ImportError as e:
    print(f"✗ yaml: {e}")

try:
    import pandas
    print("✓ pandas")
except ImportError as e:
    print(f"✗ pandas: {e}")

try:
    import numpy
    print("✓ numpy")
except ImportError as e:
    print(f"✗ numpy: {e}")

try:
    from binance.client import Client
    print("✓ python-binance")
except ImportError as e:
    print(f"✗ python-binance: {e}")

print("\nPython version:", sys.version)
