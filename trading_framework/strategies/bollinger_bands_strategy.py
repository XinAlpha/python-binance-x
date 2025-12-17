"""
布林带突破策略 - 基于波动率的交易策略
适用于趋势市场和震荡市场
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging

logger = logging.getLogger(__name__)


class BollingerBandsStrategy(BaseStrategy):
    """
    布林带突破策略

    策略逻辑：
    - 价格突破上轨 → 做多（趋势跟随）或做空（均值回归）
    - 价格突破下轨 → 做空（趋势跟随）或做多（均值回归）
    - 价格回到中轨附近 → 平仓

    两种模式：
    1. 趋势跟随模式：突破上轨做多，突破下轨做空
    2. 均值回归模式：触及下轨做多，触及上轨做空

    参数说明：
    - bb_period: 布林带周期 (默认20)
    - bb_std: 标准差倍数 (默认2)
    - mode: 'trend' 或 'mean_reversion' (默认'mean_reversion')
    - squeeze_threshold: 挤压阈值，用于判断突破力度 (默认0.02)
    """

    def __init__(self, config):
        super().__init__(config)
        self.bb_period = self.params.get('bb_period', 20)
        self.bb_std = self.params.get('bb_std', 2.0)
        self.mode = self.params.get('mode', 'mean_reversion')  # 'trend' or 'mean_reversion'
        self.squeeze_threshold = self.params.get('squeeze_threshold', 0.02)

        logger.info(f"Bollinger Bands Strategy initialized - Period: {self.bb_period}, "
                   f"Std: {self.bb_std}, Mode: {self.mode}")

    def calculate_signals(self, df):
        """计算布林带和交易信号"""
        # 计算布林带
        upper, middle, lower = Indicators.bollinger_bands(
            df['close'], self.bb_period, self.bb_std
        )

        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower

        # 计算带宽（用于判断波动率）
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        # 计算价格相对位置（%B指标）
        df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # 检测布林带挤压（低波动率，可能预示突破）
        df['bb_squeeze'] = df['bb_width'] < self.squeeze_threshold

        # 标记价格位置
        df['above_upper'] = df['close'] > df['bb_upper']
        df['below_lower'] = df['close'] < df['bb_lower']
        df['near_middle'] = abs(df['close'] - df['bb_middle']) / df['bb_middle'] < 0.005

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：
        - 均值回归模式：价格触及下轨或跌破后回升
        - 趋势跟随模式：价格突破上轨
        """
        if current_index < self.bb_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_close = current['close']
        bb_lower = current['bb_lower']
        bb_upper = current['bb_upper']
        bb_percent = current.get('bb_percent')

        if self.mode == 'mean_reversion':
            # 均值回归：价格触及或跌破下轨后回升
            if previous['close'] <= previous['bb_lower'] and current_close > bb_lower:
                logger.info(f"Long signal (mean reversion): Price bouncing from lower band")
                return True

            # 价格在下轨附近且开始回升
            if bb_percent is not None and 0 < bb_percent < 0.1:
                if current_close > previous['close']:
                    logger.info(f"Long signal (mean reversion): Price near lower band and rising")
                    return True

        else:  # trend following
            # 趋势跟随：价格突破上轨
            if previous['close'] <= previous['bb_upper'] and current_close > bb_upper:
                # 确认突破有效（成交量或前期挤压）
                if current.get('bb_squeeze', False) or df.iloc[current_index - 5:current_index]['bb_squeeze'].any():
                    logger.info(f"Long signal (trend): Breakout above upper band")
                    return True

        return False

    def should_enter_short(self, df, current_index):
        """
        做空条件：
        - 均值回归模式：价格触及上轨或突破后回落
        - 趋势跟随模式：价格突破下轨
        """
        if current_index < self.bb_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_close = current['close']
        bb_lower = current['bb_lower']
        bb_upper = current['bb_upper']
        bb_percent = current.get('bb_percent')

        if self.mode == 'mean_reversion':
            # 均值回归：价格触及或突破上轨后回落
            if previous['close'] >= previous['bb_upper'] and current_close < bb_upper:
                logger.info(f"Short signal (mean reversion): Price falling from upper band")
                return True

            # 价格在上轨附近且开始回落
            if bb_percent is not None and 0.9 < bb_percent < 1.0:
                if current_close < previous['close']:
                    logger.info(f"Short signal (mean reversion): Price near upper band and falling")
                    return True

        else:  # trend following
            # 趋势跟随：价格跌破下轨
            if previous['close'] >= previous['bb_lower'] and current_close < bb_lower:
                # 确认突破有效
                if current.get('bb_squeeze', False) or df.iloc[current_index - 5:current_index]['bb_squeeze'].any():
                    logger.info(f"Short signal (trend): Breakdown below lower band")
                    return True

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        - 均值回归：价格回到中轨或触及上轨
        - 趋势跟随：价格跌破中轨或下轨
        """
        if current_index < self.bb_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_close = current['close']
        bb_middle = current['bb_middle']
        bb_upper = current['bb_upper']

        if self.mode == 'mean_reversion':
            # 价格回到中轨附近
            if current.get('near_middle', False):
                logger.info(f"Exit long (mean reversion): Price near middle band")
                return True

            # 价格触及上轨（目标达到）
            if current_close >= bb_upper:
                logger.info(f"Exit long (mean reversion): Price at upper band")
                return True

        else:  # trend following
            # 价格跌破中轨（趋势减弱）
            if previous['close'] >= previous['bb_middle'] and current_close < bb_middle:
                logger.info(f"Exit long (trend): Price below middle band")
                return True

        return False

    def should_exit_short(self, df, current_index):
        """
        平空条件：
        - 均值回归：价格回到中轨或触及下轨
        - 趋势跟随：价格突破中轨或上轨
        """
        if current_index < self.bb_period + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        current_close = current['close']
        bb_middle = current['bb_middle']
        bb_lower = current['bb_lower']

        if self.mode == 'mean_reversion':
            # 价格回到中轨附近
            if current.get('near_middle', False):
                logger.info(f"Exit short (mean reversion): Price near middle band")
                return True

            # 价格触及下轨（目标达到）
            if current_close <= bb_lower:
                logger.info(f"Exit short (mean reversion): Price at lower band")
                return True

        else:  # trend following
            # 价格突破中轨（趋势反转）
            if previous['close'] <= previous['bb_middle'] and current_close > bb_middle:
                logger.info(f"Exit short (trend): Price above middle band")
                return True

        return False
