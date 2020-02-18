from peewee import MySQLDatabase

from vnpy.trader.database.database import Driver
from vnpy.trader.setting import get_settings
from vnpy_slim.download_task.download_sql import init_task, TaskManager, MainType, FUTURE_START
from vnpy.trader.constant import Exchange
from datetime import datetime

class DownloadManage:
    def __init__(self, symbol: str,
                    exchange: str,
                    maintype: MainType = MainType.SINGLE,
                    interval: int = 60,
                    startdate: datetime = FUTURE_START,
                    enddate: datetime = datetime.now(),
                    dateauto: bool = False):
        settings = get_settings("database.")
        keys = {"database", "user", "password", "host", "port"}
        settings = {k: v for k, v in settings.items() if k in keys}

        db = MySQLDatabase(**settings)
        task, task_detail = init_task(db, Driver.MYSQL)
        self.task_mg = TaskManager(task, task_detail)
        self.task_mg.create_task(symbol, exchange, maintype, interval, startdate, enddate, dateauto)

    def run(self):
        task_list = self.task_mg.get_task()
        self.task_mg.gen_task_detail(task_list)
        self.task_mg.download_from_detail()

# SHFE.cu1901 - 上期所 cu1901 期货合约
# DCE.m1901 - 大商所 m1901 期货合约
# CZCE.SR901 - 郑商所 SR901 期货合约
# CFFEX.IF1901 - 中金所 IF1901 期货合约
#
# CZCE.SPD SR901&SR903 - 郑商所 SR901&SR903 跨期合约
# DCE.SP a1709&a1801 - 大商所 a1709&a1801 跨期合约
#
# DCE.m1807-C-2450 - 大商所豆粕期权
#
# KQ.m@CFFEX.IF - 中金所IF品种主连合约
# KQ.i@SHFE.bu - 上期所bu品种指数

#KQ.m@DCE.m -大商所m 豆粕主连合约 10吨，1，3，5，7，8，9，11，12
#KQ.i@DCE.m -大商所m 豆粕指数

#KQ.m@CZCE.TA -郑商所m PTA主连合约，5吨，1，2，3，4，5，6，7，8，9，10，11，12
#KQ.i@CZCE.TA -郑商所m PTA指数
