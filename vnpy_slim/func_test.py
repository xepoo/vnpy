from time import sleep
count = 1
while True:
    sleep(1)
    count +=1
    print(count)




class vtest:
    a1 = 1
    a2 = 2

    def vprint(self):
        i = 1
        self.a1 = 4
        #self.names['a%s' % i] = 3
        exec('self.a{} = {}'.format(1, 3))
        exec('self.a{} = {}'.format(2, 4))
        print(self.a1)

    def aprint(self):
        print(self.a1)

v = vtest()
v.vprint()
v.aprint()
#
#
#
# list1 = [('a', 'A'), ('b', 'B'), ('c', 'C')]
# list2 = {'a':'A', 'b':'B', 'c':'C'}
# # list2 = {'inited' : True,
# #         'trading' : True,
# #         'pos' :5,
# #         'atr_value' :    6.4389915470190955,
# #         'rsi_f_value' :    84.56574577118519,
# #         'rsi_l_value' :    74.74754973400209,
# #         'rsi_max_value' :    84.56574577118519,
# #         'rsi_min_value' :    51.903967581432894,
# #         'intra_trade_high' :  2428.0,
# #         'intra_trade_low' :  2407.0,
# #         'long_stop' :0,
# #         'short_stop' :0}
#
#
# for x,(y,z) in enumerate(list2.items()):
#     print(x,y,z)



#g_db = 0
# def f1(v1):
#     global g_db
#     g_db = v1
#     print("f1:",g_db)
#
# def f2():
#     db = g_db
#     print("f2:", db)
#
# f1(1)
# f2()