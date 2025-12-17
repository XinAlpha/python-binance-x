"""
MACD趋势策略 - 基于MACD指标的趋势跟踪策略
适用于趋势明显的市场
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging

logger = logging.getLogger(__name__)


class MACDStrategy(BaseStrategy):
    """
    MACD趋势策略

    策略逻辑：
    - MACD线上穿信号线（金叉） → 做多
    - MACD线下穿信号线（死叉） → 做空/平多
    - 柱状图由负转正 → 趋势增强
    - 结合零轴位置判断主趋势

    进阶功能：
    - MACD背离检测
    - 零轴突破确认
    - 柱状图能量分析

    参数说明：
    - fast_period: 快速EMA周期 (默认12)
    - slow_period: 慢速EMA周期 (默认26)
    - signal_period: 信号线周期 (默认9)
    - use_histogram: 是否使用柱状图确认 (默认True)
    - use_zero_cross: 是否使用零轴穿越确认 (默认False)
    """

    def __init__(self, config):
        super().__init__(config)
        self.fast_period = self.params.get('fast_period', 12)
        self.slow_period = self.params.get('slow_period', 26)
        self.signal_period = self.params.get('signal_period', 9)
        self.use_histogram = self.params.get('use_histogram', True)
        self.use_zero_cross = self.params.get('use_zero_cross', False)

        logger.info(f"MACD Strategy initialized - Fast: {self.fast_period}, "
                   f"Slow: {self.slow_period}, Signal: {self.signal_period}")

    def calculate_signals(self, df):
        """计算MACD和交易信号"""
        # 计算MACD
        macd_line, signal_line, histogram = Indicators.macd(
            df['close'], self.fast_period, self.slow_period, self.signal_period
        )

        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = histogram

        # 计算MACD相对于零轴的位置
        df['macd_above_zero'] = df['macd'] > 0
        df['macd_below_zero'] = df['macd'] < 0

        # 计算柱状图的变化趋势
        df['histogram_increasing'] = df['macd_histogram'] > df['macd_histogram'].shift(1)
        df['histogram_decreasing'] = df['macd_histogram'] < df['macd_histogram'].shift(1)

        # 计算MACD强度（柱状图绝对值）
        df['macd_strength'] = abs(df['macd_histogram'])

        # 检测金叉死叉
        df['macd_golden_cross'] = (
            (df['macd'] > df['macd_signal']) &
            (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        )

        df['macd_death_cross'] = (
            (df['macd'] < df['macd_signal']) &
            (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        )

        # 检测零轴穿越
        df['zero_cross_up'] = (
            (df['macd'] > 0) &
            (df['macd'].shift(1) <= 0)
        )

        df['zero_cross_down'] = (
            (df['macd'] < 0) &
            (df['macd'].shift(1) >= 0)
        )

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：
        1. MACD金叉（MACD线上穿信号线）
        2. 可选：柱状图由负转正或正在增长
        3. 可选：MACD在零轴上方（强趋势确认）
        """
        if current_index < max(self.slow_period, self.signal_period) + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 核心条件：MACD金叉
        if current.get('macd_golden_cross', False):
            logger.info(f"MACD golden cross detected")

            # 额外确认条件
            confirmations = []

            # 1. 柱状图确认
            if self.use_histogram:
                if current['macd_histogram'] > 0 or current.get('histogram_increasing', False):
                    confirmations.append('histogram')
                else:
                    logger.debug("Histogram confirmation failed")
                    return False

            # 2. 零轴确认
            if self.use_zero_cross:
                if current['macd'] > 0:
                    confirmations.append('zero_axis')
                else:
                    logger.debug("Zero axis confirmation failed")
                    return False

            logger.info(f"Long signal confirmed with: {confirmations}")
            return True

        # 补充条件：零轴向上突破（强烈做多信号）
        if self.use_zero_cross and current.get('zero_cross_up', False):
            if current['macd'] > current['macd_signal']:
                logger.info(f"Long signal: Zero axis breakout")
                return True

        return False

    def should_enter_short(self, df, current_index):
        """
        做空条件：
        1. MACD死叉（MACD线下穿信号线）
        2. 可选：柱状图由正转负或正在减小
        3. 可选：MACD在零轴下方（强趋势确认）
        """
        if current_index < max(self.slow_period, self.signal_period) + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 核心条件：MACD死叉
        if current.get('macd_death_cross', False):
            logger.info(f"MACD death cross detected")

            # 额外确认条件
            confirmations = []

            # 1. 柱状图确认
            if self.use_histogram:
                if current['macd_histogram'] < 0 or current.get('histogram_decreasing', False):
                    confirmations.append('histogram')
                else:
                    logger.debug("Histogram confirmation failed")
                    return False

            # 2. 零轴确认
            if self.use_zero_cross:
                if current['macd'] < 0:
                    confirmations.append('zero_axis')
                else:
                    logger.debug("Zero axis confirmation failed")
                    return False

            logger.info(f"Short signal confirmed with: {confirmations}")
            return True

        # 补充条件：零轴向下突破（强烈做空信号）
        if self.use_zero_cross and current.get('zero_cross_down', False):
            if current['macd'] < current['macd_signal']:
                logger.info(f"Short signal: Zero axis breakdown")
                return True

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        1. MACD死叉
        2. 柱状图显著减小
        3. MACD跌破零轴
        """
        if current_index < max(self.slow_period, self.signal_period) + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 主要出场信号：死叉
        if current.get('macd_death_cross', False):
            logger.info(f"Exit long: MACD death cross")
            return True

        # 补充出场信号：MACD跌破零轴
        if self.use_zero_cross and current.get('zero_cross_down', False):
            logger.info(f"Exit long: MACD crossed below zero")
            return True

        # 紧急出场：柱状图快速衰减
        if self.use_histogram:
            if (current['macd_histogram'] < previous['macd_histogram'] and
                previous['macd_histogram'] < df.iloc[current_index - 2]['macd_histogram']):
                # 连续两根K线柱状图减小
                if current['macd_histogram'] < previous['macd_histogram'] * 0.5:
                    logger.info(f"Exit long: Histogram rapid decay")
                    return True

        return False

    def should_exit_short(self, df, current_index):
        """
        平空条件：
        1. MACD金叉
        2. 柱状图显著增大
        3. MACD突破零轴
        """
        if current_index < max(self.slow_period, self.signal_period) + 1:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 主要出场信号：金叉
        if current.get('macd_golden_cross', False):
            logger.info(f"Exit short: MACD golden cross")
            return True

        # 补充出场信号：MACD突破零轴
        if self.use_zero_cross and current.get('zero_cross_up', False):
            logger.info(f"Exit short: MACD crossed above zero")
            return True

        # 紧急出场：柱状图快速增强
        if self.use_histogram:
            if (current['macd_histogram'] > previous['macd_histogram'] and
                previous['macd_histogram'] > df.iloc[current_index - 2]['macd_histogram']):
                # 连续两根K线柱状图增大
                if abs(current['macd_histogram']) > abs(previous['macd_histogram']) * 1.5:
                    logger.info(f"Exit short: Histogram rapid increase")
                    return True

        return False

    def _detect_divergence(self, df, current_index, divergence_type='bullish'):
        """
        检测MACD背离（高级功能）

        Args:
            df: 数据框
            current_index: 当前索引
            divergence_type: 'bullish' 或 'bearish'

        Returns:
            bool: 是否检测到背离
        """
        if current_index < 20:
            return False

        lookback = 20
        recent_data = df.iloc[current_index - lookback:current_index + 1]

        if divergence_type == 'bullish':
            # 底背离：价格创新低，但MACD未创新低
            price_low_idx = recent_data['close'].idxmin()
            macd_low_idx = recent_data['macd'].idxmin()

            if price_low_idx != macd_low_idx:
                current_price = df.iloc[current_index]['close']
                current_macd = df.iloc[current_index]['macd']

                if (current_price < recent_data['close'].min() and
                    current_macd > recent_data['macd'].min()):
                    return True

        else:  # bearish
            # 顶背离：价格创新高，但MACD未创新高
            price_high_idx = recent_data['close'].idxmax()
            macd_high_idx = recent_data['macd'].idxmax()

            if price_high_idx != macd_high_idx:
                current_price = df.iloc[current_index]['close']
                current_macd = df.iloc[current_index]['macd']

                if (current_price > recent_data['close'].max() and
                    current_macd < recent_data['macd'].max()):
                    return True

        return False
