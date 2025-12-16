"""
实盘交易执行器 - 用于实盘/模拟交易
"""
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging

logger = logging.getLogger(__name__)


class LiveExecutor:
    """实盘交易执行器"""

    def __init__(self, strategy, config, data_fetcher):
        """
        初始化实盘执行器

        Args:
            strategy: 策略实例
            config: 配置字典
            data_fetcher: 数据获取器实例
        """
        self.strategy = strategy
        self.config = config
        self.data_fetcher = data_fetcher

        # 交易配置
        self.symbol = config['trading']['symbol']
        self.interval = config['trading']['interval']
        self.check_interval = config['live_trading']['check_interval']
        self.max_retries = config['live_trading']['max_retries']

        # Binance客户端
        self.client = Client(
            api_key=config['api']['api_key'],
            api_secret=config['api']['api_secret'],
            testnet=config['api']['testnet']
        )

        # 设置杠杆
        leverage = config['trading']['leverage']
        try:
            self.client.futures_change_leverage(symbol=self.symbol, leverage=leverage)
            logger.info(f"Leverage set to {leverage}x for {self.symbol}")
        except Exception as e:
            logger.error(f"Failed to set leverage: {e}")

        # 状态
        self.is_running = False

        logger.info(f"Live executor initialized - Symbol: {self.symbol}, Interval: {self.interval}")

    def start(self):
        """启动实盘交易"""
        logger.info("Starting live trading...")
        self.is_running = True

        try:
            while self.is_running:
                self._trading_loop()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Live trading interrupted by user")
            self.stop()

        except Exception as e:
            logger.error(f"Error in live trading: {e}")
            self.stop()

    def stop(self):
        """停止实盘交易"""
        logger.info("Stopping live trading...")
        self.is_running = False

    def _trading_loop(self):
        """交易主循环"""
        try:
            # 获取最新数据
            df = self.data_fetcher.get_futures_klines(
                symbol=self.symbol,
                interval=self.interval,
                limit=200
            )

            # 计算指标和信号
            df = self.strategy.calculate_signals(df)

            # 获取当前价格
            current_price = df['close'].iloc[-1]

            # 获取当前持仓
            current_position = self._get_current_position()

            # 更新策略持仓状态
            if current_position:
                self.strategy.update_position(
                    current_position['position_side'],
                    current_position['entry_price'],
                    current_position['position_amt']
                )
            else:
                self.strategy.update_position(None, 0, 0)

            # 获取交易信号
            signal = self.strategy.get_current_signal(df)

            logger.info(f"Current price: {current_price:.2f}, Signal: {signal}, Position: {self.strategy.position}")

            # 执行交易
            if signal == 'BUY' and not current_position:
                self._execute_long_entry(current_price)

            elif signal == 'SELL' and not current_position:
                self._execute_short_entry(current_price)

            elif signal == 'CLOSE_LONG' and current_position and current_position['position_side'] == 'LONG':
                self._execute_close_position()

            elif signal == 'CLOSE_SHORT' and current_position and current_position['position_side'] == 'SHORT':
                self._execute_close_position()

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")

    def _execute_long_entry(self, current_price):
        """执行做多开仓"""
        try:
            # 获取账户余额
            balance = self._get_available_balance()
            logger.info(f"Available balance: ${balance:.2f}")

            # 计算仓位大小
            position_size = self.strategy.calculate_position_size(balance, current_price)

            # 调整精度
            position_size = self._adjust_quantity_precision(position_size)

            if position_size <= 0:
                logger.warning("Position size too small, skipping order")
                return

            logger.info(f"Placing LONG order - Size: {position_size}, Price: ~{current_price:.2f}")

            # 下单
            order = self.client.futures_create_order(
                symbol=self.symbol,
                side='BUY',
                type='MARKET',
                quantity=position_size,
                positionSide='LONG'
            )

            logger.info(f"LONG order executed: {order['orderId']}")

            # 更新策略状态
            self.strategy.update_position('LONG', current_price, position_size)

        except BinanceAPIException as e:
            logger.error(f"Binance API error in long entry: {e}")

        except Exception as e:
            logger.error(f"Error in long entry: {e}")

    def _execute_short_entry(self, current_price):
        """执行做空开仓"""
        try:
            # 获取账户余额
            balance = self._get_available_balance()
            logger.info(f"Available balance: ${balance:.2f}")

            # 计算仓位大小
            position_size = self.strategy.calculate_position_size(balance, current_price)

            # 调整精度
            position_size = self._adjust_quantity_precision(position_size)

            if position_size <= 0:
                logger.warning("Position size too small, skipping order")
                return

            logger.info(f"Placing SHORT order - Size: {position_size}, Price: ~{current_price:.2f}")

            # 下单
            order = self.client.futures_create_order(
                symbol=self.symbol,
                side='SELL',
                type='MARKET',
                quantity=position_size,
                positionSide='SHORT'
            )

            logger.info(f"SHORT order executed: {order['orderId']}")

            # 更新策略状态
            self.strategy.update_position('SHORT', current_price, position_size)

        except BinanceAPIException as e:
            logger.error(f"Binance API error in short entry: {e}")

        except Exception as e:
            logger.error(f"Error in short entry: {e}")

    def _execute_close_position(self):
        """执行平仓"""
        try:
            # 获取当前持仓
            position = self._get_current_position()

            if not position:
                logger.warning("No position to close")
                return

            position_amt = abs(position['position_amt'])
            position_side = position['position_side']

            logger.info(f"Closing {position_side} position - Size: {position_amt}")

            # 平仓订单
            if position_side == 'LONG':
                order = self.client.futures_create_order(
                    symbol=self.symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=position_amt,
                    positionSide='LONG'
                )
            else:  # SHORT
                order = self.client.futures_create_order(
                    symbol=self.symbol,
                    side='BUY',
                    type='MARKET',
                    quantity=position_amt,
                    positionSide='SHORT'
                )

            logger.info(f"Position closed: {order['orderId']}")

            # 更新策略状态
            self.strategy.update_position(None, 0, 0)

        except BinanceAPIException as e:
            logger.error(f"Binance API error in close position: {e}")

        except Exception as e:
            logger.error(f"Error in close position: {e}")

    def _get_current_position(self):
        """
        获取当前持仓

        Returns:
            dict or None: 持仓信息
        """
        try:
            positions = self.client.futures_position_information(symbol=self.symbol)

            for pos in positions:
                position_amt = float(pos['positionAmt'])
                if position_amt != 0:
                    return {
                        'symbol': pos['symbol'],
                        'position_amt': abs(position_amt),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unRealizedProfit']),
                        'position_side': pos['positionSide']
                    }

            return None

        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None

    def _get_available_balance(self):
        """
        获取可用余额

        Returns:
            float: 可用余额(USDT)
        """
        try:
            account = self.client.futures_account()
            for asset in account['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['availableBalance'])
            return 0

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0

    def _adjust_quantity_precision(self, quantity):
        """
        调整数量精度以符合交易所要求

        Args:
            quantity: 原始数量

        Returns:
            float: 调整后的数量
        """
        try:
            # 获取交易对信息
            exchange_info = self.client.futures_exchange_info()

            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == self.symbol:
                    # 获取LOT_SIZE过滤器
                    for filter_item in symbol_info['filters']:
                        if filter_item['filterType'] == 'LOT_SIZE':
                            step_size = float(filter_item['stepSize'])
                            min_qty = float(filter_item['minQty'])

                            # 调整到步长的倍数
                            quantity = round(quantity / step_size) * step_size

                            # 确保大于最小数量
                            if quantity < min_qty:
                                quantity = 0

                            # 格式化精度
                            precision = len(str(step_size).rstrip('0').split('.')[-1])
                            quantity = round(quantity, precision)

                            return quantity

            return quantity

        except Exception as e:
            logger.error(f"Error adjusting quantity precision: {e}")
            return quantity

    def get_account_status(self):
        """
        获取账户状态

        Returns:
            dict: 账户状态信息
        """
        try:
            balance = self._get_available_balance()
            position = self._get_current_position()
            current_price = self.data_fetcher.get_futures_current_price(self.symbol)

            status = {
                'balance': balance,
                'position': position,
                'current_price': current_price
            }

            return status

        except Exception as e:
            logger.error(f"Error getting account status: {e}")
            return None
