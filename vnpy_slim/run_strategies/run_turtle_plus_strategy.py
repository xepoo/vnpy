from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy_slim.strategies.turtle_plus_strategy import ( TurtleStrategy,)
from vnpy.trader.constant import (Interval)
from datetime import datetime
import multiprocessing

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="cmain.DCE",
        #vt_symbol="cmain.DCE",
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

# (2016, 1, 1) ~ (2020, 1, 1)
    # setting = {"boll_window": 6,
    #            "boll_dev": 1.9,
    #            "atr_window": 31,
    #            "rsi_f_window": 7,
    #            "rsi_l_window": 43,
    #            "grow_window": 8,
    #            "reduce_window": 7,
    #            "sl_multiplier": 7.1,
    #            "fixed_size": 5}

#(2019, 1, 1) ~ (2020, 1, 1)
    # setting = {"boll_window": 5,
    #            "boll_dev": 2.0,
    #            "atr_window": 30,
    #            "rsi_f_window": 6,
    #            "rsi_l_window": 36,
    #            "grow_window": 6,
    #            "reduce_window": 6,
    #            "sl_multiplier": 7.2,
    #            "fixed_size": 5}

# (2016, 1, 1) ~ (2016, 7, 1)
    setting = {
        # "boll_window": 5,
        #        "boll_dev": 1.6,
        #        "atr_window": 31,
        #        "rsi_f_window": 7,
        #        "rsi_l_window": 36,
        #        "grow_window": 5,
        #        "reduce_window": 6,
        #        "sl_multiplier": 7.5,
        #        "fixed_size": 5,
        #        "db_record": 0
    }
    engine.add_strategy(TurtleStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    # setting = OptimizationSetting()
    # setting.set_target("total_net_pnl")
    # setting.add_parameter("boll_window", 5, 5, 1)
    # setting.add_parameter("boll_dev", 1.6, 1.6, 0.1)
    # setting.add_parameter("atr_window", 31, 31, 1)
    # setting.add_parameter("rsi_f_window", 7, 7, 1)
    # setting.add_parameter("rsi_l_window", 36, 36, 1)
    # setting.add_parameter("grow_window", 5, 5, 1)
    # setting.add_parameter("reduce_window", 6, 6, 1)
    # setting.add_parameter("sl_multiplier", 7.5, 7.5, 0.1)
    # setting.add_parameter("fixed_size", 5, 5, 1)
    #
    # engine.run_optimization(setting)
