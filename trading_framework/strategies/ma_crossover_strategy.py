"""
均线交叉策略 - 示例策略实现
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging

logger = logging.getLogger(__name__)


class MACrossoverStrategy(BaseStrategy):
    """
    均线交叉策略
    - 金叉(短期均线上穿长期均线)时做多
    - 死叉(短期均线下穿长期均线)时平多/做空
    - 支持止损止盈
    """

    def __init__(self, config):
        super().__init__(config)
        self.ma_short_period = self.params.get('ma_short', 10)
        self.ma_long_period = self.params.get('ma_long', 30)
        logger.info(f"MA Crossover Strategy initialized - Short: {self.ma_short_period}, Long: {self.ma_long_period}")

    def calculate_signals(self, df):
        """
        计算交易信号

        Args:
            df: K线数据DataFrame

        Returns:
            DataFrame: 添加了信号列的数据
        """
        # 计算均线
        df['ma_short'] = Indicators.sma(df['close'], self.ma_short_period)
        df['ma_long'] = Indicators.sma(df['close'], self.ma_long_period)

        # 计算均线差值
        df['ma_diff'] = df['ma_short'] - df['ma_long']
        df['ma_diff_prev'] = df['ma_diff'].shift(1)

        # 生成信号
        df['signal'] = 'HOLD'

        # 金叉 - 买入信号
        golden_cross = (df['ma_diff'] > 0) & (df['ma_diff_prev'] <= 0)
        df.loc[golden_cross, 'signal'] = 'BUY'

        # 死叉 - 卖出信号
        death_cross = (df['ma_diff'] < 0) & (df['ma_diff_prev'] >= 0)
        df.loc[death_cross, 'signal'] = 'SELL'

        return df

    def should_enter_long(self, df, current_index):
        """
        判断是否应该做多

        条件:
        1. 短期均线上穿长期均线(金叉)
        2. 当前无持仓

        Args:
            df: K线数据
            current_index: 当前索引

        Returns:
            bool: 是否做多
        """
        if current_index < self.ma_long_period:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 计算均线
        ma_short_current = current.get('ma_short', None)
        ma_long_current = current.get('ma_long', None)
        ma_short_prev = previous.get('ma_short', None)
        ma_long_prev = previous.get('ma_long', None)

        if any(x is None for x in [ma_short_current, ma_long_current, ma_short_prev, ma_long_prev]):
            return False

        # 金叉判断
        golden_cross = (ma_short_prev <= ma_long_prev) and (ma_short_current > ma_long_current)

        if golden_cross:
            logger.info(f"Golden cross detected at index {current_index}")
            return True

        return False

    def should_enter_short(self, df, current_index):
        """
        判断是否应该做空

        条件:
        1. 短期均线下穿长期均线(死叉)
        2. 当前无持仓

        Args:
            df: K线数据
            current_index: 当前索引

        Returns:
            bool: 是否做空
        """
        if current_index < self.ma_long_period:
            return False

        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        # 计算均线
        ma_short_current = current.get('ma_short', None)
        ma_long_current = current.get('ma_long', None)
        ma_short_prev = previous.get('ma_short', None)
        ma_long_prev = previous.get('ma_long', None)

        if any(x is None for x in [ma_short_current, ma_long_current, ma_short_prev, ma_long_prev]):
            return False

        # 死叉判断
        death_cross = (ma_short_prev >= ma_long_prev) and (ma_short_current < ma_long_current)

        if death_cross:
            logger.info(f"Death cross detected at index {current_index}")
            return True

        return False

    def should_exit_long(self, df, current_index):
        """
        判断是否应该平多

        条件:
        1. 死叉
        2. 或触发止损/止盈

        Args:
            df: K线数据
            current_index: 当前索引

        Returns:
            bool: 是否平多
        """
        if current_index < self.ma_long_period:
            return False

        # 检查死叉
        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        ma_short_current = current.get('ma_short', None)
        ma_long_current = current.get('ma_long', None)
        ma_short_prev = previous.get('ma_short', None)
        ma_long_prev = previous.get('ma_long', None)

        if any(x is None for x in [ma_short_current, ma_long_current, ma_short_prev, ma_long_prev]):
            return False

        death_cross = (ma_short_prev >= ma_long_prev) and (ma_short_current < ma_long_current)

        if death_cross:
            logger.info(f"Exit long signal - Death cross at index {current_index}")
            return True

        return False

    def should_exit_short(self, df, current_index):
        """
        判断是否应该平空

        条件:
        1. 金叉
        2. 或触发止损/止盈

        Args:
            df: K线数据
            current_index: 当前索引

        Returns:
            bool: 是否平空
        """
        if current_index < self.ma_long_period:
            return False

        # 检查金叉
        current = df.iloc[current_index]
        previous = df.iloc[current_index - 1]

        ma_short_current = current.get('ma_short', None)
        ma_long_current = current.get('ma_long', None)
        ma_short_prev = previous.get('ma_short', None)
        ma_long_prev = previous.get('ma_long', None)

        if any(x is None for x in [ma_short_current, ma_long_current, ma_short_prev, ma_long_prev]):
            return False

        golden_cross = (ma_short_prev <= ma_long_prev) and (ma_short_current > ma_long_current)

        if golden_cross:
            logger.info(f"Exit short signal - Golden cross at index {current_index}")
            return True

        return False
