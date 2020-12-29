import xalpha as xa
import pandas as pd
import matplotlib.pyplot as plt


zzhli = xa.get_daily("SH501018", start="20150101")
max = zzhli['close'].max()
min = zzhli['close'].min()
cur = zzhli[-1:]['close']
print(max)
print(min)
print((cur - min )/(max - min))
print((cur - min )/(min))
#x = zzhli['date']
#y = zzhli['close']
#print(zzhli)
#plt.plot(x, y)
#plt.show()