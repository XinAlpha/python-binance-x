"""
回测引擎 - 用于策略回测
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎"""

    def __init__(self, strategy, config):
        """
        初始化回测引擎

        Args:
            strategy: 策略实例
            config: 配置字典
        """
        self.strategy = strategy
        self.config = config

        # 回测配置
        self.initial_capital = config['trading']['initial_capital']
        self.commission = config['backtest']['commission']
        self.slippage = config['backtest']['slippage']

        # 回测状态
        self.capital = self.initial_capital
        self.position = None
        self.position_size = 0
        self.entry_price = 0

        # 交易记录
        self.trades = []
        self.equity_curve = []

        logger.info(f"Backtest engine initialized - Capital: ${self.initial_capital}")

    def run(self, df):
        """
        运行回测

        Args:
            df: K线数据DataFrame

        Returns:
            dict: 回测结果
        """
        logger.info("Starting backtest...")

        # 重置策略和状态
        self.strategy.reset()
        self.capital = self.initial_capital
        self.position = None
        self.position_size = 0
        self.entry_price = 0
        self.trades = []
        self.equity_curve = []

        # 计算技术指标
        df = self.strategy.calculate_signals(df)

        # 遍历每个时间点
        for i in range(len(df)):
            current = df.iloc[i]
            current_price = current['close']
            current_time = df.index[i]

            # 检查止损止盈
            if self.position:
                if self.strategy.check_stop_loss(current_price):
                    self._close_position(current_price, current_time, 'STOP_LOSS')
                    self.strategy.update_position(None, 0, 0)

                elif self.strategy.check_take_profit(current_price):
                    self._close_position(current_price, current_time, 'TAKE_PROFIT')
                    self.strategy.update_position(None, 0, 0)

            # 检查进场信号
            if self.position is None:
                if self.strategy.should_enter_long(df, i):
                    self._open_long(current_price, current_time)
                    self.strategy.update_position('LONG', current_price, self.position_size)

                elif self.strategy.should_enter_short(df, i):
                    self._open_short(current_price, current_time)
                    self.strategy.update_position('SHORT', current_price, self.position_size)

            # 检查出场信号
            elif self.position == 'LONG':
                if self.strategy.should_exit_long(df, i):
                    self._close_position(current_price, current_time, 'SIGNAL')
                    self.strategy.update_position(None, 0, 0)

            elif self.position == 'SHORT':
                if self.strategy.should_exit_short(df, i):
                    self._close_position(current_price, current_time, 'SIGNAL')
                    self.strategy.update_position(None, 0, 0)

            # 记录权益曲线
            equity = self._calculate_equity(current_price)
            self.equity_curve.append({
                'timestamp': current_time,
                'equity': equity,
                'position': self.position
            })

        # 如果还有持仓,平仓
        if self.position:
            final_price = df['close'].iloc[-1]
            final_time = df.index[-1]
            self._close_position(final_price, final_time, 'FINAL')

        # 计算回测结果
        results = self._calculate_results(df)

        logger.info("Backtest completed")
        return results

    def _open_long(self, price, time):
        """开多仓"""
        # 考虑滑点
        actual_price = price * (1 + self.slippage)

        # 计算仓位大小
        max_position_value = self.capital * self.config['trading']['max_position_size']
        self.position_size = max_position_value / actual_price

        # 计算成本(包括手续费)
        cost = self.position_size * actual_price
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost

        if total_cost > self.capital:
            logger.warning(f"Insufficient capital for long position")
            return

        self.capital -= total_cost
        self.position = 'LONG'
        self.entry_price = actual_price

        logger.info(f"Open LONG at {actual_price:.2f}, size: {self.position_size:.6f}, cost: ${total_cost:.2f}")

        self.trades.append({
            'entry_time': time,
            'entry_price': actual_price,
            'position_type': 'LONG',
            'size': self.position_size,
            'commission': commission_cost
        })

    def _open_short(self, price, time):
        """开空仓"""
        # 考虑滑点
        actual_price = price * (1 - self.slippage)

        # 计算仓位大小
        max_position_value = self.capital * self.config['trading']['max_position_size']
        self.position_size = max_position_value / actual_price

        # 计算收入(扣除手续费)
        proceeds = self.position_size * actual_price
        commission_cost = proceeds * self.commission
        net_proceeds = proceeds - commission_cost

        self.capital += net_proceeds
        self.position = 'SHORT'
        self.entry_price = actual_price

        logger.info(f"Open SHORT at {actual_price:.2f}, size: {self.position_size:.6f}, proceeds: ${net_proceeds:.2f}")

        self.trades.append({
            'entry_time': time,
            'entry_price': actual_price,
            'position_type': 'SHORT',
            'size': self.position_size,
            'commission': commission_cost
        })

    def _close_position(self, price, time, reason):
        """平仓"""
        if not self.position or not self.trades:
            return

        # 考虑滑点
        if self.position == 'LONG':
            actual_price = price * (1 - self.slippage)
            proceeds = self.position_size * actual_price
            commission_cost = proceeds * self.commission
            net_proceeds = proceeds - commission_cost
            self.capital += net_proceeds

        else:  # SHORT
            actual_price = price * (1 + self.slippage)
            cost = self.position_size * actual_price
            commission_cost = cost * self.commission
            total_cost = cost + commission_cost
            self.capital -= total_cost

        # 计算盈亏
        if self.position == 'LONG':
            pnl = (actual_price - self.entry_price) * self.position_size
        else:
            pnl = (self.entry_price - actual_price) * self.position_size

        pnl_pct = (pnl / (self.entry_price * self.position_size)) * 100

        logger.info(f"Close {self.position} at {actual_price:.2f}, PnL: ${pnl:.2f} ({pnl_pct:.2f}%), Reason: {reason}")

        # 更新最后一笔交易
        self.trades[-1].update({
            'exit_time': time,
            'exit_price': actual_price,
            'exit_reason': reason,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_commission': commission_cost
        })

        self.position = None
        self.position_size = 0
        self.entry_price = 0

    def _calculate_equity(self, current_price):
        """计算当前权益"""
        equity = self.capital

        if self.position == 'LONG':
            # 多仓未实现盈亏
            unrealized_pnl = (current_price - self.entry_price) * self.position_size
            equity += unrealized_pnl

        elif self.position == 'SHORT':
            # 空仓未实现盈亏
            unrealized_pnl = (self.entry_price - current_price) * self.position_size
            equity += unrealized_pnl

        return equity

    def _calculate_results(self, df):
        """计算回测结果指标"""
        # 基本统计
        total_trades = len([t for t in self.trades if 'exit_time' in t])
        winning_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in self.trades if t.get('pnl', 0) < 0])

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # 盈亏统计
        total_pnl = sum([t.get('pnl', 0) for t in self.trades])
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100

        avg_win = np.mean([t['pnl'] for t in self.trades if t.get('pnl', 0) > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([t['pnl'] for t in self.trades if t.get('pnl', 0) < 0]) if losing_trades > 0 else 0

        # 最大回撤
        equity_curve_df = pd.DataFrame(self.equity_curve)
        equity_curve_df['peak'] = equity_curve_df['equity'].cummax()
        equity_curve_df['drawdown'] = (equity_curve_df['equity'] - equity_curve_df['peak']) / equity_curve_df['peak']
        max_drawdown = equity_curve_df['drawdown'].min() * 100

        # 夏普比率 (假设无风险利率为0)
        equity_curve_df['returns'] = equity_curve_df['equity'].pct_change()
        sharpe_ratio = (equity_curve_df['returns'].mean() / equity_curve_df['returns'].std() * np.sqrt(252)) if equity_curve_df['returns'].std() > 0 else 0

        # 盈亏比
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        results = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': total_return,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

        return results

    def print_results(self, results):
        """打印回测结果"""
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS".center(60))
        print("=" * 60)
        print(f"\nInitial Capital:     ${results['initial_capital']:,.2f}")
        print(f"Final Capital:       ${results['final_capital']:,.2f}")
        print(f"Total Return:        {results['total_return']:.2f}%")
        print(f"Total PnL:           ${results['total_pnl']:,.2f}")
        print(f"\n{'─' * 60}")
        print(f"\nTotal Trades:        {results['total_trades']}")
        print(f"Winning Trades:      {results['winning_trades']}")
        print(f"Losing Trades:       {results['losing_trades']}")
        print(f"Win Rate:            {results['win_rate']:.2f}%")
        print(f"\n{'─' * 60}")
        print(f"\nAverage Win:         ${results['avg_win']:,.2f}")
        print(f"Average Loss:        ${results['avg_loss']:,.2f}")
        print(f"Profit Factor:       {results['profit_factor']:.2f}")
        print(f"\n{'─' * 60}")
        print(f"\nMax Drawdown:        {results['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio:        {results['sharpe_ratio']:.2f}")
        print(f"\n{'=' * 60}\n")

        # 打印交易明细
        if results['trades']:
            print("\nTRADE DETAILS:")
            print("-" * 120)
            print(f"{'Entry Time':<20} {'Exit Time':<20} {'Type':<6} {'Entry':<10} {'Exit':<10} {'PnL':<12} {'PnL%':<8} {'Reason':<12}")
            print("-" * 120)
            for trade in results['trades']:
                if 'exit_time' in trade:
                    print(f"{str(trade['entry_time']):<20} {str(trade['exit_time']):<20} "
                          f"{trade['position_type']:<6} {trade['entry_price']:<10.2f} "
                          f"{trade['exit_price']:<10.2f} ${trade['pnl']:<11.2f} "
                          f"{trade['pnl_pct']:<7.2f}% {trade['exit_reason']:<12}")
            print("-" * 120)
