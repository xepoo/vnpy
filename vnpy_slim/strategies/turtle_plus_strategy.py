# encoding: UTF-8

"""
单标的海龟交易策略，实现了完整海龟策略中的信号部分。
"""

from __future__ import division

#from vnpy.trader.vtObject import VtBarData
#from vnpy.trader.vtConstant import DIRECTION_LONG, DIRECTION_SHORT
from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
    BarData,
    TickData,
    TradeData,
    OrderData
)


########################################################################
class TurtleResult(object):
    """一次完整的开平交易"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.unit = 0
        self.entry = 0  # 开仓均价
        self.exit = 0  # 平仓均价
        self.pnl = 0  # 盈亏

    # ----------------------------------------------------------------------
    def open(self, price, change):
        """开仓或者加仓"""
        self.unit += change
        self.entry = price

    # ----------------------------------------------------------------------
    def close(self, price):
        """平仓"""
        self.exit = price
        self.pnl = self.unit * (self.exit - self.entry)


########################################################################
class TurtleSignal(object):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, entryWindow, exitWindow, entryDev,
                 exitDev, rsiWindow, rsiSignal):
        """Constructor"""
        self.entryWindow = entryWindow
        self.exitWindow = exitWindow
        self.entryDev = entryDev
        self.exitDev = exitDev
        self.rsiWindow = rsiWindow
        self.rsiSignal = rsiSignal

        self.am = ArrayManager(60)

        self.atrVolatility = 0
        self.entryUp = 0
        self.entryDown = 0
        self.exitUp = 0
        self.exitDown = 0
        self.rsiValue = 0

        self.unit = 0
        self.result = None
        self.lastResult = None

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self.generateSignal(bar)
        self.calculateIndicator()

    # ----------------------------------------------------------------------
    def calculateIndicator(self):
        """"""
        keltnerEntryUp, keltnerEntryDown = self.am.keltner(self.entryWindow, self.entryDev)
        keltnerExitUp, keltnerExitDown = self.am.keltner(self.exitWindow, self.exitDev)

        donchianEntryUp, donchianEntryDown = self.am.donchian(self.entryWindow)
        donchianExitUp, donchianExitDown = self.am.donchian(self.exitWindow)

        self.entryUp = max(donchianEntryUp, keltnerEntryUp)
        self.entryDown = min(donchianEntryDown, keltnerEntryDown)

        self.exitUp = min(keltnerExitUp, donchianExitUp)
        self.exitDown = max(keltnerExitDown, donchianExitDown)

        self.rsiValue = self.am.rsi(self.rsiWindow)

    # ----------------------------------------------------------------------
    def generateSignal(self, bar):
        """"""
        # 平仓
        if self.unit > 0:
            if bar.low <= self.exitDown:
                self.close(self.exitDown)
        if self.unit < 0:
            if bar.high >= self.exitUp:
                self.close(self.exitUp)
                # 开仓
        else:
            if self.rsiValue >= (50 + self.rsiSignal):
                if bar.high >= self.entryUp:
                    self.open(self.entryUp, 1)
            elif self.rsiValue <= (50 - self.rsiSignal):
                if bar.low <= self.entryDown:
                    self.open(self.entryDown, -1)

    # ----------------------------------------------------------------------
    def open(self, price, change):
        """"""
        self.unit += change

        if not self.result:
            self.result = TurtleResult()
        self.result.open(price, change)

    # ----------------------------------------------------------------------
    def close(self, price):
        """"""
        self.unit = 0

        self.result.close(price)
        self.lastResult = self.result
        self.result = None

    # ----------------------------------------------------------------------
    def getLastPnl(self):
        """"""
        if not self.lastResult:
            return 0

        return self.lastResult.pnl

    ########################################################################


class TurtleStrategy(CtaTemplate):
    """海龟交易策略"""
    className = 'TurtleStrategy'
    author = u'用Python的交易员'


    # 策略参数
    initDays = 10  # 初始化数据所用的天数
    capital = 1000000
    tradingUnit = 4
    contractSize = 10

    # 参数列表，保存了参数的名称
    parameters = []

    # 变量列表，保存了变量的名称
    variables = ['inited',
               'trading',
               'pos',
               'currentSignal',
               'atrVolatility'
               ]

    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = [
        'pos',
        'currentSignal'
    ]

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, strategy_name, vt_symbol, setting):
        """Constructor"""
        super().__init__(ctaEngine, strategy_name, vt_symbol, setting)

        self.fastSignal = TurtleSignal(20, 10, 1, 0, 14, 10)
        self.slowSignal = TurtleSignal(50, 20, 1, 0, 14, 10)

        self.bg = BarGenerator(self.onBar)
        self.am = ArrayManager(60)

        self.dailyBar = None
        self.currentSignal = ""

        self.atrWindow = 20
        self.atrVolatility = 0
        self.multiplier = 0

    # ----------------------------------------------------------------------
    def on_init(self):
        """初始化策略（必须由用户继承实现）"""
        self.write_log(u'%s策略初始化' % self.className)

        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.load_bar(self.initDays)
        # for bar in initData:
        #     self.on_bar(bar)
        #
        # self.put_event()

    # ----------------------------------------------------------------------
    def on_start(self):
        """启动策略（必须由用户继承实现）"""
        self.write_log(u'%s策略启动' % self.className)
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop(self):
        """停止策略（必须由用户继承实现）"""
        self.write_log(u'%s策略停止' % self.className)
        self.put_event()

    # ----------------------------------------------------------------------
    def on_tick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.bg.update_tick(tick)

        # 没有仓位，则检查开仓
        if not self.pos:
            volume = self.tradingUnit * self.multiplier

            # 快速信号
            if tick.last_price >= self.fastSignal.entryUp:
                if (self.fastSignal.getLastPnl() <= 0 and
                        self.fastSignal.rsiValue >= 50 + self.fastSignal.rsiSignal):
                    self.buy(tick.limit_up, volume)
                    self.currentSignal = 'fast'

            elif tick.last_price <= self.fastSignal.entryDown:
                if (self.fastSignal.getLastPnl() <= 0 and
                        self.fastSignal.rsiValue <= 50 - self.slowSignal.rsiSignal):
                    self.short(tick.limit_down, volume)
                    self.currentSignal = 'fast'

            # 慢速信号
            elif tick.last_price >= self.slowSignal.entryUp:
                if (self.slowSignal.getLastPnl() <= 0 and
                        self.slowSignal.rsiValue >= 50 + self.fastSignal.rsiSignal):
                    self.buy(tick.limit_up, volume)
                    self.currentSignal = 'slow'

            elif tick.last_price <= self.slowSignal.entryDown:
                if (self.slowSignal.getLastPnl() <= 0 and
                        self.slowSignal.rsiValue <= 50 - self.fastSignal.rsiSignal):
                    self.short(tick.limit_down, volume)
                    self.currentSignal = 'slow'

        # 有多头仓位，则检查卖出平仓
        elif self.pos > 0:
            if self.currentSignal == 'fast':
                if tick.last_price <= self.fastSignal.exitDown:
                    self.sell(tick.limit_down, self.pos)
                    self.currentSignal = ''
            else:
                if tick.last_price <= self.slowSignal.exitDown:
                    self.sell(tick.limit_down, self.pos)
                    self.currentSignal = ''

        # 有空头仓位，则检查买入平仓
        else:
            if self.currentSignal == 'fast':
                if tick.last_price >= self.fastSignal.exitUp:
                    self.cover(tick.limit_up, abs(self.pos))
                    self.currentSignal = ''
            else:
                if tick.last_price >= self.slowSignal.exitUp:
                    self.cover(tick.limit_up, abs(self.pos))
                    self.currentSignal = ''


    # ----------------------------------------------------------------------
    def onBarBackTesting(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        # 没有仓位，则检查开仓
        if not self.pos:
            volume = self.tradingUnit * self.multiplier

            # 快速信号
            if bar.close >= self.fastSignal.entryUp:
                if (self.fastSignal.getLastPnl() <= 0 and
                        self.fastSignal.rsiValue >= 50 + self.fastSignal.rsiSignal):
                    self.buy(bar.high*110/100, volume)
                    self.currentSignal = 'fast'

            elif bar.close <= self.fastSignal.entryDown:
                if (self.fastSignal.getLastPnl() <= 0 and
                        self.fastSignal.rsiValue <= 50 - self.slowSignal.rsiSignal):
                    self.short(bar.low*90/100, volume)
                    self.currentSignal = 'fast'

            # 慢速信号
            elif bar.close >= self.slowSignal.entryUp:
                if (self.slowSignal.getLastPnl() <= 0 and
                        self.slowSignal.rsiValue >= 50 + self.fastSignal.rsiSignal):
                    self.buy(bar.high*110/100, volume)
                    self.currentSignal = 'slow'

            elif bar.close <= self.slowSignal.entryDown:
                if (self.slowSignal.getLastPnl() <= 0 and
                        self.slowSignal.rsiValue <= 50 - self.fastSignal.rsiSignal):
                    self.short(bar.low*90/100, volume)
                    self.currentSignal = 'slow'

        # 有多头仓位，则检查卖出平仓
        elif self.pos > 0:
            if self.currentSignal == 'fast':
                if bar.close <= self.fastSignal.exitDown:
                    self.sell(bar.low*90/100, self.pos)
                    self.currentSignal = ''
            else:
                if bar.close <= self.slowSignal.exitDown:
                    self.sell(bar.low*90/100, self.pos)
                    self.currentSignal = ''

        # 有空头仓位，则检查买入平仓
        else:
            if self.currentSignal == 'fast':
                if bar.close >= self.fastSignal.exitUp:
                    self.cover(bar.high*110/100, abs(self.pos))
                    self.currentSignal = ''
            else:
                if bar.close >= self.slowSignal.exitUp:
                    self.cover(bar.high*110/100, abs(self.pos))
                    self.currentSignal = ''

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""

        self.onBarBackTesting(bar)

        newDay = False
        if not self.dailyBar:
            newDay = True
        elif self.dailyBar.datetime.day != bar.datetime.day:
            newDay = True

            self.fastSignal.onBar(self.dailyBar)
            self.slowSignal.onBar(self.dailyBar)

            self.am.update_bar(self.dailyBar)
            if not self.pos:
                self.atrVolatility = self.am.atr(self.atrWindow)

                riskValue = self.capital * 0.01
                multiplier = riskValue / (self.atrVolatility * self.contractSize)
                self.multiplier = int(round(multiplier, 0))

        if newDay:
            self.dailyBar = BarData()
            self.dailyBar.datetime = bar.datetime.replace(hour=0, minute=0)

            self.dailyBar.open = bar.open
            self.dailyBar.high = bar.high
            self.dailyBar.low = bar.low
        else:
            self.dailyBar.high = max(self.dailyBar.high, bar.high)
            self.dailyBar.low = min(self.dailyBar.low, bar.low)

        self.dailyBar.close = bar.close

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """成交推送"""
        pass

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass

