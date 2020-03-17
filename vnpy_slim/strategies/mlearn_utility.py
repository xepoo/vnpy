import numpy as np
from sklearn.neural_network import MLPClassifier
from vnpy.app.cta_strategy import (ArrayManager, BarData)
from vnpy.trader.constant import Direction
import joblib

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


class LSTM_Analyze(ArrayManager):
    def __init__(self, size=100):
        super().__init__(size)
        self.model = load_model('LSTM.h5')
        self.atr_value = 0
        self.rsi_value = 0
        self.cci_value = 0
        self.hist = 0
        self.std_value = 0
        self.percentage_value = 0
        self.trend = 0
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def get_x_y(self, data, N, offset):
        """
        Split data into x (features) and y (target)
        """
        x, y = [], []
        for i in range(offset, len(data)):
            x.append(data[i - N:i])
            y.append(data[i])
        x = np.array(x)
        y = np.array(y)

        return x, y

    def update_bar(self, bar: BarData):
        super().update_bar(bar)
        if self.inited == True:
            self.predict(60)

    def predict_close(self, n):
        close_in = self.scaler.fit_transform(self.close_array.reshape(-1, 1))
        close_in, _ = self.get_x_y(close_in, n, n)

        close_out = self.model.predict(close_in)
        close_out = self.scaler.inverse_transform(close_out)
        return close_out[-1]

    def predict(self, n):
        close_out = self.predict_close(n)
        if close_out > self.close_array[-1]:
            self.trend = Direction.LONG
        elif close_out < self.close_array[-1]:
            self.trend = Direction.SHORT
        else:
            self.trend = Direction.NET


class MLP_Analyze(ArrayManager):
    def __init__(self, size=100):
        super().__init__(size)
        self.clf = joblib.load('clf_selected.m')
        self.atr_value = 0
        self.rsi_value = 0
        self.cci_value = 0
        self.hist = 0
        self.std_value = 0
        self.percentage_value = 0
        self.trend = 0

    def percentage(self, array=False):
        v_percent = np.zeros(len(self.close))
        for i in range(1, len(self.close)):
            if self.close[i - 1] == 0.0:
                percentage = 0.0
            else:
                percentage = ((self.close[i] - self.close[i - 1]) /
                              self.close[i - 1]) * 100.0
            v_percent[i] = percentage
        v_percent[v_percent == 'nan'] = 0
        v_percent[v_percent == 'inf'] = 0
        if array:
            return v_percent
        else:
            return v_percent[-1]

    def update_bar(self, bar: BarData):
        super().update_bar(bar)
        if self.inited == True:
            self.predict()

    def predict(self, n=60):
        macd, signal, self.hist = self.macd(12, 26, 9, array=True)
        self.atr_value = self.atr(25, array=True)
        self.rsi_value = self.rsi(35, array=True)
        self.cci_value = self.cci(30, array=True)
        self.std_value = self.std(30, array=True)
        self.percentage_value = self.percentage(array=True)
        x = np.array([
            self.hist[-n:], self.atr_value[-n:], self.rsi_value[-n:],
            self.cci_value[-n:], self.std_value[-n:],
            self.percentage_value[-n:]
        ])
        x = x.T
        y = self.clf.predict(x)
        print(y)
        if y[-1] == 1:
            self.trend = Direction.LONG
        elif y[-1] == -1:
            self.trend = Direction.SHORT
        elif y[-1] == 0:
            self.trend = Direction.NET
