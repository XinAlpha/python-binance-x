"""
策略基类 - 所有策略都应继承此类
"""
from abc import ABC, abstractmethod
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, config):
        """
        初始化策略

        Args:
            config: 策略配置字典
        """
        self.config = config
        self.name = config.get('name', 'base_strategy')
        self.params = config.get('params', {})
        self.position = None  # 当前持仓: None, 'LONG', 'SHORT'
        self.entry_price = 0  # 入场价格
        self.position_size = 0  # 持仓数量
        logger.info(f"Strategy '{self.name}' initialized with params: {self.params}")

    @abstractmethod
    def calculate_signals(self, df):
        """
        计算交易信号 (需要子类实现)

        Args:
            df: 包含价格和指标的DataFrame

        Returns:
            str: 'BUY', 'SELL', 'CLOSE_LONG', 'CLOSE_SHORT', 'HOLD'
        """
        pass

    @abstractmethod
    def should_enter_long(self, df, current_index):
        """
        判断是否应该做多 (需要子类实现)

        Args:
            df: K线数据
            current_index: 当前索引位置

        Returns:
            bool: 是否做多
        """
        pass

    @abstractmethod
    def should_enter_short(self, df, current_index):
        """
        判断是否应该做空 (需要子类实现)

        Args:
            df: K线数据
            current_index: 当前索引位置

        Returns:
            bool: 是否做空
        """
        pass

    @abstractmethod
    def should_exit_long(self, df, current_index):
        """
        判断是否应该平多 (需要子类实现)

        Args:
            df: K线数据
            current_index: 当前索引位置

        Returns:
            bool: 是否平多
        """
        pass

    @abstractmethod
    def should_exit_short(self, df, current_index):
        """
        判断是否应该平空 (需要子类实现)

        Args:
            df: K线数据
            current_index: 当前索引位置

        Returns:
            bool: 是否平空
        """
        pass

    def check_stop_loss(self, current_price):
        """
        检查止损

        Args:
            current_price: 当前价格

        Returns:
            bool: 是否触发止损
        """
        if self.position is None or self.entry_price == 0:
            return False

        stop_loss_pct = self.params.get('stop_loss', 0.02)

        if self.position == 'LONG':
            loss_pct = (self.entry_price - current_price) / self.entry_price
            if loss_pct >= stop_loss_pct:
                logger.warning(f"Stop loss triggered! Loss: {loss_pct:.2%}")
                return True

        elif self.position == 'SHORT':
            loss_pct = (current_price - self.entry_price) / self.entry_price
            if loss_pct >= stop_loss_pct:
                logger.warning(f"Stop loss triggered! Loss: {loss_pct:.2%}")
                return True

        return False

    def check_take_profit(self, current_price):
        """
        检查止盈

        Args:
            current_price: 当前价格

        Returns:
            bool: 是否触发止盈
        """
        if self.position is None or self.entry_price == 0:
            return False

        take_profit_pct = self.params.get('take_profit', 0.04)

        if self.position == 'LONG':
            profit_pct = (current_price - self.entry_price) / self.entry_price
            if profit_pct >= take_profit_pct:
                logger.info(f"Take profit triggered! Profit: {profit_pct:.2%}")
                return True

        elif self.position == 'SHORT':
            profit_pct = (self.entry_price - current_price) / self.entry_price
            if profit_pct >= take_profit_pct:
                logger.info(f"Take profit triggered! Profit: {profit_pct:.2%}")
                return True

        return False

    def update_position(self, position_type, price, size=0):
        """
        更新持仓信息

        Args:
            position_type: 'LONG', 'SHORT', None
            price: 入场价格
            size: 持仓数量
        """
        self.position = position_type
        self.entry_price = price
        self.position_size = size

        if position_type:
            logger.info(f"Position updated: {position_type} at {price}, size: {size}")
        else:
            logger.info("Position closed")

    def calculate_position_size(self, capital, price, risk_pct=None):
        """
        计算仓位大小

        Args:
            capital: 可用资金
            price: 当前价格
            risk_pct: 风险比例 (可选，默认从配置读取)

        Returns:
            float: 仓位数量
        """
        if risk_pct is None:
            risk_pct = self.params.get('max_position_size', 0.5)

        position_value = capital * risk_pct
        size = position_value / price

        logger.debug(f"Calculated position size: {size} (risk: {risk_pct:.2%})")
        return size

    def get_current_signal(self, df):
        """
        获取当前交易信号 (用于回测和实盘)

        Args:
            df: K线数据DataFrame

        Returns:
            str: 交易信号
        """
        current_index = len(df) - 1
        current_price = df['close'].iloc[-1]

        # 检查止损止盈
        if self.check_stop_loss(current_price):
            return 'CLOSE_LONG' if self.position == 'LONG' else 'CLOSE_SHORT'

        if self.check_take_profit(current_price):
            return 'CLOSE_LONG' if self.position == 'LONG' else 'CLOSE_SHORT'

        # 检查开仓信号
        if self.position is None:
            if self.should_enter_long(df, current_index):
                return 'BUY'
            elif self.should_enter_short(df, current_index):
                return 'SELL'

        # 检查平仓信号
        elif self.position == 'LONG':
            if self.should_exit_long(df, current_index):
                return 'CLOSE_LONG'

        elif self.position == 'SHORT':
            if self.should_exit_short(df, current_index):
                return 'CLOSE_SHORT'

        return 'HOLD'

    def reset(self):
        """重置策略状态 (用于回测)"""
        self.position = None
        self.entry_price = 0
        self.position_size = 0
        logger.info(f"Strategy '{self.name}' reset")
