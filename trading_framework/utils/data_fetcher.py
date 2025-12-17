"""
数据获取模块 - 使用 python-binance 获取市场数据
"""
import pandas as pd
from binance.client import Client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataFetcher:
    """币安数据获取器"""

    def __init__(self, api_key=None, api_secret=None, testnet=False, proxy=None, timeout=30):
        """
        初始化数据获取器

        Args:
            api_key: API密钥 (获取公开数据时可为None)
            api_secret: API密钥 (获取公开数据时可为None)
            testnet: 是否使用测试网
            proxy: 代理地址，如 'http://127.0.0.1:7890' (可选)
            timeout: 连接超时时间(秒)，默认30秒
        """
        # 构建请求参数
        requests_params = {'timeout': timeout}

        # 如果提供了代理，添加到请求参数
        if proxy:
            requests_params['proxies'] = {
                'http': proxy,
                'https': proxy
            }
            logger.info(f"Using proxy: {proxy}")

        self.client = Client(
            api_key,
            api_secret,
            testnet=testnet,
            requests_params=requests_params
        )
        logger.info(f"DataFetcher initialized (testnet={testnet}, timeout={timeout}s)")

    def get_historical_klines(self, symbol, interval, start_str, end_str=None, limit=1000):
        """
        获取历史K线数据

        Args:
            symbol: 交易对，如 'BTCUSDT'
            interval: K线周期，如 '1h', '4h', '1d'
            start_str: 开始时间，如 '2024-01-01' 或 '1 month ago UTC'
            end_str: 结束时间 (可选)
            limit: 最大返回数量

        Returns:
            pandas.DataFrame: K线数据
        """
        try:
            logger.info(f"Fetching historical klines: {symbol} {interval} from {start_str}")

            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )

            df = self._klines_to_dataframe(klines)
            logger.info(f"Successfully fetched {len(df)} klines")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical klines: {e}")
            raise

    def get_futures_klines(self, symbol, interval, start_str=None, end_str=None, limit=500):
        """
        获取期货历史K线数据

        Args:
            symbol: 交易对
            interval: K线周期
            start_str: 开始时间 (可选)
            end_str: 结束时间 (可选)
            limit: 最大返回数量

        Returns:
            pandas.DataFrame: K线数据
        """
        try:
            logger.info(f"Fetching futures klines: {symbol} {interval}")

            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }

            if start_str:
                params['startTime'] = self._date_to_timestamp(start_str)
            if end_str:
                params['endTime'] = self._date_to_timestamp(end_str)

            klines = self.client.futures_klines(**params)
            df = self._klines_to_dataframe(klines)

            logger.info(f"Successfully fetched {len(df)} futures klines")
            return df

        except Exception as e:
            logger.error(f"Error fetching futures klines: {e}")
            raise

    def get_current_price(self, symbol):
        """
        获取当前价格

        Args:
            symbol: 交易对

        Returns:
            float: 当前价格
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            raise

    def get_futures_current_price(self, symbol):
        """
        获取期货当前价格

        Args:
            symbol: 交易对

        Returns:
            float: 当前价格
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching futures price: {e}")
            raise

    def get_account_balance(self):
        """
        获取账户余额

        Returns:
            dict: 账户余额信息
        """
        try:
            account = self.client.get_account()
            balances = {}
            for balance in account['balances']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    balances[balance['asset']] = {
                        'free': float(balance['free']),
                        'locked': float(balance['locked']),
                        'total': float(balance['free']) + float(balance['locked'])
                    }
            return balances
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            raise

    def get_futures_account_balance(self):
        """
        获取期货账户余额

        Returns:
            dict: 账户余额信息
        """
        try:
            account = self.client.futures_account()
            balances = {}
            for balance in account['assets']:
                if float(balance['availableBalance']) > 0:
                    balances[balance['asset']] = {
                        'available': float(balance['availableBalance']),
                        'balance': float(balance['walletBalance']),
                        'unrealized_pnl': float(balance['unrealizedProfit'])
                    }
            return balances
        except Exception as e:
            logger.error(f"Error fetching futures balance: {e}")
            raise

    def get_futures_position(self, symbol=None):
        """
        获取期货持仓信息

        Args:
            symbol: 交易对 (可选，为None时返回所有持仓)

        Returns:
            list or dict: 持仓信息
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)

            # 过滤出有持仓的
            active_positions = []
            for pos in positions:
                if float(pos['positionAmt']) != 0:
                    active_positions.append({
                        'symbol': pos['symbol'],
                        'position_amt': float(pos['positionAmt']),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unRealizedProfit']),
                        'leverage': int(pos['leverage']),
                        'position_side': pos['positionSide']
                    })

            return active_positions if symbol is None else (active_positions[0] if active_positions else None)

        except Exception as e:
            logger.error(f"Error fetching position: {e}")
            raise

    def _klines_to_dataframe(self, klines):
        """
        将K线数据转换为DataFrame

        Args:
            klines: K线原始数据

        Returns:
            pandas.DataFrame: 格式化的K线数据
        """
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        # 转换数据类型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        numeric_columns = ['open', 'high', 'low', 'close', 'volume',
                          'quote_volume', 'taker_buy_base', 'taker_buy_quote']
        df[numeric_columns] = df[numeric_columns].astype(float)
        df['trades'] = df['trades'].astype(int)

        # 设置索引
        df.set_index('timestamp', inplace=True)

        return df

    def _date_to_timestamp(self, date_str):
        """
        将日期字符串转换为时间戳(毫秒)

        Args:
            date_str: 日期字符串

        Returns:
            int: 时间戳(毫秒)
        """
        if isinstance(date_str, str):
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return int(dt.timestamp() * 1000)
        return date_str
