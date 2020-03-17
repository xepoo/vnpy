from vnpy.app.cta_strategy import (CtaTemplate, StopOrder, TickData, BarData,
                                   TradeData, OrderData, BarGenerator)
from vnpy.trader.database import database_manager
from vnpy_slim.strategies.strategy_utility import get_trade_long_price, get_trade_short_price
from vnpy_slim.strategies.mlearn_utility import LSTM_Analyze  #,MLPAnalyze
from vnpy.trader.constant import Direction


class MLearnStrategy(CtaTemplate):
    """"""
    author = "用Python的交易员"

    load_bar_day = 20
    sl_multiplier = 7.6
    fixed_size = 1
    db_record = 0
    bar_window = 5
    bar_size = 100
    slippage_rate = 0.002

    direction = Direction.NET
    atr_value = 0
    trade_long_price = 0
    trade_short_price = 0
    intra_trade_high = 0
    intra_trade_low = 0
    long_stop = 0
    short_stop = 0
    atr_window = 30

    vt_xm_orderids = []

    parameters = [
        "load_bar_day", "sl_multiplier", "fixed_size", "db_record",
        "bar_window", "bar_size", "slippage_rate"
    ]
    variables = [
        "direction", "atr_value", "trade_long_price", "trade_long_price",
        "intra_trade_high", "intra_trade_low", "long_stop", "short_stop"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, self.bar_window, self.on_xmin_bar)
        #self.am_xm = MLP_Analyze(self.bar_size)
        self.am_xm = LSTM_Analyze(self.bar_size)

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
        self.bg.update_bar(bar)

    def on_xmin_bar(self, bar: BarData):
        """"""
        self.cancel_order_list(self.vt_xm_orderids)
        self.am_xm.update_bar(bar)
        if not self.am_xm.inited:
            return

        self.direction = self.am_xm.trend
        self.atr_value = self.am_xm.atr(self.atr_window)
        self.trade_long_price = get_trade_long_price(bar.close_price,
                                                     self.slippage_rate)
        self.trade_short_price = get_trade_short_price(bar.close_price,
                                                       self.slippage_rate)
        vt_orderids = []
        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.direction == Direction.LONG:
                vt_orderids = self.buy(self.trade_long_price, self.fixed_size)
            elif self.direction == Direction.SHORT:
                vt_orderids = self.short(self.trade_short_price,
                                         self.fixed_size)

            self.vt_xm_orderids.extend(vt_orderids)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price
            if self.direction == Direction.SHORT:
                vt_orderids = self.sell(self.trade_short_price, abs(self.pos))
            else:
                self.long_stop = self.intra_trade_high - self.atr_value * self.sl_multiplier
                vt_orderids = self.sell(self.long_stop, abs(self.pos), True)
            self.vt_xm_orderids.extend(vt_orderids)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            if self.direction == Direction.LONG:
                vt_orderids = self.cover(self.trade_long_price, abs(self.pos))
            else:
                self.short_stop = self.intra_trade_low + self.atr_value * self.sl_multiplier
                vt_orderids = self.cover(self.short_stop, abs(self.pos), True)
            self.vt_xm_orderids.extend(vt_orderids)

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
        # 数据库记录成交记录，bar记录，variables值
        if self.db_record:
            database_manager.save_trade_data(trade, self.get_variables())

        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
