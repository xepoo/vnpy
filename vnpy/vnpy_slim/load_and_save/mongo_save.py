
from vnpy.app.csv_loader import CsvLoaderEngine
from vnpy.trader.constant import Exchange, Interval
import os
import csv

engine = CsvLoaderEngine(None, None)
engine.load_by_handle(
    open("shfe.cu1802_min.csv", "r"),
    symbol="cu1802",
    exchange=Exchange.SHFE,
    interval=Interval.MINUTE,
    datetime_head="datetime",
    open_head="SHFE.cu1802.open",
    close_head="SHFE.cu1802.close",
    low_head="SHFE.cu1802.low",
    high_head="SHFE.cu1802.high",
    volume_head="SHFE.cu1802.volume",
    #datetime_format=None
    datetime_format="%Y-%m-%d %H:%M:%S.000000000",
)
engine.close()