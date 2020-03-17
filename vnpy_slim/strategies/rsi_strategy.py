from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.database import database_manager
from vnpy_slim.strategies.strategy_utility import if_keep_grow,if_keep_reduce,grow_rate
from datetime import time

class RSIStrategy(CtaTemplate):
    """"""

    author = "用Python的交易员"

    no_trade_time_begin1 = time(hour=9, minute=0)
    no_trade_time_end1 = time(hour=9, minute=30)
    no_trade_time_begin2 = time(hour=23, minute=0)
    no_trade_time_end2 = time(hour=23, minute=30)

    load_bar_day = 20

    boll_window = 16
    boll_dev = 2.6
    # cci_window = 10
    atr_window = 30
    # atr_ma_window = 10
    rsi_f_window = 5
    rsi_l_window = 10
    grow_window = 5
    reduce_window = 5
    # rsi_entry = 16
    # ma_window = 5
    sl_multiplier = 7.6
    fixed_size = 1
    db_record = 0
    bar_size = 100

    boll_up = 0
    boll_down = 0
    # cci_value = 0
    atr_value = 0
    # atr_ma = 0

    rsi_f_value = 0
    rsi_l_value = 0
    rsi_max_value = 0
    rsi_min_value = 0
    rsi_f_ma = 0
    rsi_l_ma = 0

    intra_trade_high = 0
    intra_trade_low = 0
    long_stop = 0
    short_stop = 0

    vt_1m_orderids = []
    vt_15m_orderids = []

    parameters = ["boll_window", "boll_dev", "atr_window", "rsi_f_window", "rsi_l_window","grow_window","reduce_window","sl_multiplier","fixed_size","bar_size","db_record"]
    variables = ["boll_up", "boll_down", "atr_value", "rsi_f_value", "rsi_l_value","rsi_f_ma", "rsi_l_ma", "rsi_max_value","rsi_min_value","intra_trade_high",
                 "intra_trade_low", "long_stop", "short_stop"]

    # parameters = ["boll_window", "boll_dev", "cci_window","rsi_window","rsi_entry","ma_window",
    #               "atr_window","atr_ma_window","sl_multiplier", "fixed_size"]
    # variables = ["boll_up", "boll_down", "cci_value", "atr_value","atr_ma","rsi_value",
    #              "intra_trade_high", "intra_trade_low", "long_stop", "short_stop"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

#todo,多时间周期，分长短期，判断不同的指标
        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        #self.am_1m = ArrayManager()
        self.am_15m = ArrayManager(self.bar_size)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.load_bar_day)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        # self.cancel_order_list(self.vt_1m_orderids)
        # self.am_1m.update_bar(bar)
        # if not self.am_1m.inited:
        #     return
        # # #todo 1分钟的策略
        #
        # self.boll_up, self.boll_down = self.am_1m.boll(self.boll_window, self.boll_dev)
        # self.atr_value = self.am_1m.atr(self.atr_window)
        # rsi_f_array = self.am_1m.rsi(self.rsi_f_window, array=True)
        # rsi_l_array = self.am_1m.rsi(self.rsi_l_window, array=True)
        # self.rsi_f_value = rsi_f_array[-1]
        # self.rsi_l_value = rsi_l_array[-1]
        #
        # if self.pos == 0:
        #     self.intra_trade_high = bar.high_price
        #     self.intra_trade_low = bar.low_price
        #
        #     # todo,波动不够大，应该过滤
        #     if self.rsi_f_value > self.rsi_l_value and if_keep_grow(self.grow_window, rsi_f_array):
        #         vt_orderids = self.buy(self.boll_up, self.fixed_size, True)
        #         self.vt_1m_orderids.extend(vt_orderids)
        #     elif self.rsi_f_value < self.rsi_l_value and if_keep_reduce(self.reduce_window, rsi_f_array):
        #         vt_orderids = self.short(self.boll_down, self.fixed_size, True)
        #         self.vt_1m_orderids.extend(vt_orderids)
        # # todo，持续范围内小波动，震荡策略
        #
        #
        #
        # elif self.pos > 0:
        #     self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
        #     self.intra_trade_low = bar.low_price
        #     if if_keep_reduce(self.reduce_window, rsi_f_array):  # self.rsi_f_value < self.rsi_l_value and
        #         vt_orderids = self.sell(bar.close_price - 5, abs(self.pos))
        #     else:
        #         self.long_stop = self.intra_trade_high - self.atr_value * self.sl_multiplier
        #         vt_orderids = self.sell(self.long_stop, abs(self.pos), True)
        #     self.vt_1m_orderids.extend(vt_orderids)
        # elif self.pos < 0:
        #     self.intra_trade_high = bar.high_price
        #     self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
        #     if if_keep_grow(self.grow_window, rsi_f_array):  # self.rsi_f_value > self.rsi_l_value and
        #         vt_orderids = self.cover(bar.close_price + 5, abs(self.pos))
        #     else:
        #         self.short_stop = self.intra_trade_low + self.atr_value * self.sl_multiplier
        #         vt_orderids = self.cover(self.short_stop, abs(self.pos), True)
        #     self.vt_1m_orderids.extend(vt_orderids)
        # if self.db_record:
        #     database_manager.save_bar_calc(bar, self.get_variables())
        #
        # self.put_event()

        self.bg.update_bar(bar)

    def on_15min_bar(self, bar: BarData):
        """"""
        self.cancel_order_list(self.vt_15m_orderids)
        self.am_15m.update_bar(bar)
        if not self.am_15m.inited:
            return

        self.boll_up, self.boll_down = self.am_15m.boll(self.boll_window, self.boll_dev)
        #self.cci_value = am.cci(self.cci_window)
        self.atr_value = self.am_15m.atr(self.atr_window)
        # atr_array = am.atr(self.atr_window, array=True)
        # self.atr_value = atr_array[-1]
        #self.atr_ma = atr_array[-self.atr_ma_window:].mean()
        rsi_f_array = self.am_15m.rsi(self.rsi_f_window, array=True)
        rsi_l_array = self.am_15m.rsi(self.rsi_l_window, array=True)
        # self.rsi_max_value = rsi_f_array[-self.rsi_f_window:].max()
        # self.rsi_min_value = rsi_f_array[-self.rsi_f_window:].min()
        # self.rsi_f_ma = rsi_f_array[-self.rsi_f_window:].mean()
        # self.rsi_l_ma = rsi_f_array[-self.rsi_f_window:].mean()
        self.rsi_f_value = rsi_f_array[-1]
        self.rsi_l_value = rsi_l_array[-1]

        #self.ma_value = am.sma(self.ma_window)

        # if (bar.datetime.time() >= self.no_trade_time_begin1 and bar.datetime.time() <= self.no_trade_time_end1) \
        #         or (bar.datetime.time() >= self.no_trade_time_begin2 and bar.datetime.time() <= self.no_trade_time_end2):
        #     return

        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

#todo,波动不够大，应该过滤
            #if self.rsi_f_value > 50 and self.rsi_f_value > self.rsi_l_value and if_keep_grow(self.grow_window, rsi_f_array) and self.rsi_f_value < 85: #self.rsi_f_value>=self.rsi_max_value:
            if self.rsi_f_value > self.rsi_l_value :#and if_keep_grow(self.grow_window, rsi_f_array):
                #self.buy(bar.close_price+5, self.fixed_size)
                vt_orderids = self.buy(self.boll_up, self.fixed_size, True)
                self.vt_15m_orderids.extend(vt_orderids)
            #elif self.rsi_f_value < 50 and self.rsi_f_value < self.rsi_l_value and if_keep_reduce(self.reduce_window, rsi_f_array) and self.rsi_f_value >15: #self.rsi_f_value <=self.rsi_min_value:
            elif self.rsi_f_value < self.rsi_l_value :# and if_keep_reduce(self.reduce_window, rsi_f_array):
                #self.short(bar.close_price-5, self.fixed_size)
                vt_orderids = self.short(self.boll_down, self.fixed_size, True)
                self.vt_15m_orderids.extend(vt_orderids)
#todo，持续范围内小波动，震荡策略


        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price
            if  if_keep_reduce(self.reduce_window, rsi_f_array):#self.rsi_f_value < self.rsi_l_value and
                vt_orderids = self.sell(bar.close_price-5, abs(self.pos))
            else:
                self.long_stop = self.intra_trade_high - self.atr_value * self.sl_multiplier
                vt_orderids = self.sell(self.long_stop, abs(self.pos), True)
            self.vt_15m_orderids.extend(vt_orderids)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            if if_keep_grow(self.grow_window, rsi_f_array): #self.rsi_f_value > self.rsi_l_value and
                vt_orderids = self.cover(bar.close_price + 5, abs(self.pos))
            else:
                self.short_stop = self.intra_trade_low + self.atr_value * self.sl_multiplier
                vt_orderids = self.cover(self.short_stop, abs(self.pos), True)
            self.vt_15m_orderids.extend(vt_orderids)

        if self.db_record:
            database_manager.save_bar_calc(bar, self.get_variables())

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        #数据库记录成交记录，bar记录，variables值
        if self.db_record:
            database_manager.save_trade_data(trade, self.get_variables())

        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
