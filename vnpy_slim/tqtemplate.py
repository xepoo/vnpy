from vnpy.gateway.tianqin.tqdata import TqdataApi
from vnpy.trader.constant import Exchange, Interval
import datetime

tqdata = TqdataApi()
bars = tqdata.query_history(symbol='cu1911', exchange=Exchange.SHFE, interval=Interval.MINUTE, start=datetime.datetime.now()-datetime.timedelta(days = 10), end=datetime.datetime.now())
print(bars[1])