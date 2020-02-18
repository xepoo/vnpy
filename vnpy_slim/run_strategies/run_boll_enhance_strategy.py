from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy_slim.strategies.boll_enhance_strategy import ( BollEnhanceStrategy,)
from vnpy.trader.constant import (Interval)
from datetime import datetime
import multiprocessing

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="mhot.DCE",
        interval=Interval.MINUTE,
        start=datetime(2016, 1, 1),
        end=datetime(2020, 1, 1),
        rate=0.3 / 10000,
        slippage=0.2,
        size=250,
        pricetick=1,
        capital=1_000_000,
    )

    setting = {"boll_window": 16,
               "boll_dev": 2.6,
               "cci_window": 10,
               "atr_window": 26,
               "atr_ma_window": 7,
               "rsi_window": 7,
               "rsi_entry": 23,
               "ma_window": 5,
               "sl_multiplier": 7.6,
               "fixed_size": 5}
    engine.add_strategy(BollEnhanceStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    # setting = OptimizationSetting()
    # setting.set_target("total_net_pnl")
    # setting.add_parameter("boll_window", 16, 16, 1)
    # setting.add_parameter("boll_dev", 2.6, 2.6, 1.0)
    # setting.add_parameter("cci_window", 10, 10, 1)
    # setting.add_parameter("atr_window", 26, 26, 1)
    # setting.add_parameter("rsi_window", 7, 7, 1)
    # setting.add_parameter("rsi_entry", 23, 23, 1)
    # setting.add_parameter("sl_multiplier", 25300, 25300, 100)
    # setting.add_parameter("fixed_size", 5, 5, 1)
    #
    # engine.run_optimization(setting)