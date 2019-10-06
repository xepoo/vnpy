from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from datetime import datetime
engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="cu1802.SHFE",
    interval="1m",
    start=datetime(2017, 3, 1),
    end=datetime(2017, 4, 30),
    rate=0.3/10000,
    slippage=0.2,
    size=300,
    pricetick=0.2,
    capital=1_000_000,
)
engine.add_strategy(AtrRsiStrategy, {})
engine.load_data()
engine.run_backtesting()
df = engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()
setting = OptimizationSetting()
setting.set_target("sharpe_ratio")
setting.add_parameter("atr_length", 3, 39, 1)
setting.add_parameter("atr_ma_length", 10, 30, 1)
engine.run_ga_optimization(setting)
print("end")

# from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
# from vnpy.app.cta_backtester.engine import BacktesterEngine
# from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import AtrRsiStrategy
# from vnpy.event.engine import EventEngine
# from vnpy.trader.engine import MainEngine
# from datetime import datetime
# from vnpy.gateway.ctp import CtpGateway
# import time
# engine = BacktestingEngine()
#
# event_engine = EventEngine()
# main_engine = MainEngine(event_engine)
# main_engine.add_gateway(CtpGateway)
# setting = {
#     "用户名": "152402",
#     "密码": "baiyun18",
#     "经纪商代码": "9999",
#     "交易服务器":"180.168.146.187:10101",
#     "行情服务器":"180.168.146.187:10111",
#     "产品名称":"simnow_client_test",
#     "授权编码":"0000000000000000",
#     "产品信息": ""
# }
# main_engine.connect(setting, "CTP")
# engine_class = BacktesterEngine(main_engine, event_engine)
# #engine_class.init_rqdata("13793190053","baiyun18")
# time.sleep(3)
#
# engine_class.run_downloading(vt_symbol="IF88.CFFEX", interval="1m", start=datetime(2019, 1, 1), end=datetime(2019, 4, 30),)

# engine.set_parameters(
#     vt_symbol="IF88.CFFEX",
#     interval="1m",
#     start=datetime(2019, 1, 1), end=datetime(2019, 4, 30),
#     rate=0.3 / 10000,
#     slippage=0.2,
#     size=300,
#     pricetick=0.2,
#     capital=1_000_000,
# )
# engine.add_strategy(AtrRsiStrategy, {})
# engine.load_data()
# engine.run_backtesting()
#
# df = engine.calculate_result()
# engine.calculate_statistics()
# engine.show_chart()
#
# #以下为优化
# setting = OptimizationSetting()
# setting.set_target("sharpe_ratio")
# setting.add_parameter("attr_length", 3, 39, 1)
# setting.add_parameter("atr_ma_length", 10, 30, 1)
# engine.run_ga_optimization(setting)