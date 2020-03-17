from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader
from vnpy.trader.database import database_manager
from vnpy.app.csv_loader import CsvLoaderEngine
from vnpy.trader.constant import Exchange, Interval
import os
from vnpy.trader.object import BarData, HistoryRequest

CSV_PATH = "future_data/"

INTERVAL_2_SEC_MAP = {
    Interval.MINUTE: 60,
    Interval.HOUR: 3600,
    Interval.DAILY: 86400
}

class TqdataApi:

    def init(self):
        """"""

    def make_csvfile_name(self, symbol:str, exchange:Exchange, interval:Interval, start_dt:datetime, end_dt:datetime):
        return CSV_PATH + exchange.value + '_' + symbol + '_' + str(interval.value) + '_' + start_dt.strftime("%Y%m%d%H%M%S") + '_' + end_dt.strftime("%Y%m%d%H%M%S") + ".csv"

    def download_bar(self, symbol:str, exchange:Exchange, interval:Interval, start_dt:datetime, end_dt:datetime):

        csv_file_name = self.make_csvfile_name(symbol=symbol, exchange=exchange, interval=interval, start_dt=start_dt, end_dt=end_dt)
        if os.path.exists(csv_file_name):
            print(csv_file_name + "已存在，删除")
            os.remove(csv_file_name)

        # 下载从 2018-01-01凌晨6点 到 2018-06-01下午4点 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
        # 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
        # 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
        with TqApi(TqSim()) as api:
            download_task = DataDownloader(api, symbol_list=[exchange.value + '.' + symbol],
                                           dur_sec=INTERVAL_2_SEC_MAP[interval],
                                           start_dt=start_dt, end_dt=end_dt,
                                           csv_file_name=csv_file_name)
            # 使用with closing机制确保下载完成后释放对应的资源
            with closing(api):
                while not download_task.is_finished():
                    self.api.wait_update()
                    print("tq download progress: ", "%.2f%%" % download_task.get_progress())


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



    def data_csv2db(self, symbol:str, exchange:Exchange, interval:Interval, start_dt:datetime, end_dt:datetime):
        csv_file_name = self.make_csvfile_name(symbol=symbol, exchange=exchange, interval=interval, start_dt=start_dt, end_dt=end_dt)
        if not os.path.exists(csv_file_name):
            print(csv_file_name + "不存在，错误")
            return None
        engine = CsvLoaderEngine(None, None)
        engine.load_by_handle(
            open(csv_file_name, "r"),
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            datetime_head="datetime",
            open_head=exchange.value + '.' + symbol + ".open",
            close_head=exchange.value + '.' + symbol + ".close",
            low_head=exchange.value + '.' + symbol + ".low",
            high_head=exchange.value + '.' + symbol + ".high",
            volume_head=exchange.value + '.' + symbol + ".volume",
            datetime_format="%Y-%m-%d %H:%M:%S.000000000",
        )
        engine.close()

    def query_history(self, req: HistoryRequest):
        """
        Query history bar data from RQData.
        """
        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start
        end = req.end

        bars = database_manager.load_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start=start,
            end=end,
        )

        if not bars:
            self.download_bar(symbol=symbol, exchange=exchange, interval=interval, start_dt=start, end_dt=end)
            self.data_csv2db(symbol=symbol, exchange=exchange, interval=interval, start_dt=start, end_dt=end)
            bars = database_manager.load_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=start,
                end=end,
            )

        return bars

tqdata_api = TqdataApi()