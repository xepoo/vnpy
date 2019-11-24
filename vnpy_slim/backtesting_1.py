from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from vnpy.app.cta_strategy.strategies.double_ma_strategy import DoubleMaStrategy
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import TurtleSignalStrategy
from datetime import datetime
engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="cu1802.SHFE",
    interval="1m",
    start=datetime(2017, 3, 1),
    end=datetime(2018, 2, 1),
    rate=0.3/10000,
    slippage=0.2,
    size=300,
    pricetick=0.2,
    capital=1_000_000,
)
engine.add_strategy(AtrRsiStrategy, {})
#engine.add_strategy(DoubleMaStrategy, {})
engine.load_data()
engine.run_backtesting()
df = engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()
# setting = OptimizationSetting()
# setting.set_target("sharpe_ratio")
# setting.add_parameter("atr_length", 3, 39, 1)
# setting.add_parameter("atr_ma_length", 10, 30, 1)
# engine.run_ga_optimization(setting)
#
# engine.run_backtesting()
#
#
# df = engine.calculate_result()
# engine.calculate_statistics()
# engine.show_chart()
print("end")
