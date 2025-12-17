"""
网格交易策略 - 震荡市场的量化交易策略
适用于横盘震荡行情，低买高卖
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging
import numpy as np

logger = logging.getLogger(__name__)


class GridTradingStrategy(BaseStrategy):
    """
    网格交易策略

    策略逻辑：
    - 在价格区间内设置多个网格线
    - 价格下跌到网格线时买入
    - 价格上涨到网格线时卖出
    - 持续低买高卖，赚取震荡利润

    适用场景：
    - 横盘震荡市场
    - 波动率较高的交易对
    - 不适合单边趋势市场

    参数说明：
    - grid_num: 网格数量 (默认10)
    - price_range: 价格区间百分比 (默认0.2，即±20%)
    - grid_mode: 'arithmetic' 或 'geometric' (默认'arithmetic')
    - rebalance_threshold: 网格重置阈值 (默认0.3，即价格偏离30%时重置网格)
    """

    def __init__(self, config):
        super().__init__(config)
        self.grid_num = self.params.get('grid_num', 10)
        self.price_range = self.params.get('price_range', 0.2)
        self.grid_mode = self.params.get('grid_mode', 'arithmetic')
        self.rebalance_threshold = self.params.get('rebalance_threshold', 0.3)

        # 网格参数
        self.grid_prices = []
        self.base_price = None
        self.grid_positions = {}  # 记录每个网格的持仓

        logger.info(f"Grid Trading Strategy initialized - Grids: {self.grid_num}, "
                   f"Range: {self.price_range*100}%, Mode: {self.grid_mode}")

    def calculate_signals(self, df):
        """计算网格线和交易信号"""
        # 计算基准价格（使用近期平均价）
        if self.base_price is None or self._should_rebalance(df):
            self.base_price = df['close'].iloc[-50:].mean()
            self._setup_grid()

        # 标记当前价格所在的网格
        df['current_grid'] = df['close'].apply(self._get_grid_level)

        # 计算价格在网格中的位置
        df['grid_position'] = df.apply(
            lambda row: self._calculate_grid_position(row['close']), axis=1
        )

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：
        价格下跌触及下方网格线时买入
        """
        if current_index < 1 or not self.grid_prices:
            return False

        current_price = df.iloc[current_index]['close']
        previous_price = df.iloc[current_index - 1]['close']

        # 找到当前价格穿越的网格线
        crossed_grid = self._get_crossed_grid(previous_price, current_price, direction='down')

        if crossed_grid is not None:
            # 检查该网格是否已经有持仓
            if not self._has_position_at_grid(crossed_grid):
                logger.info(f"Long signal: Price crossed down to grid {crossed_grid} at {current_price:.2f}")
                return True

        return False

    def should_enter_short(self, df, current_index):
        """
        做空条件：
        价格上涨触及上方网格线时卖出（平多或做空）
        """
        if current_index < 1 or not self.grid_prices:
            return False

        current_price = df.iloc[current_index]['close']
        previous_price = df.iloc[current_index - 1]['close']

        # 找到当前价格穿越的网格线
        crossed_grid = self._get_crossed_grid(previous_price, current_price, direction='up')

        if crossed_grid is not None:
            # 在网格交易中，通常不做空，只是卖出多单
            # 如果需要做空，可以在这里实现
            logger.info(f"Short signal: Price crossed up to grid {crossed_grid} at {current_price:.2f}")
            return False  # 网格策略通常只做多，不做空

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        价格上涨触及上方网格线时平仓
        """
        if current_index < 1 or not self.grid_prices:
            return False

        current_price = df.iloc[current_index]['close']
        previous_price = df.iloc[current_index - 1]['close']

        # 找到当前价格穿越的网格线
        crossed_grid = self._get_crossed_grid(previous_price, current_price, direction='up')

        if crossed_grid is not None and self.position == 'LONG':
            # 计算盈利
            if self.entry_price > 0:
                profit_pct = (current_price - self.entry_price) / self.entry_price
                if profit_pct > 0.01:  # 至少1%的利润
                    logger.info(f"Exit long: Price crossed up to grid {crossed_grid}, profit: {profit_pct:.2%}")
                    return True

        return False

    def should_exit_short(self, df, current_index):
        """
        平空条件：
        价格下跌触及下方网格线时平仓
        """
        if current_index < 1 or not self.grid_prices:
            return False

        current_price = df.iloc[current_index]['close']
        previous_price = df.iloc[current_index - 1]['close']

        # 找到当前价格穿越的网格线
        crossed_grid = self._get_crossed_grid(previous_price, current_price, direction='down')

        if crossed_grid is not None and self.position == 'SHORT':
            # 计算盈利
            if self.entry_price > 0:
                profit_pct = (self.entry_price - current_price) / self.entry_price
                if profit_pct > 0.01:
                    logger.info(f"Exit short: Price crossed down to grid {crossed_grid}, profit: {profit_pct:.2%}")
                    return True

        return False

    def _setup_grid(self):
        """设置网格线"""
        if self.base_price is None:
            return

        upper_price = self.base_price * (1 + self.price_range)
        lower_price = self.base_price * (1 - self.price_range)

        if self.grid_mode == 'arithmetic':
            # 等差网格
            self.grid_prices = np.linspace(lower_price, upper_price, self.grid_num + 1)
        else:
            # 等比网格（对数网格）
            self.grid_prices = np.geomspace(lower_price, upper_price, self.grid_num + 1)

        logger.info(f"Grid setup: Base={self.base_price:.2f}, "
                   f"Range=[{lower_price:.2f}, {upper_price:.2f}], "
                   f"Grids={len(self.grid_prices)}")

    def _should_rebalance(self, df):
        """判断是否需要重新设置网格"""
        if self.base_price is None:
            return True

        current_price = df['close'].iloc[-1]
        deviation = abs(current_price - self.base_price) / self.base_price

        if deviation > self.rebalance_threshold:
            logger.info(f"Rebalancing grid: deviation {deviation:.2%} exceeds threshold")
            return True

        return False

    def _get_grid_level(self, price):
        """获取价格所在的网格层级"""
        if not self.grid_prices:
            return None

        for i, grid_price in enumerate(self.grid_prices):
            if price <= grid_price:
                return i

        return len(self.grid_prices) - 1

    def _get_crossed_grid(self, prev_price, curr_price, direction='down'):
        """
        检测价格穿越了哪条网格线

        Args:
            prev_price: 前一个价格
            curr_price: 当前价格
            direction: 'up' 或 'down'

        Returns:
            穿越的网格索引，如果没有穿越返回None
        """
        if not self.grid_prices:
            return None

        if direction == 'down':
            # 价格下跌，检查是否穿越了某条网格线（从上往下）
            for i, grid_price in enumerate(self.grid_prices):
                if prev_price > grid_price >= curr_price:
                    return i
        else:
            # 价格上涨，检查是否穿越了某条网格线（从下往上）
            for i, grid_price in enumerate(self.grid_prices):
                if prev_price < grid_price <= curr_price:
                    return i

        return None

    def _calculate_grid_position(self, price):
        """
        计算价格在网格中的相对位置（0-1之间）

        Returns:
            float: 0表示在最低网格，1表示在最高网格
        """
        if not self.grid_prices or len(self.grid_prices) < 2:
            return 0.5

        min_price = self.grid_prices[0]
        max_price = self.grid_prices[-1]

        if max_price == min_price:
            return 0.5

        position = (price - min_price) / (max_price - min_price)
        return max(0, min(1, position))

    def _has_position_at_grid(self, grid_level):
        """检查某个网格是否已有持仓"""
        return grid_level in self.grid_positions

    def update_position(self, position_type, price, size=0):
        """
        更新持仓信息（重写父类方法以跟踪网格持仓）
        """
        super().update_position(position_type, price, size)

        if position_type == 'LONG' and self.grid_prices:
            # 记录在哪个网格开仓
            grid_level = self._get_grid_level(price)
            if grid_level is not None:
                self.grid_positions[grid_level] = {
                    'price': price,
                    'size': size
                }
        elif position_type is None:
            # 平仓时清除网格记录
            if self.entry_price and self.grid_prices:
                grid_level = self._get_grid_level(self.entry_price)
                if grid_level in self.grid_positions:
                    del self.grid_positions[grid_level]

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.grid_prices = []
        self.base_price = None
        self.grid_positions = {}
        logger.info("Grid strategy reset")
