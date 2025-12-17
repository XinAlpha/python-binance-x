"""
突破回踩策略 - 趋势跟踪的经典策略
在突破关键位后等待回踩再入场，提高胜率
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging
import numpy as np

logger = logging.getLogger(__name__)


class BreakoutPullbackStrategy(BaseStrategy):
    """
    突破回踩策略

    策略逻辑：
    1. 识别关键支撑/阻力位
    2. 价格突破阻力位 → 等待回踩确认 → 做多
    3. 价格跌破支撑位 → 等待反弹确认 → 做空
    4. 使用成交量确认突破有效性

    适用场景：
    - 趋势市场
    - 关键位突破
    - 盘整后的方向选择

    参数说明：
    - lookback_period: 寻找支撑阻力的回溯周期 (默认20)
    - breakout_threshold: 突破幅度阈值 (默认0.01，即1%)
    - pullback_ratio: 回踩比例 (默认0.5，回踩50%)
    - use_volume: 是否使用成交量确认 (默认True)
    - volume_multiplier: 成交量倍数 (默认1.5)
    """

    def __init__(self, config):
        super().__init__(config)
        self.lookback_period = self.params.get('lookback_period', 20)
        self.breakout_threshold = self.params.get('breakout_threshold', 0.01)
        self.pullback_ratio = self.params.get('pullback_ratio', 0.5)
        self.use_volume = self.params.get('use_volume', True)
        self.volume_multiplier = self.params.get('volume_multiplier', 1.5)

        # 状态变量
        self.resistance_level = None
        self.support_level = None
        self.breakout_high = None
        self.breakout_low = None
        self.awaiting_pullback = False
        self.pullback_direction = None  # 'long' or 'short'

        logger.info(f"Breakout Pullback Strategy initialized - Lookback: {self.lookback_period}, "
                   f"Threshold: {self.breakout_threshold*100}%")

    def calculate_signals(self, df):
        """计算支撑阻力位和交易信号"""
        # 计算支撑和阻力位
        df['resistance'] = df['high'].rolling(window=self.lookback_period).max()
        df['support'] = df['low'].rolling(window=self.lookback_period).min()

        # 计算平均成交量
        df['avg_volume'] = df['volume'].rolling(window=self.lookback_period).mean()

        # 计算波动率（ATR）
        df['atr'] = Indicators.atr(df['high'], df['low'], df['close'], period=14)

        # 标记关键价格水平
        df = self._identify_key_levels(df)

        # 检测突破
        df['resistance_breakout'] = (
            (df['close'] > df['resistance']) &
            (df['close'].shift(1) <= df['resistance'].shift(1))
        )

        df['support_breakdown'] = (
            (df['close'] < df['support']) &
            (df['close'].shift(1) >= df['support'].shift(1))
        )

        # 成交量确认
        if self.use_volume:
            df['volume_confirmed'] = df['volume'] > df['avg_volume'] * self.volume_multiplier
        else:
            df['volume_confirmed'] = True

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：
        1. 价格突破阻力位（已发生）
        2. 价格回踩至关键位（斐波那契50%或支撑位）
        3. 出现反弹信号（价格开始回升）
        4. 成交量确认
        """
        if current_index < self.lookback_period + 5:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 检查是否刚刚发生突破
        if current.get('resistance_breakout', False) and current.get('volume_confirmed', False):
            self.resistance_level = previous['resistance']
            self.breakout_high = current['high']
            self.awaiting_pullback = True
            self.pullback_direction = 'long'
            logger.info(f"Resistance breakout detected at {current['close']:.2f}, awaiting pullback")
            return False

        # 如果正在等待回踩
        if self.awaiting_pullback and self.pullback_direction == 'long':
            if self.resistance_level is None:
                return False

            current_price = current['close']
            previous_price = previous['close']

            # 计算回踩幅度
            if self.breakout_high:
                pullback_level = self.resistance_level + (self.breakout_high - self.resistance_level) * (1 - self.pullback_ratio)

                # 价格已回踩到目标位置且开始反弹
                if previous_price <= pullback_level and current_price > previous_price:
                    # 确认反弹
                    if self._confirm_reversal(df, current_index, direction='up'):
                        logger.info(f"Long signal: Pullback complete at {current_price:.2f}, "
                                  f"target was {pullback_level:.2f}")
                        self._reset_breakout_state()
                        return True

        return False

    def should_enter_short(self, df, current_index):
        """
        做空条件：
        1. 价格跌破支撑位（已发生）
        2. 价格反弹至关键位
        3. 出现回落信号（价格开始下跌）
        4. 成交量确认
        """
        if current_index < self.lookback_period + 5:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 检查是否刚刚发生跌破
        if current.get('support_breakdown', False) and current.get('volume_confirmed', False):
            self.support_level = previous['support']
            self.breakout_low = current['low']
            self.awaiting_pullback = True
            self.pullback_direction = 'short'
            logger.info(f"Support breakdown detected at {current['close']:.2f}, awaiting pullback")
            return False

        # 如果正在等待反弹回踩
        if self.awaiting_pullback and self.pullback_direction == 'short':
            if self.support_level is None:
                return False

            current_price = current['close']
            previous_price = previous['close']

            # 计算反弹幅度
            if self.breakout_low:
                pullback_level = self.support_level - (self.support_level - self.breakout_low) * (1 - self.pullback_ratio)

                # 价格已反弹到目标位置且开始回落
                if previous_price >= pullback_level and current_price < previous_price:
                    # 确认回落
                    if self._confirm_reversal(df, current_index, direction='down'):
                        logger.info(f"Short signal: Pullback complete at {current_price:.2f}, "
                                  f"target was {pullback_level:.2f}")
                        self._reset_breakout_state()
                        return True

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        1. 价格跌破支撑位
        2. 价格创新低
        3. 动量减弱
        """
        if current_index < 5:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 跌破支撑位
        if current.get('support_breakdown', False):
            logger.info(f"Exit long: Support breakdown")
            return True

        # 价格显著回落
        if self.entry_price > 0:
            drawdown = (self.entry_price - current['close']) / self.entry_price
            if drawdown > 0.03:  # 回撤超过3%
                logger.info(f"Exit long: Significant drawdown {drawdown:.2%}")
                return True

        return False

    def should_exit_short(self, df, current_index):
        """
        平空条件：
        1. 价格突破阻力位
        2. 价格创新高
        3. 动量转强
        """
        if current_index < 5:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 突破阻力位
        if current.get('resistance_breakout', False):
            logger.info(f"Exit short: Resistance breakout")
            return True

        # 价格显著反弹
        if self.entry_price > 0:
            drawdown = (current['close'] - self.entry_price) / self.entry_price
            if drawdown > 0.03:  # 反弹超过3%
                logger.info(f"Exit short: Significant bounce {drawdown:.2%}")
                return True

        return False

    def _identify_key_levels(self, df):
        """
        识别关键价格水平（支撑和阻力）

        使用局部极值点方法
        """
        window = 5

        # 识别局部高点
        df['local_high'] = (
            (df['high'] == df['high'].rolling(window=window * 2 + 1, center=True).max())
        )

        # 识别局部低点
        df['local_low'] = (
            (df['low'] == df['low'].rolling(window=window * 2 + 1, center=True).min())
        )

        return df

    def _confirm_reversal(self, df, current_index, direction='up'):
        """
        确认反转信号

        Args:
            df: 数据框
            current_index: 当前索引
            direction: 'up' 或 'down'

        Returns:
            bool: 是否确认反转
        """
        if current_index < 3:
            return False

        current = df.iloc[current_index]
        prev1 = df.iloc[current_index - 1]
        prev2 = df.iloc[current_index - 2]

        if direction == 'up':
            # 向上反转：连续两根K线收高
            if (current['close'] > prev1['close'] and
                prev1['close'] > prev2['close']):
                # 成交量确认
                if not self.use_volume or current['volume'] > prev1['volume']:
                    return True

        else:  # down
            # 向下反转：连续两根K线收低
            if (current['close'] < prev1['close'] and
                prev1['close'] < prev2['close']):
                # 成交量确认
                if not self.use_volume or current['volume'] > prev1['volume']:
                    return True

        return False

    def _reset_breakout_state(self):
        """重置突破状态"""
        self.awaiting_pullback = False
        self.pullback_direction = None
        self.breakout_high = None
        self.breakout_low = None

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.resistance_level = None
        self.support_level = None
        self._reset_breakout_state()
        logger.info("Breakout pullback strategy reset")
