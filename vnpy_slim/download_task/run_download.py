from vnpy_slim.download_task.download_manage import DownloadManage
from vnpy_slim.download_task.download_sql import MainType
import multiprocessing
from datetime import datetime, time
from time import sleep

load_setting = {
    "玉米主连分钟":{
        "symbol":"c",
        "exchange":"DCE",
        "type":"main",
        "interval":60,
        },
    # "玉米指数分钟": {
    #     "symbol":"c",
    #     "exchange":"DCE",
    #     "type":"idx",
    #     "interval":60,
    # },
    # "玉米主连日": {
    #     "symbol":"c",
    #     "exchange":"DCE",
    #     "type":"main",
    #     "interval":86400,
    # },
    # "玉米指数日": {
    #     "symbol":"c",
    #     "exchange":"DCE",
    #     "type":"idx",
    #     "interval":86400,
    # },
    # "螺纹钢主连分钟": {
    #     "symbol": "rb",
    #     "exchange": "SHFE",
    #     "type": "main",
    #     "interval": 60,
    # },
    # "螺纹钢指数分钟": {
    #     "symbol": "rb",
    #     "exchange": "SHFE",
    #     "type": "idx",
    #     "interval": 60,
    # },
    # "螺纹钢主连日": {
    #     "symbol": "rb",
    #     "exchange": "SHFE",
    #     "type": "main",
    #     "interval": 86400,
    # },
    # "螺纹钢指数日": {
    #     "symbol": "rb",
    #     "exchange": "SHFE",
    #     "type": "idx",
    #     "interval": 86400,
    # },
    # "PTA主连分钟": {
    #     "symbol": "TA",
    #     "exchange": "CZCE",
    #     "type": "main",
    #     "interval": 60,
    # },
    # "PTA指数分钟": {
    #     "symbol": "TA",
    #     "exchange": "CZCE",
    #     "type": "idx",
    #     "interval": 60,
    # },
    # "PTA主连日": {
    #     "symbol": "TA",
    #     "exchange": "CZCE",
    #     "type": "main",
    #     "interval": 86400,
    # },
    # "PTA指数日": {
    #     "symbol": "TA",
    #     "exchange": "CZCE",
    #     "type": "idx",
    #     "interval": 86400,
    # },
}

# ----------------------------------------------------------------------
def runChildProcess():
    """子进程运行函数"""
    print(u"开始更新K线数据")

    for k, v in load_setting.items():
        print("start download: ", k)
        load = DownloadManage(symbol=v["symbol"], exchange=v["exchange"], maintype= MainType.convert2type(v["type"]), interval=v["interval"])
        load.run()
        print("end download: ", k)
    print(u"K线数据更新完成")

# ----------------------------------------------------------------------
def runParentProcess():
    """守护进程运行函数"""
    updateDate = None  # 已更新数据的日期

    while True:
        # 每轮检查等待5秒，避免跑满CPU（浪费算力）
        sleep(5)

        currentTime = datetime.now().time()
        print(u"当前时间为：", currentTime)

        # 过滤交易日
        today = datetime.now().date()
        weekday = datetime.now().weekday()
        #if weekday in [5, 6]:  # 从0开始，周六为5，周日为6
        #    continue

        # 每日5点后开始下载当日数据，通常3:15收盘后（国债）数据提供商需要一定时间清洗数据）
        #if currentTime <= time(17, 0):
        #    continue

        # 每日只需要更新一次数据
        if updateDate == today:
            continue

        # 启动子进程来更新数据
        p = multiprocessing.Process(target=runChildProcess)

        p.start()
        print(u"启动子进程")
        p.join()
        print(u"子进程已关闭")

        # 记录当日数据已经更新
        updateDate = today


if __name__ == "__main__":
    runParentProcess()