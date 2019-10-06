from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader

api = TqApi(TqSim())
download_tasks = {}
# 下载从 2018-01-01凌晨6点 到 2018-06-01下午4点 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
# 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
# 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
download_tasks["cu_min"] = DataDownloader(api, symbol_list=["SHFE.cu1802"], dur_sec=60,
                                          start_dt=datetime(2017, 2, 1, 6, 0, 0), end_dt=datetime(2018, 3, 1, 6, 0, 0),
                                          csv_file_name="shfe.cu1802_min.csv")

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