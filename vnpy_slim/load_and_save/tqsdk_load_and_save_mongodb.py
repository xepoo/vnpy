from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader

from vnpy.app.csv_loader import CsvLoaderEngine
from vnpy.trader.constant import Exchange, Interval
import os

api = TqApi(TqSim())
set_csv_path = "D:\\SynologyDrive\\future_data\\"
set_exchange = Exchange.SHFE.value
set_symbol = "cu1802"
set_bar_sec = 60
set_start_date = datetime(2017, 2, 1, 6, 0, 0)
set_end_date = datetime(2018, 3, 1, 6, 0, 0)
set_csv_file_name = set_csv_path+set_exchange+'_'+set_symbol+'_'+str(set_bar_sec)+'_'+set_start_date.strftime("%Y%m%d%H%M%S")+'_'+set_end_date.strftime("%Y%m%d%H%M%S")+".csv"

if os.path.exists(set_csv_file_name):
    print(set_csv_file_name + "已存在，删除")
    os.remove(set_csv_file_name)

download_tasks = {}
# 下载从 2018-01-01凌晨6点 到 2018-06-01下午4点 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
# 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
# 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
download_tasks["cu_min"] = DataDownloader(api, symbol_list=[set_exchange+'.'+set_symbol], dur_sec=set_bar_sec,
                                          start_dt=set_start_date, end_dt=set_end_date,
                                          csv_file_name=set_csv_file_name)

# download_tasks["cu_min"] = DataDownloader(api, symbol_list=["SHFE.cu1803"], dur_sec=60,
#                                           start_dt=datetime(2017, 3, 1, 6, 0, 0), end_dt=datetime(2018, 4, 1, 6, 0, 0),
#                                           csv_file_name="shfe.cu1803_min.csv")
#
# download_tasks["cu_min"] = DataDownloader(api, symbol_list=["SHFE.cu1804"], dur_sec=60,
#                                           start_dt=datetime(2017, 4, 1, 6, 0, 0), end_dt=datetime(2018, 5, 1, 6, 0, 0),
#                                           csv_file_name="shfe.cu1804_min.csv")

# 下载从 2018-05-01凌晨0点 到 2018-06-01凌晨0点 的 T1809 盘口Tick数据
# download_tasks["T_tick"] = DataDownloader(api, symbol_list=["SHFE.cu1801"], dur_sec=0,
#                                           start_dt=datetime(2017, 1, 1), end_dt=datetime(2018, 1, 1),
#                                           csv_file_name="SHFE.cu1801_tick.csv")
# 使用with closing机制确保下载完成后释放对应的资源
with closing(api):
    while not all([v.is_finished() for v in download_tasks.values()]):
        api.wait_update()
        print("progress: ", {k: ("%.2f%%" % v.get_progress()) for k, v in download_tasks.items()})

print("下载完成，开始写入数据库")


engine = CsvLoaderEngine(None, None)
engine.load_by_handle(
    open(set_csv_file_name, "r"),
    symbol=set_symbol,
    exchange=Exchange.SHFE,
    interval=Interval.MINUTE,
    datetime_head="datetime",
    open_head=set_exchange+'.'+set_symbol+".open",
    close_head=set_exchange+'.'+set_symbol+".close",
    low_head=set_exchange+'.'+set_symbol+".low",
    high_head=set_exchange+'.'+set_symbol+".high",
    volume_head=set_exchange+'.'+set_symbol+".volume",
    datetime_format="%Y-%m-%d %H:%M:%S.000000000",
)
engine.close()
print("写入数据库完成")