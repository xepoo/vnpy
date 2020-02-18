from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy_slim.strategies.b_breaker_a_strategy import ( RBreakAStrategy,)
from vnpy.trader.constant import (Interval)
from datetime import datetime
import multiprocessing

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="cmain.DCE",
        interval=Interval.MINUTE,
        start=datetime(2017, 1, 1),
        end=datetime(2020, 1, 1),
        rate=0.3 / 10000,
        slippage=0.2,
        size=250,
        pricetick=1,
        capital=1_000_000,
    )

    setting = {
        "setup_coef": 0.38,
        "break_coef": 0.2,
        "enter_coef_1": 1.07,
        "enter_coef_2": 0.07,
        "fixed_size": 1,
        "donchian_window": 21,
        "trailing_long": 0.4,
        "trailing_short": 0.4,
        "multiplier": 5
    }
    engine.add_strategy(RBreakAStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    # setting = OptimizationSetting()
    # setting.set_target("total_net_pnl")
    # setting.add_parameter("setup_coef",  0.38,  0.38, 0.01)
    # setting.add_parameter("break_coef", 0.10, 0.10, 0.01)
    # setting.add_parameter("enter_coef_1", 1.07, 1.07, 0.01)
    # setting.add_parameter("enter_coef_2", 0.07,0.07, 0.01)
    # setting.add_parameter("donchian_window", 21, 21, 1)
    # setting.add_parameter("trailing_long", 0.4, 0.4, 0.1)
    # setting.add_parameter("trailing_short", 0.4, 0.4, 0.1)
    # engine.run_optimization(setting)