""""""
from datetime import datetime
from typing import List, Optional, Sequence, Type

from peewee import (
    AutoField,
    CharField,
    Database,
    DateTimeField,
    FloatField,
    Model,
    #MySQLDatabase,
    #PostgresqlDatabase,
    #SqliteDatabase,
    chunked,
)

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, TickData, TradeData
#from vnpy.trader.utility import get_file_path
from .database import BaseDatabaseManager, Driver
#from vnpy.trader.database.initialize import database_db

def init(db: Database, driver: Driver):
    global g_db
    g_db = db
    bar, tick, trade, bar_calc = init_models(db, driver)
    return SqlManager(db, bar, tick, trade, bar_calc)

class ModelBase(Model):

    def to_dict(self):
        return self.__data__




def init_models(db: Database, driver: Driver):
    class DbBarData(ModelBase):
        """
        Candlestick bar data for database storage.

        Index is defined unique with datetime, interval, symbol
        """

        id = AutoField()
        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        datetime: datetime = DateTimeField()
        interval: str = CharField(max_length=32)

        volume: float = FloatField()
        open_interest: float = FloatField()
        open_price: float = FloatField()
        high_price: float = FloatField()
        low_price: float = FloatField()
        close_price: float = FloatField()

        class Meta:
            database = db
            indexes = ((("symbol", "exchange", "interval", "datetime"), True),)

        @staticmethod
        def from_bar(bar: BarData):
            """
            Generate DbBarData object from BarData.
            """
            db_bar = DbBarData()

            db_bar.symbol = bar.symbol
            db_bar.exchange = bar.exchange.value
            db_bar.datetime = bar.datetime
            db_bar.interval = bar.interval.value
            db_bar.volume = bar.volume
            db_bar.open_interest = bar.open_interest
            db_bar.open_price = bar.open_price
            db_bar.high_price = bar.high_price
            db_bar.low_price = bar.low_price
            db_bar.close_price = bar.close_price

            return db_bar

        def to_bar(self):
            """
            Generate BarData object from DbBarData.
            """
            bar = BarData(
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                datetime=self.datetime,
                interval=Interval(self.interval),
                volume=self.volume,
                open_price=self.open_price,
                high_price=self.high_price,
                open_interest=self.open_interest,
                low_price=self.low_price,
                close_price=self.close_price,
                gateway_name="DB",
            )
            return bar

        @staticmethod
        def save_all(objs: List["DbBarData"]):
            """
            save a list of objects, update if exists.
            """
            dicts = [i.to_dict() for i in objs]
            with db.atomic():
                if driver is Driver.POSTGRESQL:
                    for bar in dicts:
                        DbBarData.insert(bar).on_conflict(
                            update=bar,
                            conflict_target=(
                                DbBarData.symbol,
                                DbBarData.exchange,
                                DbBarData.interval,
                                DbBarData.datetime,
                            ),
                        ).execute()
                else:
                    for c in chunked(dicts, 50):
                        DbBarData.insert_many(
                            c).on_conflict_replace().execute()

    class DbTickData(ModelBase):
        """
        Tick data for database storage.

        Index is defined unique with (datetime, symbol)
        """

        id = AutoField()

        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        datetime: datetime = DateTimeField()

        name: str = CharField(max_length=32)
        volume: float = FloatField()
        open_interest: float = FloatField()
        last_price: float = FloatField()
        last_volume: float = FloatField()
        limit_up: float = FloatField()
        limit_down: float = FloatField()

        open_price: float = FloatField()
        high_price: float = FloatField()
        low_price: float = FloatField()
        pre_close: float = FloatField()

        bid_price_1: float = FloatField()
        bid_price_2: float = FloatField(null=True)
        bid_price_3: float = FloatField(null=True)
        bid_price_4: float = FloatField(null=True)
        bid_price_5: float = FloatField(null=True)

        ask_price_1: float = FloatField()
        ask_price_2: float = FloatField(null=True)
        ask_price_3: float = FloatField(null=True)
        ask_price_4: float = FloatField(null=True)
        ask_price_5: float = FloatField(null=True)

        bid_volume_1: float = FloatField()
        bid_volume_2: float = FloatField(null=True)
        bid_volume_3: float = FloatField(null=True)
        bid_volume_4: float = FloatField(null=True)
        bid_volume_5: float = FloatField(null=True)

        ask_volume_1: float = FloatField()
        ask_volume_2: float = FloatField(null=True)
        ask_volume_3: float = FloatField(null=True)
        ask_volume_4: float = FloatField(null=True)
        ask_volume_5: float = FloatField(null=True)

        class Meta:
            database = db
            indexes = ((("symbol", "exchange", "datetime"), True),)

        @staticmethod
        def from_tick(tick: TickData):
            """
            Generate DbTickData object from TickData.
            """
            db_tick = DbTickData()

            db_tick.symbol = tick.symbol
            db_tick.exchange = tick.exchange.value
            db_tick.datetime = tick.datetime
            db_tick.name = tick.name
            db_tick.volume = tick.volume
            db_tick.open_interest = tick.open_interest
            db_tick.last_price = tick.last_price
            db_tick.last_volume = tick.last_volume
            db_tick.limit_up = tick.limit_up
            db_tick.limit_down = tick.limit_down
            db_tick.open_price = tick.open_price
            db_tick.high_price = tick.high_price
            db_tick.low_price = tick.low_price
            db_tick.pre_close = tick.pre_close

            db_tick.bid_price_1 = tick.bid_price_1
            db_tick.ask_price_1 = tick.ask_price_1
            db_tick.bid_volume_1 = tick.bid_volume_1
            db_tick.ask_volume_1 = tick.ask_volume_1

            if tick.bid_price_2:
                db_tick.bid_price_2 = tick.bid_price_2
                db_tick.bid_price_3 = tick.bid_price_3
                db_tick.bid_price_4 = tick.bid_price_4
                db_tick.bid_price_5 = tick.bid_price_5

                db_tick.ask_price_2 = tick.ask_price_2
                db_tick.ask_price_3 = tick.ask_price_3
                db_tick.ask_price_4 = tick.ask_price_4
                db_tick.ask_price_5 = tick.ask_price_5

                db_tick.bid_volume_2 = tick.bid_volume_2
                db_tick.bid_volume_3 = tick.bid_volume_3
                db_tick.bid_volume_4 = tick.bid_volume_4
                db_tick.bid_volume_5 = tick.bid_volume_5

                db_tick.ask_volume_2 = tick.ask_volume_2
                db_tick.ask_volume_3 = tick.ask_volume_3
                db_tick.ask_volume_4 = tick.ask_volume_4
                db_tick.ask_volume_5 = tick.ask_volume_5

            return db_tick

        def to_tick(self):
            """
            Generate TickData object from DbTickData.
            """
            tick = TickData(
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                datetime=self.datetime,
                name=self.name,
                volume=self.volume,
                open_interest=self.open_interest,
                last_price=self.last_price,
                last_volume=self.last_volume,
                limit_up=self.limit_up,
                limit_down=self.limit_down,
                open_price=self.open_price,
                high_price=self.high_price,
                low_price=self.low_price,
                pre_close=self.pre_close,
                bid_price_1=self.bid_price_1,
                ask_price_1=self.ask_price_1,
                bid_volume_1=self.bid_volume_1,
                ask_volume_1=self.ask_volume_1,
                gateway_name="DB",
            )

            if self.bid_price_2:
                tick.bid_price_2 = self.bid_price_2
                tick.bid_price_3 = self.bid_price_3
                tick.bid_price_4 = self.bid_price_4
                tick.bid_price_5 = self.bid_price_5

                tick.ask_price_2 = self.ask_price_2
                tick.ask_price_3 = self.ask_price_3
                tick.ask_price_4 = self.ask_price_4
                tick.ask_price_5 = self.ask_price_5

                tick.bid_volume_2 = self.bid_volume_2
                tick.bid_volume_3 = self.bid_volume_3
                tick.bid_volume_4 = self.bid_volume_4
                tick.bid_volume_5 = self.bid_volume_5

                tick.ask_volume_2 = self.ask_volume_2
                tick.ask_volume_3 = self.ask_volume_3
                tick.ask_volume_4 = self.ask_volume_4
                tick.ask_volume_5 = self.ask_volume_5

            return tick

        @staticmethod
        def save_all(objs: List["DbTickData"]):
            dicts = [i.to_dict() for i in objs]
            with db.atomic():
                if driver is Driver.POSTGRESQL:
                    for tick in dicts:
                        DbTickData.insert(tick).on_conflict(
                            update=tick,
                            conflict_target=(
                                DbTickData.symbol,
                                DbTickData.exchange,
                                DbTickData.datetime,
                            ),
                        ).execute()
                else:
                    for c in chunked(dicts, 50):
                        DbTickData.insert_many(c).on_conflict_replace().execute()

    class DbTradeData(ModelBase):

        id = AutoField()
        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        orderid: str = CharField(max_length=32)
        tradeid: str = CharField(max_length=32)
        direction: str = CharField(max_length=32)
        offset: str = CharField(max_length=32)
        price: float = FloatField()
        volume: float = FloatField()
        time: str = CharField(max_length=32)
        v0: float = CharField(max_length=32)
        v1: float = CharField(max_length=32)
        v2: float = CharField(max_length=32)
        v3: float = CharField(max_length=32)
        v4: float = CharField(max_length=32)
        v5: float = CharField(max_length=32)
        v6: float = CharField(max_length=32)
        v7: float = CharField(max_length=32)
        v8: float = CharField(max_length=32)
        v9: float = CharField(max_length=32)
        v10: float = CharField(max_length=32)
        v11: float = CharField(max_length=32)
        v12: float = CharField(max_length=32)
        v13: float = CharField(max_length=32)
        v14: float = CharField(max_length=32)
        v15: float = CharField(max_length=32)
        v16: float = CharField(max_length=32)
        v17: float = CharField(max_length=32)
        v18: float = CharField(max_length=32)
        v19: float = CharField(max_length=32)

        # def init(self):
        #     self.database_db = g_db
        #     self.database_db.connect()
        #     self.database_db.create_tables([DbTradeData])

        # @classmethod
        # def get_db(cls):
        #     return cls.database_db

        class Meta:
            database = db
            indexes = ((("symbol", "exchange", "time"), False),)

        def from_trade(self, trade: TradeData):
            """
            Generate DbTradeData object from TradeData.
            """
            self.symbol = trade.symbol
            self.exchange = trade.exchange.value
            self.orderid = trade.orderid
            self.tradeid = trade.tradeid
            self.direction = trade.direction.value
            self.offset = trade.offset.value
            self.price = trade.price
            self.volume = trade.volume
            self.time = trade.time

        def from_var(self, var: dict):
            for n, (k, v) in enumerate(var.items()):
                exec('self.v{} = {}'.format(n, str(v)))

        def save_trade(self):
            data = self.to_dict()
            self.insert(data).execute()

    class DBBarCalcData(ModelBase):

        id = AutoField()
        symbol: str = CharField(max_length=32)
        exchange: str = CharField(max_length=32)
        datetime: datetime = DateTimeField()
        interval: str = CharField(max_length=32)

        volume: float = FloatField()
        open_interest: float = FloatField()
        open_price: float = FloatField()
        high_price: float = FloatField()
        low_price: float = FloatField()
        close_price: float = FloatField()
        time: str = CharField(max_length=32)
        v0: float = CharField(max_length=32)
        v1: float = CharField(max_length=32)
        v2: float = CharField(max_length=32)
        v3: float = CharField(max_length=32)
        v4: float = CharField(max_length=32)
        v5: float = CharField(max_length=32)
        v6: float = CharField(max_length=32)
        v7: float = CharField(max_length=32)
        v8: float = CharField(max_length=32)
        v9: float = CharField(max_length=32)
        v10: float = CharField(max_length=32)
        v11: float = CharField(max_length=32)
        v12: float = CharField(max_length=32)
        v13: float = CharField(max_length=32)
        v14: float = CharField(max_length=32)
        v15: float = CharField(max_length=32)
        v16: float = CharField(max_length=32)
        v17: float = CharField(max_length=32)
        v18: float = CharField(max_length=32)
        v19: float = CharField(max_length=32)
        class Meta:
            database = db
            indexes = ((("symbol", "exchange", "interval", "datetime"), True),)

        def from_bar(self, bar: BarData):

            self.symbol = bar.symbol
            self.exchange = bar.exchange.value
            self.datetime = bar.datetime
            #self.interval = bar.interval.value
            self.volume = bar.volume
            self.open_interest = bar.open_interest
            self.open_price = bar.open_price
            self.high_price = bar.high_price
            self.low_price = bar.low_price
            self.close_price = bar.close_price

        def from_var(self, var: dict):
            for n, (k, v) in enumerate(var.items()):
                exec('self.v{} = {}'.format(n, str(v)))

        def save_bar_calc(self):
            data = self.to_dict()
            self.insert(data).execute()

    db.connect()
    db.create_tables([DbBarData, DbTickData, DbTradeData, DBBarCalcData])
    trade = DbTradeData()
    bar_calc = DBBarCalcData()
    trade.truncate_table()
    bar_calc.truncate_table()
    return DbBarData, DbTickData, trade, bar_calc


class SqlManager(BaseDatabaseManager):

    def __init__(self, db, class_bar: Type[Model], class_tick: Type[Model], trade, bar_calc):
        self.db = db
        self.class_bar = class_bar
        self.class_tick = class_tick
        self.db_trade = trade
        self.db_bar_calc = bar_calc

    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime,
    ) -> Sequence[BarData]:
        s = (
            self.class_bar.select()
                .where(
                (self.class_bar.symbol == symbol)
                & (self.class_bar.exchange == exchange.value)
                & (self.class_bar.interval == interval.value)
                & (self.class_bar.datetime >= start)
                & (self.class_bar.datetime <= end)
            )
            .order_by(self.class_bar.datetime)
        )
        data = [db_bar.to_bar() for db_bar in s]
        return data

    def load_tick_data(
        self, symbol: str, exchange: Exchange, start: datetime, end: datetime
    ) -> Sequence[TickData]:
        s = (
            self.class_tick.select()
                .where(
                (self.class_tick.symbol == symbol)
                & (self.class_tick.exchange == exchange.value)
                & (self.class_tick.datetime >= start)
                & (self.class_tick.datetime <= end)
            )
            .order_by(self.class_tick.datetime)
        )

        data = [db_tick.to_tick() for db_tick in s]
        return data

    def save_bar_data(self, datas: Sequence[BarData]):
        ds = [self.class_bar.from_bar(i) for i in datas]
        self.class_bar.save_all(ds)

    def save_tick_data(self, datas: Sequence[TickData]):
        ds = [self.class_tick.from_tick(i) for i in datas]
        self.class_tick.save_all(ds)

    def save_trade_data(self, trade: TradeData, var: dict):
        self.db_trade.from_trade(trade)
        self.db_trade.from_var(var)
        self.db_trade.save_trade()

    def save_bar_calc(
        self,
        bar: BarData,
        var: dict
    ):
        self.db_bar_calc.from_bar(bar)
        self.db_bar_calc.from_var(var)
        self.db_bar_calc.save_bar_calc()

    def get_newest_bar_data(
        self, symbol: str, exchange: "Exchange", interval: "Interval"
    ) -> Optional["BarData"]:
        s = (
            self.class_bar.select()
                .where(
                (self.class_bar.symbol == symbol)
                & (self.class_bar.exchange == exchange.value)
                & (self.class_bar.interval == interval.value)
            )
            .order_by(self.class_bar.datetime.desc())
            .first()
        )
        if s:
            return s.to_bar()
        return None

    def get_newest_tick_data(
        self, symbol: str, exchange: "Exchange"
    ) -> Optional["TickData"]:
        s = (
            self.class_tick.select()
                .where(
                (self.class_tick.symbol == symbol)
                & (self.class_tick.exchange == exchange.value)
            )
            .order_by(self.class_tick.datetime.desc())
            .first()
        )
        if s:
            return s.to_tick()
        return None

    def clean(self, symbol: str):
        self.class_bar.delete().where(self.class_bar.symbol == symbol).execute()
        self.class_tick.delete().where(self.class_tick.symbol == symbol).execute()
