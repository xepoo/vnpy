from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager
)
from vnpy.trader.object import (
    BarData,
    TickData
)
from typing import Any

class DemoStrategy(CtaTemplate):
    """
    vnpy 实战进阶学习课程
    """
    author = 'Demo'
    #定义参数
    #快速均线窗口
    fast_window = 10
    #慢速均线窗口
    slow_window = 20

    #定义变量
    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0

    parameters = ['fast_window','slow_window']


    variables = [
        'fast_ma0',
        'fast_ma1',
        'slow_ma0',
        'slow_ma1',
    ]

    def __init__(
        self,
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,):
        super().__init__(
            cta_engine,strategy_name,
            vt_symbol,setting
            )
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(days = 10)

    def on_start(self):
        """启动"""
        self.write_log("策略启动")

    def on_stop(self):
        """停止"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """TICK更新"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """K线更新"""
        am = self.am
        am.update_bar(bar)
        if am.inited:
            return

        #计算技术指标
        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        #判断均线交叉
        #金叉
        cross_over = (self.fast_ma0 >= self.slow_ma0
        and self.fast_ma1 < self.slow_ma1)
        #死叉
        cross_below = (self.fast_ma0 <= self.slow_ma0
        and self.fast_ma1 > self.slow_ma1)

        if cross_over:
            price = bar.close_price + 5
            if not self.pos:
                self.buy(price,1)
            elif self.pos < 0:
                self.cover(price,1)
                self.buy(price,1)
        elif cross_below:
            price = bar.close_price - 5
            if not self.pos:
                self.short(price,1)
            elif self.pos > 0:
                self.sell(price,1)
                self.short(price,1)
        
        #更新图像界面
        self.put_event()
                    