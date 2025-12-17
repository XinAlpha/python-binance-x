"""
RSI超买超卖策略 - 基于相对强弱指标
适用于震荡市场
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging

logger = logging.getLogger(__name__)


class RSIStrategy(BaseStrategy):
    """
    RSI超买超卖策略

    策略逻辑：
    - RSI < 30 (超卖) → 做多
    - RSI > 70 (超买) → 做空或平仓
    - 适合震荡市场，不适合强趋势市场

    参数说明：
    - rsi_period: RSI周期 (默认14)
    - oversold: 超卖阈值 (默认30)
    - overbought: 超买阈值 (默认70)
    - use_divergence: 是否使用背离信号 (默认False)
    """

    def __init__(self, config):
        super().__init__(config)
        self.rsi_period = self.params.get('rsi_period', 14)
        self.oversold = self.params.get('oversold', 30)
        self.overbought = self.params.get('overbought', 70)
        self.use_divergence = self.params.get('use_divergence', False)

        logger.info(f"RSI Strategy initialized - Period: {self.rsi_period}, "
                   f"Oversold: {self.oversold}, Overbought: {self.overbought}")

    def calculate_signals(self, df):
        """计算RSI和交易信号"""
        # 计算RSI
        df['rsi'] = Indicators.rsi(df['close'], self.rsi_period)

        # 计算RSI的移动平均（用于确认趋势）
        df['rsi_ma'] = Indicators.sma(df['rsi'], 5)

        # 标记超买超卖区域
        df['oversold'] = df['rsi'] < self.oversold
        df['overbought'] = df['rsi'] > self.overbought

        # 如果使用背离信号
        if self.use_divergence:
            df = self._calculate_divergence(df)

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：
        1. RSI从超卖区域(<30)向上突破
        2. RSI开始回升
        """
        if current_index < self.rsi_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_rsi = current.get('rsi')
        previous_rsi = previous.get('rsi')

        if current_rsi is None or previous_rsi is None:
            return False

        # 从超卖区域向上突破
        if previous_rsi <= self.oversold and current_rsi > self.oversold:
            logger.info(f"Long signal: RSI breakout from oversold at {current_rsi:.2f}")
            return True

        # RSI在超卖区域且开始回升
        if current_rsi < self.oversold + 5 and current_rsi > previous_rsi:
            logger.info(f"Long signal: RSI reversal from oversold at {current_rsi:.2f}")
            return True

        return False

    def should_enter_short(self, df, current_index):
        """
        做空条件：
        1. RSI从超买区域(>70)向下突破
        2. RSI开始回落
        """
        if current_index < self.rsi_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_rsi = current.get('rsi')
        previous_rsi = previous.get('rsi')

        if current_rsi is None or previous_rsi is None:
            return False

        # 从超买区域向下突破
        if previous_rsi >= self.overbought and current_rsi < self.overbought:
            logger.info(f"Short signal: RSI breakout from overbought at {current_rsi:.2f}")
            return True

        # RSI在超买区域且开始回落
        if current_rsi > self.overbought - 5 and current_rsi < previous_rsi:
            logger.info(f"Short signal: RSI reversal from overbought at {current_rsi:.2f}")
            return True

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        1. RSI进入超买区域
        2. RSI开始显著回落
        """
        if current_index < self.rsi_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_rsi = current.get('rsi')
        previous_rsi = previous.get('rsi')

        if current_rsi is None or previous_rsi is None:
            return False

        # RSI进入超买区域
        if current_rsi >= self.overbought:
            logger.info(f"Exit long: RSI overbought at {current_rsi:.2f}")
            return True

        # RSI显著回落（下降超过5个点）
        if current_rsi < previous_rsi - 5:
            logger.info(f"Exit long: RSI falling at {current_rsi:.2f}")
            return True

        return False

    def should_exit_short(self, df, current_index):
        """
        平空条件：
        1. RSI进入超卖区域
        2. RSI开始显著回升
        """
        if current_index < self.rsi_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_rsi = current.get('rsi')
        previous_rsi = previous.get('rsi')

        if current_rsi is None or previous_rsi is None:
            return False

        # RSI进入超卖区域
        if current_rsi <= self.oversold:
            logger.info(f"Exit short: RSI oversold at {current_rsi:.2f}")
            return True

        # RSI显著回升（上升超过5个点）
        if current_rsi > previous_rsi + 5:
            logger.info(f"Exit short: RSI rising at {current_rsi:.2f}")
            return True

        return False

    def _calculate_divergence(self, df):
        """
        计算RSI背离信号（高级功能）

        背离说明：
        - 价格创新高，但RSI未创新高 → 顶背离（看跌）
        - 价格创新低，但RSI未创新低 → 底背离（看涨）
        """
        window = 14

        df['price_high'] = df['close'].rolling(window=window).max()
        df['price_low'] = df['close'].rolling(window=window).min()
        df['rsi_high'] = df['rsi'].rolling(window=window).max()
        df['rsi_low'] = df['rsi'].rolling(window=window).min()

        # 检测背离（简化版）
        df['bullish_divergence'] = (
            (df['close'] == df['price_low']) &
            (df['rsi'] > df['rsi_low'].shift(1))
        )

        df['bearish_divergence'] = (
            (df['close'] == df['price_high']) &
            (df['rsi'] < df['rsi_high'].shift(1))
        )

        return df
