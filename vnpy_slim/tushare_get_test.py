import tushare as ts
ts.set_token('3313904c0168e7bee0811581a6c668a2236a261475987a71640bb140')
pro = ts.pro_api()

df = ts.pro_bar(ts_code='CFFEX.IF1901', asset='FT', start_date='20180101', end_date='20191011')
print(df)