from vnpy.app.data_recorder.engine import RecorderEngine
from vnpy.app.script_trader import init_cli_trading
from vnpy.gateway.ctp import CtpGateway
from vnpy.event import Event, EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from threading import Thread
from queue import Queue, Empty
from copy import copy
from vnpy.trader.object import (
    SubscribeRequest,
    TickData,
    BarData,
    ContractData
)
from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT
from vnpy.trader.utility import load_json, save_json, BarGenerator
from vnpy.trader.database import database_manager
import time
import json
# 事件引擎
event_engine=EventEngine()
# 主要引擎
main_engine=MainEngine(event_engine)
# 添加引擎
main_engine.init_engines()
#加载ctp接口
main_engine.add_gateway(CtpGateway)
# 连接CTP
setting = {
    "用户名": "152402",
    "密码": "baiyun18",
    "经纪商代码": "9999",
    "交易服务器":"180.168.146.187:10101",
    "行情服务器":"180.168.146.187:10111",
    "产品名称":"simnow_client_test",
    "授权编码":"0000000000000000",
    "产品信息": ""
}
main_engine.connect(setting,'CTP')
APP_NAME = "DataRecorder"

EVENT_RECORDER_LOG = "eRecorderLog"
EVENT_RECORDER_UPDATE = "eRecorderUpdate"
time.sleep(3)

contract_list=main_engine.get_all_contracts()
print(contract_list[1])
for contract in contract_list:
    req = SubscribeRequest(
            symbol=contract.symbol,
            exchange=contract.exchange
        )
    main_engine.subscribe(req, contract.gateway_name)
recorder=RecorderEngine(main_engine,event_engine)
while True:
    now_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time.sleep(1)
    if now_time[-2:]=='00':
        print(now_time)