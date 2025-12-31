"""
策略加载器 - 动态加载策略
"""
import logging

logger = logging.getLogger(__name__)


def load_strategy(config):
    """
    根据配置动态加载策略

    Args:
        config: 策略配置字典，包含 name 和 params

    Returns:
        策略实例

    Raises:
        ValueError: 如果策略名称未知
        ImportError: 如果策略导入失败
    """
    strategy_name = config.get('name', 'ma_crossover')

    # 策略映射
    strategy_map = {
        'ma_crossover': ('strategies.ma_crossover_strategy', 'MACrossoverStrategy'),
        'rsi': ('strategies.rsi_strategy', 'RSIStrategy'),
        'bollinger_bands': ('strategies.bollinger_bands_strategy', 'BollingerBandsStrategy'),
        'grid_trading': ('strategies.grid_trading_strategy', 'GridTradingStrategy'),
        'macd': ('strategies.macd_strategy', 'MACDStrategy'),
        'breakout_pullback': ('strategies.breakout_pullback_strategy', 'BreakoutPullbackStrategy'),
        'momentum_dip_buying': ('strategies.momentum_dip_buying_strategy', 'MomentumDipBuyingStrategy')
    }

    if strategy_name not in strategy_map:
        available = ', '.join(strategy_map.keys())
        raise ValueError(f"未知策略: '{strategy_name}'. 可用策略: {available}")

    module_name, class_name = strategy_map[strategy_name]

    try:
        # 动态导入策略模块
        if strategy_name == 'ma_crossover':
            from strategies.ma_crossover_strategy import MACrossoverStrategy as StrategyClass
        elif strategy_name == 'rsi':
            from strategies.rsi_strategy import RSIStrategy as StrategyClass
        elif strategy_name == 'bollinger_bands':
            from strategies.bollinger_bands_strategy import BollingerBandsStrategy as StrategyClass
        elif strategy_name == 'grid_trading':
            from strategies.grid_trading_strategy import GridTradingStrategy as StrategyClass
        elif strategy_name == 'macd':
            from strategies.macd_strategy import MACDStrategy as StrategyClass
        elif strategy_name == 'breakout_pullback':
            from strategies.breakout_pullback_strategy import BreakoutPullbackStrategy as StrategyClass
        elif strategy_name == 'momentum_dip_buying':
            from strategies.momentum_dip_buying_strategy import MomentumDipBuyingStrategy as StrategyClass

        # 创建策略实例
        strategy = StrategyClass(config)
        logger.info(f"Strategy loaded: {class_name}")
        return strategy

    except ImportError as e:
        logger.error(f"Failed to import strategy '{strategy_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize strategy '{strategy_name}': {e}")
        raise
