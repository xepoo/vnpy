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
        interval=Interval.DAILY,
        start=datetime(2016, 1, 6),
        end=datetime(2020, 1, 1),
        rate=0.3 / 10000,
        slippage=0.2,
        size=10,
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
        "fast_entryWindow":10,
        "fast_exitWindow":5,
        "slow_entryWindow":20,
        "slow_exitWindow":10,
        "entryDev":1.0,
        "exitDev":0.0,
        "rsiWindow":7,
        "rsiSignal":10,
        "atrWindow":10,
    }
    engine.add_strategy(TurtleStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    # setting = OptimizationSetting()
    # setting.set_target("total_net_pnl")
    # setting.add_parameter("fast_entryWindow", 5, 30, 5)
    # setting.add_parameter("fast_exitWindow", 50, 100, 10)
    # setting.add_parameter("slow_entryWindow", 40, 100, 20)
    # setting.add_parameter("slow_exitWindow", 40, 100, 20)
    # setting.add_parameter("entryDev", 1.0, 1.0, 0.2)
    # setting.add_parameter("exitDev", 0, 0.2, 0.2)
    # setting.add_parameter("rsiWindow", 30, 30, 0)
    # setting.add_parameter("rsiSignal", 10, 10, 0)
    # setting.add_parameter("atrWindow", 30, 30, 0)
    #
    # engine.run_optimization(setting)
