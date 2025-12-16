"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Indicators:
    """技术指标计算器"""

    @staticmethod
    def sma(data, period):
        """
        简单移动平均线 (Simple Moving Average)

        Args:
            data: 价格序列 (Series or DataFrame column)
            period: 周期

        Returns:
            pandas.Series: SMA值
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data, period):
        """
        指数移动平均线 (Exponential Moving Average)

        Args:
            data: 价格序列
            period: 周期

        Returns:
            pandas.Series: EMA值
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(data, period=14):
        """
        相对强弱指标 (Relative Strength Index)

        Args:
            data: 价格序列
            period: 周期 (默认14)

        Returns:
            pandas.Series: RSI值 (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(data, fast=12, slow=26, signal=9):
        """
        MACD指标 (Moving Average Convergence Divergence)

        Args:
            data: 价格序列
            fast: 快线周期 (默认12)
            slow: 慢线周期 (默认26)
            signal: 信号线周期 (默认9)

        Returns:
            tuple: (macd, signal, histogram)
        """
        ema_fast = Indicators.ema(data, fast)
        ema_slow = Indicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = Indicators.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(data, period=20, std_dev=2):
        """
        布林带 (Bollinger Bands)

        Args:
            data: 价格序列
            period: 周期 (默认20)
            std_dev: 标准差倍数 (默认2)

        Returns:
            tuple: (upper_band, middle_band, lower_band)
        """
        middle_band = Indicators.sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def atr(high, low, close, period=14):
        """
        平均真实波幅 (Average True Range)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期 (默认14)

        Returns:
            pandas.Series: ATR值
        """
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def stochastic(high, low, close, k_period=14, d_period=3):
        """
        随机指标 (Stochastic Oscillator)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_period: K线周期 (默认14)
            d_period: D线周期 (默认3)

        Returns:
            tuple: (k_line, d_line)
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_line = k_line.rolling(window=d_period).mean()

        return k_line, d_line

    @staticmethod
    def adx(high, low, close, period=14):
        """
        平均趋向指标 (Average Directional Index)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期 (默认14)

        Returns:
            pandas.Series: ADX值
        """
        # 计算+DM和-DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # 计算ATR
        atr = Indicators.atr(high, low, close, period)

        # 计算+DI和-DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # 计算DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)

        # 计算ADX
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def obv(close, volume):
        """
        能量潮指标 (On Balance Volume)

        Args:
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            pandas.Series: OBV值
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    @staticmethod
    def vwap(high, low, close, volume):
        """
        成交量加权平均价 (Volume Weighted Average Price)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            pandas.Series: VWAP值
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap

    @staticmethod
    def calculate_all_indicators(df, ma_short=10, ma_long=30):
        """
        计算所有常用指标

        Args:
            df: K线数据DataFrame (需包含 open, high, low, close, volume)
            ma_short: 短期均线周期
            ma_long: 长期均线周期

        Returns:
            pandas.DataFrame: 包含所有指标的DataFrame
        """
        logger.info("Calculating technical indicators...")

        result = df.copy()

        # 移动平均线
        result['sma_short'] = Indicators.sma(df['close'], ma_short)
        result['sma_long'] = Indicators.sma(df['close'], ma_long)
        result['ema_short'] = Indicators.ema(df['close'], ma_short)
        result['ema_long'] = Indicators.ema(df['close'], ma_long)

        # RSI
        result['rsi'] = Indicators.rsi(df['close'])

        # MACD
        macd, signal, histogram = Indicators.macd(df['close'])
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_histogram'] = histogram

        # 布林带
        upper, middle, lower = Indicators.bollinger_bands(df['close'])
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower

        # ATR
        result['atr'] = Indicators.atr(df['high'], df['low'], df['close'])

        # Stochastic
        k_line, d_line = Indicators.stochastic(df['high'], df['low'], df['close'])
        result['stoch_k'] = k_line
        result['stoch_d'] = d_line

        # ADX
        result['adx'] = Indicators.adx(df['high'], df['low'], df['close'])

        # OBV
        result['obv'] = Indicators.obv(df['close'], df['volume'])

        # VWAP
        result['vwap'] = Indicators.vwap(df['high'], df['low'], df['close'], df['volume'])

        logger.info("Indicators calculation completed")
        return result
