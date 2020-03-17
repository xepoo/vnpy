import pandas as pd
import numpy as np
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
import matplotlib.pyplot as plt
import pymysql
from sklearn.preprocessing import MinMaxScaler
import math
from sklearn.metrics import mean_squared_error

import tensorflow as tf
#进行配置，使用30%的GPU
config = tf.compat.v1.ConfigProto()
config.gpu_options.allocator_type = 'BFC'  #A "Best-fit with coalescing" algorithm, simplified from a version of dlmalloc.
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)

CONST_TRAINING_SEQUENCE_LENGTH = 60
CONST_TESTING_CASES = 5


class LSTMDataAnalysis(object):
    def __init__(
            self,
            exportpath="D:\\SynologyDrive\\future_data\\",
            datformat=['datetime', 'high', 'low', 'open', 'close', 'volume']):
        self.collection = None
        self.df = pd.DataFrame()
        self.exportpath = exportpath
        self.datformat = datformat
        self.startBar = 2
        self.endBar = 12
        self.step = 2
        self.pValue = 0.05

    #-----------------------------------------导入数据-------------------------------------------------
    def db2df(self,
              symbol,
              start,
              end,
              mysqlhost="localhost",
              mysqlport=3306,
              user="root",
              password="root",
              database="",
              export2csv=False):
        """读取MongoDB数据库行情记录，输出到Dataframe中"""
        self.collection = symbol
        conn = pymysql.connect(host=mysqlhost,
                               port=mysqlport,
                               user=user,
                               password=password,
                               database=database,
                               charset='utf8',
                               use_unicode=True)
        sql = "SELECT `datetime`, `high_price` as `high`, `low_price` as `low`, `open_price` as `open`, `close_price` as `close`, `volume` " \
              "FROM dbbardata where symbol='%s' and `datetime`>str_to_date('%s','%%Y-%%m-%%d') and `datetime`<str_to_date('%s','%%Y-%%m-%%d')" % (symbol, start, end)
        self.df = pd.read_sql(sql=sql, con=conn)
        self.df = self.df[self.datformat]
        self.df = self.df.reset_index(drop=True)
        print(sql)
        print(self.df.shape)
        path = self.exportpath + self.collection + ".csv"
        if export2csv == True:
            self.df.to_csv(path, index=True, header=True)
        return self.df

    def csv2df(self, csvpath, dataname="csv_data", export2csv=False):
        """读取csv行情数据，输入到Dataframe中"""
        csv_df = pd.read_csv(csvpath)
        self.df = csv_df[self.datformat]
        self.df["datetime"] = pd.to_datetime(self.df['datetime'])
        self.df = self.df.reset_index(drop=True)
        path = self.exportpath + dataname + ".csv"
        if export2csv == True:
            self.df.to_csv(path, index=True, header=True)
        return self

    def df2Barmin(self, inputdf, barmins, crossmin=1, export2csv=False):
        """输入分钟k线dataframe数据，合并多多种数据，例如三分钟/5分钟等，如果开始时间是9点1分，crossmin = 0；如果是9点0分，crossmin为1"""
        dfbarmin = pd.DataFrame()
        highBarMin = 0
        lowBarMin = 0
        openBarMin = 0
        volumeBarmin = 0
        datetime = 0
        for i in range(0, len(inputdf) - 1):
            bar = inputdf.iloc[i, :].to_dict()
            if openBarMin == 0:
                openBarmin = bar["open"]
            if highBarMin == 0:
                highBarMin = bar["high"]
            else:
                highBarMin = max(bar["high"], highBarMin)
            if lowBarMin == 0:
                lowBarMin = bar["low"]
            else:
                lowBarMin = min(bar["low"], lowBarMin)
            closeBarMin = bar["close"]
            datetime = bar["datetime"]
            volumeBarmin += int(bar["volume"])
            # X分钟已经走完
            if not (bar["datetime"].minute + crossmin) % barmins:  # 可以用X整除
                # 生成上一X分钟K线的时间戳
                barMin = {
                    'datetime': datetime,
                    'high': highBarMin,
                    'low': lowBarMin,
                    'open': openBarmin,
                    'close': closeBarMin,
                    'volume': volumeBarmin
                }
                dfbarmin = dfbarmin.append(barMin, ignore_index=True)
                highBarMin = 0
                lowBarMin = 0
                openBarMin = 0
                volumeBarmin = 0
        if export2csv == True:
            dfbarmin.to_csv(self.exportpath + "bar" + str(barmins) +
                            str(self.collection) + ".csv",
                            index=True,
                            header=True)
        return dfbarmin

    def dataNormalization(self, data):
        return [(datum - data[0]) / data[0] for datum in data]

    def dataDeNormalization(self, data, base):
        return [(datum + 1) * base for datum in data]

    def split_data(self, df: pd.DataFrame, test_size):
        num_test = int(test_size * len(df))
        num_train = len(df) - num_test
        print("num_train = " + str(num_train))
        print("num_test = " + str(num_test))

        # Split into train, cv, and test
        train = df[:num_train][['datetime', 'close', 'open']]
        test = df[num_train:][['datetime', 'close', 'open']]

        return train, test

        # # Step 1. 取close列
        # #df = df[['open','close','high','low','volume']].values
        # df = df['close'].tolist()
        # # Step 2. Building Training data
        # dataTraining = []
        # for i in range(
        #         len(df) -
        #         CONST_TESTING_CASES * CONST_TRAINING_SEQUENCE_LENGTH):
        #     dataSegment = df[i:i + CONST_TRAINING_SEQUENCE_LENGTH + 1]
        #     dataTraining.append(self.dataNormalization(dataSegment))

        # dataTraining = np.array(dataTraining)
        # np.random.shuffle(dataTraining)
        # X_Training = dataTraining[:, :-1]
        # Y_Training = dataTraining[:, -1]

        # print("X_Training:",X_Training[-1])
        # print("X_Training:",Y_Training[-1])

        # # Step 3. Building Testing data
        # X_Testing = []
        # Y_Testing_Base = []
        # for i in range(CONST_TESTING_CASES, 0, -1):
        #     dataSegment = df[-(i + 1) * CONST_TRAINING_SEQUENCE_LENGTH:-i *
        #                      CONST_TRAINING_SEQUENCE_LENGTH]
        #     Y_Testing_Base.append(dataSegment[0])
        #     X_Testing.append(self.dataNormalization(dataSegment))

        # Y_Testing = df[-CONST_TESTING_CASES * CONST_TRAINING_SEQUENCE_LENGTH:]

        # X_Testing = np.array(X_Testing)
        # Y_Testing = np.array(Y_Testing)

        # # Step 4. Reshape for deep learning
        # X_Training = np.reshape(X_Training,
        #                         (X_Training.shape[0], X_Training.shape[1], 1))
        # X_Testing = np.reshape(X_Testing,
        #                        (X_Testing.shape[0], X_Testing.shape[1], 1))

        # return X_Training, Y_Training, X_Testing, Y_Testing, Y_Testing_Base

    def get_x_y(self, data, N):
        """
        Split data into x (features) and y (target)
        """
        x, y = [], []
        for i in range(N, len(data)):
            x.append(data[i - N:i])
            y.append(data[i][0])
        x = np.array(x)
        y = np.array(y)

        return x, y

    def get_learn_data(self, df, test_size, N):
        train, test = DA.split_data(df, test_size)

        scaler = MinMaxScaler(feature_range=(0, 1))
        train_scaled = scaler.fit_transform(
            np.array(train[['close','open']]).reshape(-1, 2))

        # Scale the cv dataset according the min and max obtained from train set
        test_scaled = scaler.transform(np.array(test[['close','open']]).reshape(-1, 2))

        scaler2 = MinMaxScaler(feature_range=(0, 1))
        y = scaler2.fit_transform(np.array(test['close']).reshape(-1, 1))

        # Split train into x and y
        x_train_scaled, y_train_scaled = DA.get_x_y(train_scaled, N)
        # Split cv into x and y
        x_test_scaled, y_test_scaled = DA.get_x_y(test_scaled, N)
        return x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, test, scaler, scaler2

    def predict(self, model, X):
        predictionsNormalized = []

        for i in range(len(X)):
            data = X[i]
            result = []

            for j in range(CONST_TRAINING_SEQUENCE_LENGTH):
                predicted = model.predict(data[np.newaxis, :, :])[0, 0]
                result.append(predicted)
                data = data[1:]
                data = np.insert(data, [CONST_TRAINING_SEQUENCE_LENGTH - 1],
                                 predicted,
                                 axis=0)

            predictionsNormalized.append(result)

        return predictionsNormalized

    def plotResults(self, Y_Hat, Y):
        print("y.shape", Y.shape)
        print("Y_Hat.shape", Y_Hat.shape)

        Y_Hat = pd.DataFrame({'Y_Hat': Y_Hat.reshape(-1), 
                       'datetime': Y['datetime'][-len(Y_Hat):]})

        ax = Y.plot(x='datetime', y='close', style='b-', grid=True)
        ax = Y_Hat.plot(x='datetime', y='Y_Hat', style='r-', grid=True, ax=ax)
        ax.legend(['Y', 'Y_Hat'])
        ax.set_xlabel("datetime")
        ax.set_ylabel("rmb")
        plt.show()

        # for i in range(len(Y_Hat)):
        #     padding = [None for _ in range(i * CONST_TRAINING_SEQUENCE_LENGTH)]
        #     plt.plot(padding + Y_Hat[i])

        #plt.show()

    def get_mape(self, y_true, y_pred):
        """
        Compute mean absolute percentage error (MAPE)
        """
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def train_pred_eval_model(self,
                              x_train,
                              y_train,
                              x_test,
                              y_test,
                              test_base,
                              scaler,
                              scaler2,
                              lstm_units=50,
                              dropout_prob=0.5,
                              optimizer='adam',
                              epochs=1,
                              batch_size=1):
        '''
        Train model, do prediction, scale back to original range and do evaluation
        Use LSTM here.
        Returns rmse, mape and predicted values
        Inputs
            x_train  : e.g. x_train.shape=(451, 9, 1). Here we are using the past 9 values to predict the next value
            y_train  : e.g. y_train.shape=(451, 1)
            x_test     : use this to do predictions 
            y_test     : actual value of the predictions (scaled)
            scaler          : scaler that is used to fit_transform train set
            lstm_units      : lstm param
            dropout_prob    : lstm param
            optimizer       : lstm param
            epochs          : lstm param
            batch_size      : lstm param
        Outputs
            rmse            : root mean square error
            mape            : mean absolute percentage error
            est             : predictions
        '''
        # Create the LSTM network
        print("x_train.shape:", x_train.shape)
        model = Sequential()
        model.add(
            LSTM(units=lstm_units,
                 return_sequences=True,
                 input_shape=(x_train.shape[1], 2)))
        model.add(
            Dropout(dropout_prob))  # Add dropout with a probability of 0.5
        model.add(LSTM(units=lstm_units))
        model.add(
            Dropout(dropout_prob))  # Add dropout with a probability of 0.5
        model.add(Dense(1))

        # Compile and fit the LSTM network
        model.compile(loss='mean_squared_error', optimizer=optimizer)
        model.fit(x_train,
                  y_train,
                  epochs=epochs,
                  batch_size=batch_size,
                  verbose=0)

        # Do prediction
        print("x_test.shape:", x_test.shape)
        y_predict = model.predict(x_test)
        
        y_predict = scaler2.inverse_transform(y_predict)

        # Get correct scale of y_cv
        y_test = scaler2.inverse_transform(y_test.reshape(-1,1))

        # Calculate RMSE and MAPE
        rmse = math.sqrt(mean_squared_error(y_test, y_predict))
        mape = self.get_mape(y_test, y_predict)

        print("y_test.shape:", y_test.reshape(-1).shape)
        print("y_predict.shape:", y_predict.reshape(-1).shape)
        print("test_base.shape:", np.array(test_base['close']).reshape(-1)[-360:].shape)
        dfresult = pd.DataFrame({'Actual': y_test.reshape(-1), 'Predict': y_predict.reshape(-1), 'base': np.array(test_base['close']).reshape(-1)[-360:]})
        dfresult.to_csv(exportpath + "result2" + ".csv", index=True, header=True)

        return rmse, mape, y_predict

 
if __name__ == '__main__':
    # 读取数据
    exportpath = "D:\\SynologyDrive\\future_data\\"
    DA = LSTMDataAnalysis(exportpath)
    #数据库导入
    start = "2016-05-01"
    end = "2016-07-01"
    df = DA.db2df(symbol="cmain",
                  start=start,
                  end=end,
                  mysqlhost="localhost",
                  mysqlport=3306,
                  user="root",
                  password="root",
                  database="futures_schema")

    test_size = 0.2  # proportion of dataset to be used as test set
    #cv_size = 0.2  # proportion of dataset to be used as cross-validation set
    N = 9  # for feature at day t, we use lags from t-1, t-2, ..., t-N as features.
    lstm_units = 50  # lstm param. initial value before tuning.
    dropout_prob = 1  # lstm param. initial value before tuning.
    optimizer = 'adam'  # lstm param. initial value before tuning.
    epochs = 1  # lstm param. initial value before tuning.
    batch_size = 1  # lstm param. initial value before tuning.

    df = DA.df2Barmin(df, 5)
    x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, test_base, scaler,scaler2 = DA.get_learn_data(
        df, test_size, N)

    print(df.head())

    rmse, mape, y_predict = DA.train_pred_eval_model(x_train_scaled,
                             y_train_scaled,
                             x_test_scaled,
                             y_test_scaled,
                             test_base,
                             scaler,
                             scaler2,
                             lstm_units=50,
                             dropout_prob=1.0,
                             optimizer='nadam',
                             epochs=50,
                             batch_size=8)

    # # Step 2. Build model
    # model = Sequential()

    # model.add(LSTM(input_dim=1, output_dim=50, return_sequences=True))
    # model.add(Dropout(0.2))

    # model.add(LSTM(200, return_sequences=False))
    # model.add(Dropout(0.2))

    # model.add(Dense(output_dim=1))
    # #model.add(Activation('linear'))tanh
    # model.add(Activation('tanh'))

    # model.compile(loss='mse', optimizer='rmsprop')

    # # Step 3. Train model
    # model.fit(X_Training,
    #           Y_Training,
    #           batch_size=512,
    #           nb_epoch=5,
    #           validation_split=0.05)

    # plot_model(model, to_file='model.png')
    # # Step 4. Predict
    # predictionsNormalized = DA.predict(model, X_Testing)

    # # Step 5. De-nomalize
    # predictions = []
    # for i, row in enumerate(predictionsNormalized):
    #     predictions.append(DA.dataDeNormalization(row, Y_Testing_Base[i]))

    # Step 6. Plot
    print("y_predict:", y_predict.shape)
    print("test_base:", test_base.shape)
    DA.plotResults(y_predict, test_base)

    #model.save("LSTM.h5")
