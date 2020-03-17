""""""
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Type
from abc import ABC
from enum import Enum
from vnpy.trader.setting import get_settings
import os
import time

from peewee import (
    AutoField,
    CharField,
    Database,
    DateTimeField,
    FloatField,
    Model,
    MySQLDatabase,
    PostgresqlDatabase,
    SqliteDatabase,
    chunked,
    IntegerField)

from vnpy.trader.constant import Exchange, Interval, convert_interval
from vnpy.trader.object import BarData, TickData
from vnpy.trader.utility import get_file_path
from vnpy.trader.database.database import Driver
from vnpy.trader.database.database_sql import ModelBase
from dataclasses import dataclass
from vnpy.app.csv_loader import CsvLoaderEngine
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader

FUTURE_START = datetime(2016,1,1,9)
FUTURE_PATH = "future_data/"



class MainType(Enum):
    MASTER = "main" #KQ.m@
    INDEX = "idx" #KQ.i@
    SINGLE = "SINGLE"
    def convert2str(type):
        if type == MainType.SINGLE:
            return None
        elif type == MainType.MASTER:
            return "KQ.m@"
        elif type == MainType.INDEX:
            return "KQ.i@"

    def convert2type(str):
        if str == "main":
            return MainType.MASTER
        elif str == "idx":
            return MainType.INDEX
        else:
            return MainType.SINGLE



class TaskStatus(Enum):
        INIT = "init"
        PROCESSING = "processing"
        FINISHED = "finished"
        SUSPEND = "suspend"
        ERROR = "error"

@dataclass
class DownloadTaskData():
    """
    Candlestick bar data of a certain trading period.
    """
    maintype: MainType
    symbol: str
    exchange: Exchange
    interval: int
    startdate: datetime
    enddate: datetime
    status: TaskStatus
    detaildate: datetime
    processdate: datetime

    def __post_init__(self):
        """"""
        self.vt_symbol = f"{self.symbol}.{self.exchange.value}"

@dataclass
class DownloadTaskDetailData():
    """
    Candlestick bar data of a certain trading period.
    """
    maintype: MainType
    symbol: str
    exchange: Exchange
    interval: int
    detaildate: datetime
    status: TaskStatus
    processdate: datetime
    breakpointdate: datetime

    def __post_init__(self):
        """"""
        self.vt_symbol = f"{self.symbol}.{self.exchange.value}"

class TQDownload():
    def __init__(self):
        self.api = TqApi(TqSim())

    def tq_download_task(self, t: DownloadTaskDetailData, csv_file_name: str):
        download_tasks = {}
        start_date = t.detaildate + timedelta(days=-1)

        if t.maintype != MainType.SINGLE:
            symbol = MainType.convert2str(t.maintype) + t.exchange.value+'.'+t.symbol
        else:
            symbol = t.exchange.value + '.' + t.symbol

        download_tasks['task_name'] = DataDownloader(self.api,
                                                   symbol_list=symbol,
                                                   dur_sec=t.interval,
                                                   start_dt=datetime(start_date.year, start_date.month, start_date.day,
                                                                     21, 0, 0),
                                                   end_dt=datetime(t.detaildate.year, t.detaildate.month,
                                                                   t.detaildate.day, 16, 0, 0),
                                                   csv_file_name= csv_file_name)
        #with closing(self.api):
        while not all([v.is_finished() for v in download_tasks.values()]):
            self.api.wait_update()
            #print("progress: ", {k: ("%.2f%%" % v.get_progress()) for k, v in download_tasks.items()})


# def init():
#     settings = get_settings("database.")
#     db = init_mysql(settings)
#     task, task_detail = init_task(db, Driver.MYSQL)
#     return TaskManager(task, task_detail)
#
# def init_mysql(settings: dict):
#     keys = {"database", "user", "password", "host", "port"}
#     settings = {k: v for k, v in settings.items() if k in keys}
#     db = MySQLDatabase(**settings)
#     return db

def init_task(db: Database, driver: Driver):
    class DownLoadTask(ModelBase):
        """
        Candlestick bar data for database storage.

        Index is defined unique with datetime, interval, symbol
        """
        maintype: str = CharField(max_length=32)
        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        interval: int = IntegerField()
        startdate: datetime = DateTimeField()
        enddate: datetime = DateTimeField()

        status: str = CharField(max_length=32, null=True)
        detaildate: datetime = DateTimeField(null=True)
        processdate: datetime = DateTimeField(null=True)

        class Meta:
            database = db
            db_table = 'download_task'
            indexes = ((("maintype", "symbol", "exchange", "interval", "startdate", "enddate"), True),)

        @staticmethod
        def from_task(task: DownloadTaskData):
            """
            Generate DbBarData object from BarData.
            """
            db_task = DownLoadTask()
            db_task.maintype = task.maintype.value
            db_task.symbol = task.symbol
            db_task.exchange = task.exchange.value
            db_task.interval = task.interval
            db_task.startdate = task.startdate
            db_task.enddate = task.enddate
            db_task.status = task.status.value
            db_task.detaildate = task.detaildate
            db_task.processdate = task.processdate

            return db_task

        def to_task(self):
            """
            Generate BarData object from DbBarData.
            """
            task = DownLoadTask(
                maintype=MainType(self.maintype),
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                interval=self.interval,
                startdate=self.startdate,
                enddate=self.enddate,
                status=TaskStatus(self.status),
                detaildate=self.detaildate,
                processdate=self.processdate,
            )
            return task

        @staticmethod
        def save_all(objs: List["DownLoadTask"]):
            """
            save a list of objects, update if exists.
            """
            dicts = [i.to_dict() for i in objs]
            with db.atomic():
                if driver is Driver.POSTGRESQL:
                    for task in dicts:
                        DownLoadTask.insert(task).on_conflict(
                            update=task,
                            conflict_target=(
                                DownLoadTask.maintype,
                                DownLoadTask.symbol,
                                DownLoadTask.exchange,
                                DownLoadTask.interval,
                                DownLoadTask.startdate,
                                DownLoadTask.enddate,
                            ),
                        ).execute()
                else:
                    for c in chunked(dicts, 50):
                        DownLoadTask.insert_many(
                            c).on_conflict_ignore().execute()

    class DownloadTaskDetail(ModelBase):
        """
        Tick data for database storage.

        Index is defined unique with (datetime, symbol)
        """
        maintype: str = CharField(max_length=32)
        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        interval: int = IntegerField()
        detaildate: datetime = DateTimeField()
        status: str = CharField(max_length=32)
        processdate: datetime = DateTimeField()
        breakpointdate: datetime = DateTimeField()

        class Meta:
            database = db
            db_table = 'download_task_detail'
            indexes = ((("maintype", "symbol", "exchange", "interval", "detaildate"), True),)

        @staticmethod
        def from_task_detail(task_detail: DownloadTaskDetailData):
            """
            Generate DbTickData object from TickData.
            """
            db_task_detail = DownloadTaskDetail()
            db_task_detail.maintype = task_detail.maintype.value
            db_task_detail.symbol = task_detail.symbol
            db_task_detail.exchange = task_detail.exchange.value
            db_task_detail.interval = task_detail.interval
            db_task_detail.detaildate = task_detail.detaildate
            db_task_detail.status = task_detail.status.value
            db_task_detail.processdate = task_detail.processdate
            db_task_detail.breakpointdate = task_detail.breakpointdate

            return db_task_detail

        def to_task_detail(self):
            """
            Generate TickData object from DbTickData.
            """
            task_detail = DownloadTaskDetailData(
                maintype=MainType(self.maintype),
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                interval=self.interval,
                detaildate=self.detaildate,
                status=TaskStatus(self.status),
                processdate=self.processdate,
                breakpointdate=self.breakpointdate,
            )

            return task_detail

        @staticmethod
        def save_all(objs: List["DownloadTaskDetail"]):
            dicts = [i.to_dict() for i in objs]
            with db.atomic():
                if driver is Driver.POSTGRESQL:
                    for task_detail in dicts:
                        DownloadTaskDetail.insert(task_detail).on_conflict(
                            update=task_detail,
                            conflict_target=(
                                DownloadTaskDetail.maintype,
                                DownloadTaskDetail.symbol,
                                DownloadTaskDetail.exchange,
                                DownloadTaskDetail.interval,
                                DownloadTaskDetail.detaildate,
                            ),
                        ).execute()
                else:
                    for c in chunked(dicts, 50):
                        DownloadTaskDetail.insert_many(c).on_conflict_ignore().execute()

    db.connect()
    db.create_tables([DownLoadTask, DownloadTaskDetail])
    return DownLoadTask, DownloadTaskDetail


class TaskManager(ABC):

    def __init__(self, class_task: Type[Model], class_task_detail: Type[Model]):
        self.class_task = class_task
        self.class_task_detail = class_task_detail
        self.tq_down = TQDownload()
        self.engine = CsvLoaderEngine(None, None)

    def create_task(self,
                    symbol: str,
                    exchange: str,
                    maintype: MainType = MainType.SINGLE,
                    interval: int = 60,
                    startdate: datetime = FUTURE_START,
                    enddate: datetime = datetime.now(),
                    dateauto: bool = False):
        if dateauto:
            if int(symbol[-4:-2]) < 70 :
                year = int('20'+symbol[-4:-2])
            else:
                year = int('19'+symbol[-4:-2])
            month = int(symbol[-2:])
            if month == 12:
                enddate = datetime(year+1, 1, 1)
            else:
                enddate = datetime(year, month+1, 1)
            if enddate > datetime.now():
                enddate = datetime.now()
            startdate = datetime(year-1, month, 1)

        self.class_task.insert(
            maintype=maintype.value,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            startdate=startdate,
            enddate=enddate,
            status=TaskStatus.INIT.value,
        ).on_conflict_replace().execute()

    def get_task(self) -> Sequence[DownloadTaskData]:
        s = (
            self.class_task.select()
                .where(
                (self.class_task.status == TaskStatus.INIT.value)
            )
            .order_by(self.class_task.processdate)
        )
        data = [db_task.to_task() for db_task in s]
        return data

    def get_task_detail(self) -> Sequence[DownloadTaskDetailData]:
        s = (
            self.class_task_detail.select()
                .where(
                (self.class_task_detail.status == TaskStatus.INIT.value)
                |(self.class_task_detail.status == TaskStatus.SUSPEND.value)
            )
            .order_by(self.class_task_detail.detaildate)
        )
        data = [class_task_detail.to_task_detail() for class_task_detail in s]
        return data

    def update_task(self,
                    maintype: MainType,
                    symbol: str,
                    exchange: Exchange,
                    interval: int,
                    startdate: datetime,
                    enddate: datetime,
                    status: TaskStatus):
        self.class_task.update(
            status=status.value,
            processdate=datetime.now()
        ).where((self.class_task.maintype==maintype.value)
                &(self.class_task.symbol==symbol)
                &(self.class_task.exchange==exchange.value)
                &(self.class_task.interval==interval)
                &(self.class_task.startdate==startdate)
                & (self.class_task.enddate==enddate)
                ).execute()

    def gen_task_detail(self, objs: Sequence["DownloadTaskData"]):
        task_detail_list = []
        for t in objs:
            startdate = datetime(t.startdate.year, t.startdate.month, t.startdate.day, 9)
            enddate = datetime(t.enddate.year, t.enddate.month, t.enddate.day, 16)
            daydate = startdate
            while daydate < enddate:
                if daydate.weekday() not in[5,6]:
                    task_detail = DownloadTaskDetailData(
                        maintype=MainType(t.maintype),
                        symbol=t.symbol,
                        exchange=Exchange(t.exchange),
                        interval=t.interval,
                        detaildate=daydate,
                        status=TaskStatus.INIT,
                        processdate=datetime.now(),
                        breakpointdate=datetime.now(),
                    )
                    task_detail_list.append(task_detail)
                daydate += timedelta(days=1)
            self.update_task(t.maintype, t.symbol, t.exchange, t.interval, t.startdate, t.enddate, TaskStatus.FINISHED)

        ds = [self.class_task_detail.from_task_detail(i) for i in task_detail_list]
        self.class_task_detail.save_all(ds)

    def update_task_detail(self,
                    maintype: MainType,
                    symbol: str,
                    exchange: Exchange,
                    interval: int,
                    detaildate: datetime,
                    status: TaskStatus):
        self.class_task_detail.update(
            status=status.value,
            processdate=datetime.now()
        ).where((self.class_task_detail.maintype==maintype.value)
                &(self.class_task_detail.symbol==symbol)
                &(self.class_task_detail.exchange==exchange.value)
                &(self.class_task_detail.interval==interval)
                &(self.class_task_detail.detaildate==detaildate)
                ).execute()

    def make_csv_file(self, t: DownloadTaskDetailData):
        path = FUTURE_PATH + t.maintype.value + "_" + t.symbol + "_" + t.exchange.value + "/" + str(t.interval)
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        task_name = t.maintype.value + '_' + t.symbol + '_' + t.exchange.value + '_' + str(t.interval) + '_' + t.detaildate.strftime(
            "%Y%m%d")
        csv_file_name = path + '/' + task_name + ".csv"
        return csv_file_name

    def load_csv_to_db(self, t: DownloadTaskDetailData, csv_file_name:str):
        interval = convert_interval(t.interval)
        if t.maintype != MainType.SINGLE:
            head = MainType.convert2str(t.maintype)+t.exchange.value + '.' + t.symbol
            symbol = t.symbol+t.maintype.value
        else:
            head = t.exchange.value + '.' + t.symbol
            symbol = t.symbol

        self.engine.load_by_handle(
            open(csv_file_name, "r"),
            symbol=symbol,
            exchange=t.exchange,
            interval=interval,
            datetime_head="datetime",
            open_head=head + ".open",
            close_head=head + ".close",
            low_head=head + ".low",
            high_head=head + ".high",
            volume_head=head + ".volume",
            datetime_format="%Y-%m-%d %H:%M:%S.000000000",
        )

    def download_from_detail(self):
        data = self.get_task_detail()
        sum = len(data)
        for n, t in enumerate(data):
            time.sleep(1)
            csv_file_name = self.make_csv_file(t)
            self.tq_down.tq_download_task(t, csv_file_name)
            self.load_csv_to_db(t, csv_file_name)

            end_dt = datetime(t.detaildate.year, t.detaildate.month,t.detaildate.day, 16, 0, 0)
            if datetime.now() < end_dt:
                self.update_task_detail(t.maintype,t.symbol,t.exchange,t.interval,t.detaildate,TaskStatus.SUSPEND)
            else:
                self.update_task_detail(t.maintype,t.symbol, t.exchange, t.interval, t.detaildate, TaskStatus.FINISHED)

            print(f"完成 {n}/{sum}, 文件：{csv_file_name}")


    def clean(self, symbol: str):
        self.class_task.delete().where(self.class_task.symbol == symbol).execute()
        self.class_task_detail.delete().where(self.class_task_detail.symbol == symbol).execute()
