from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy_slim.strategies.mlearn_strategy import (MLearnStrategy,)
from vnpy.trader.constant import (Interval)
from datetime import datetime
import multiprocessing

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    engine = BacktestingEngine()
    engine.set_parameters(
        #vt_symbol="mhot.DCE",
        vt_symbol="cmain.DCE",
        #vt_symbol="rbmain.SHFE",
        interval=Interval.MINUTE,
        start=datetime(2016, 1, 1),
        end=datetime(2020, 1, 1),
        rate=0.3 / 10000,
        slippage=0.2,
        size=250,
        pricetick=1,
        capital=1_000_000,
    )

    setting = {}

    engine.add_strategy(MLearnStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    # setting = OptimizationSetting()
    # setting.set_target("total_net_pnl")
    # setting.add_parameter("boll_window", 5, 5, 1)
    # setting.add_parameter("boll_dev", 1.1, 1.1, 0.1)
    # setting.add_parameter("atr_window", 40, 40, 1)
    # setting.add_parameter("rsi_f_window", 5, 15, 1)
    # setting.add_parameter("rsi_l_window", 31, 31, 1)
    # setting.add_parameter("grow_window", 8, 8, 1)
    # setting.add_parameter("reduce_window", 10, 10, 1)
    # setting.add_parameter("sl_multiplier", 8.0, 8.0, 0.2)
    # setting.add_parameter("fixed_size", 5, 5, 1)
    # setting.add_parameter("bar_size", 80, 120, 5)
    #
    # #
    # engine.run_optimization(setting)
