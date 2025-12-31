"""
动量回踩加仓策略 (Momentum Dip Buying Strategy)

策略逻辑：
1. 如果5分钟涨幅大于5% → 2倍杠杆半仓做多
2. 做多后下跌超3% → 用剩余半仓继续做多（加仓）
3. 加仓后再次下跌超3% → 全部止损
4. 做多后上涨5% → 止盈平仓

适用场景：
- 强势上涨行情
- 高波动市场
- 需要快速反应

风险等级：高
建议K线周期：5m（必须）
"""
from .base_strategy import BaseStrategy
from utils.indicators import Indicators
import logging
import numpy as np

logger = logging.getLogger(__name__)


class MomentumDipBuyingStrategy(BaseStrategy):
    """
    动量回踩加仓策略

    入场条件：
    - 5分钟涨幅 > 5% (可配置)
    - 使用50%仓位做多，2倍杠杆

    加仓条件：
    - 首次做多后，价格回调 > 3% (可配置)
    - 使用剩余50%仓位加仓

    止损条件：
    - 加仓后再次下跌 > 3%

    止盈条件：
    - 做多后上涨 > 5% (可配置)

    参数说明：
    - pump_threshold: 快速涨幅阈值 (默认0.05，即5%)
    - dip_threshold: 回调阈值 (默认0.03，即3%)
    - profit_target: 止盈目标 (默认0.05，即5%)
    - position_1_ratio: 首次开仓比例 (默认0.5，即50%)
    - leverage_multiplier: 杠杆倍数 (默认2)
    """

    def __init__(self, config):
        super().__init__(config)

        # 策略参数
        self.pump_threshold = self.params.get('pump_threshold', 0.05)  # 5%快速涨幅
        self.dip_threshold = self.params.get('dip_threshold', 0.03)    # 3%回调
        self.profit_target = self.params.get('profit_target', 0.05)    # 5%止盈
        self.position_1_ratio = self.params.get('position_1_ratio', 0.5)  # 首仓50%
        self.leverage_multiplier = self.params.get('leverage_multiplier', 2)  # 2倍杠杆

        # 状态变量
        self.first_entry_price = 0      # 首次入场价格
        self.first_position_size = 0    # 首次仓位大小
        self.second_entry_price = 0     # 加仓价格
        self.second_position_size = 0   # 加仓大小
        self.has_added_position = False # 是否已加仓
        self.avg_entry_price = 0        # 平均持仓成本

        # 用于检测快速上涨
        self.pump_detected = False
        self.pump_start_price = 0

        logger.info(f"Momentum Dip Buying Strategy initialized - "
                   f"Pump: {self.pump_threshold*100}%, "
                   f"Dip: {self.dip_threshold*100}%, "
                   f"Profit: {self.profit_target*100}%")

    def calculate_signals(self, df):
        """计算交易信号"""
        # 计算5分钟价格变化
        df['price_change_5m'] = df['close'].pct_change(5)

        # 计算1分钟价格变化（用于快速检测）
        df['price_change_1m'] = df['close'].pct_change(1)

        # 计算成交量（用于确认）
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_spike'] = df['volume'] > df['volume_ma'] * 1.5

        # 计算波动率（ATR）
        df['atr'] = Indicators.atr(df['high'], df['low'], df['close'], period=14)

        return df

    def should_enter_long(self, df, current_index):
        """
        做多条件：5分钟涨幅超过阈值
        """
        if current_index < 10:
            return False

        # 如果已经持仓，不再入场
        if self.position is not None:
            return False

        current = df.iloc[current_index]

        # 检测5分钟涨幅
        price_change_5m = current.get('price_change_5m', 0)

        # 确认成交量配合
        volume_confirmed = current.get('volume_spike', False)

        # 快速涨幅超过阈值
        if price_change_5m > self.pump_threshold:
            # 最好有成交量确认，但不强制
            logger.info(f"Pump detected! 5m change: {price_change_5m:.2%}, "
                       f"Volume spike: {volume_confirmed}")
            return True

        return False

    def should_exit_long(self, df, current_index):
        """
        平多条件：
        1. 止盈：上涨5%
        2. 止损：加仓后再次下跌3%
        """
        if current_index < 5 or self.position != 'LONG':
            return False

        current = df.iloc[current_index]
        current_price = current['close']

        # 计算平均持仓成本
        if self.has_added_position:
            # 已加仓，使用平均成本
            avg_price = self.avg_entry_price
        else:
            # 未加仓，使用首次入场价
            avg_price = self.first_entry_price

        if avg_price <= 0:
            return False

        # 计算收益
        profit_pct = (current_price - avg_price) / avg_price

        # 止盈条件：上涨5%
        if profit_pct >= self.profit_target:
            logger.info(f"Take profit! Profit: {profit_pct:.2%} at price {current_price:.2f}")
            return True

        # 止损条件：加仓后再次下跌3%
        if self.has_added_position:
            # 从加仓价格算起的跌幅
            dip_from_second = (self.second_entry_price - current_price) / self.second_entry_price

            if dip_from_second > self.dip_threshold:
                logger.info(f"Stop loss! Dip from 2nd entry: {dip_from_second:.2%} "
                           f"at price {current_price:.2f}")
                return True

        return False

    def should_enter_short(self, df, current_index):
        """
        本策略不做空
        """
        return False

    def should_exit_short(self, df, current_index):
        """
        本策略不做空
        """
        return False

    def get_current_signal(self, df):
        """
        获取当前交易信号（增强版，支持加仓逻辑）
        """
        if len(df) == 0:
            return 'HOLD'

        current_index = len(df) - 1
        df = self.calculate_signals(df)
        current = df.iloc[current_index]
        current_price = current['close']

        # 如果没有持仓
        if self.position is None:
            if self.should_enter_long(df, current_index):
                return 'BUY'
            elif self.should_enter_short(df, current_index):
                return 'SELL'

        # 如果持多仓
        elif self.position == 'LONG':
            # 检查是否需要加仓
            if not self.has_added_position and self.first_entry_price > 0:
                dip_from_first = (self.first_entry_price - current_price) / self.first_entry_price

                # 回调超过3%，加仓
                if dip_from_first > self.dip_threshold:
                    logger.info(f"Add position! Dip from 1st entry: {dip_from_first:.2%} "
                               f"at price {current_price:.2f}")
                    return 'ADD_LONG'  # 自定义信号：加仓

            # 检查是否需要平仓
            if self.should_exit_long(df, current_index):
                return 'CLOSE_LONG'

        # 如果持空仓
        elif self.position == 'SHORT':
            if self.should_exit_short(df, current_index):
                return 'CLOSE_SHORT'

        return 'HOLD'

    def calculate_position_size(self, balance, current_price):
        """
        计算仓位大小

        首次开仓：使用50%资金，2倍杠杆
        加仓：使用剩余50%资金，2倍杠杆
        """
        if not self.has_added_position:
            # 首次开仓：50%资金 × 2倍杠杆
            position_value = balance * self.position_1_ratio * self.leverage_multiplier
        else:
            # 加仓：剩余50%资金 × 2倍杠杆
            position_value = balance * (1 - self.position_1_ratio) * self.leverage_multiplier

        position_size = position_value / current_price

        logger.info(f"Position size calculated: {position_size:.6f} "
                   f"(Value: ${position_value:.2f}, Price: {current_price:.2f})")

        return position_size

    def update_position(self, position_type, entry_price, position_size):
        """
        更新持仓状态（重写以支持加仓逻辑）
        """
        # 如果是首次开仓
        if self.position is None and position_type == 'LONG':
            self.position = position_type
            self.entry_price = entry_price
            self.first_entry_price = entry_price
            self.first_position_size = position_size
            self.position_size = position_size
            self.has_added_position = False

            logger.info(f"First position opened: {position_type} at {entry_price:.2f}, "
                       f"size: {position_size:.6f}")

        # 如果是加仓
        elif self.position == 'LONG' and not self.has_added_position:
            self.second_entry_price = entry_price
            self.second_position_size = position_size
            self.has_added_position = True

            # 计算平均持仓成本
            total_value = (self.first_entry_price * self.first_position_size +
                          entry_price * position_size)
            total_size = self.first_position_size + position_size
            self.avg_entry_price = total_value / total_size
            self.position_size = total_size

            logger.info(f"Position added at {entry_price:.2f}, size: {position_size:.6f}, "
                       f"Avg price: {self.avg_entry_price:.2f}, Total size: {total_size:.6f}")

        # 如果是平仓
        elif position_type is None:
            logger.info(f"Position closed. Entry: {self.entry_price:.2f}, "
                       f"Avg: {self.avg_entry_price:.2f}")
            self.position = None
            self.entry_price = 0
            self.position_size = 0
            self.first_entry_price = 0
            self.first_position_size = 0
            self.second_entry_price = 0
            self.second_position_size = 0
            self.has_added_position = False
            self.avg_entry_price = 0

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.first_entry_price = 0
        self.first_position_size = 0
        self.second_entry_price = 0
        self.second_position_size = 0
        self.has_added_position = False
        self.avg_entry_price = 0
        self.pump_detected = False
        self.pump_start_price = 0
        logger.info("Momentum Dip Buying strategy reset")
