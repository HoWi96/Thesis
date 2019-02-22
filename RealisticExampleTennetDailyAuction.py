# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 23:19:12 2018

@author: user
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.special

data = pd.read_csv("DataNovember.csv")
description = data.describe()
#stdSun2018 = description["SUN2018"]["std"]

SunMonitored2017 = 2952.78
SunMonitored2018 = 3369.05
WindMonitored2017 = 2621.92
WindMonitored2018 = 3157.19

#SCALE DATA
#----------
SunInstalled = 30
WindInstalled = 100

data["WIND2017"] = data["WIND2017"]*WindInstalled/WindMonitored2017 
data["WIND2018"] = data["WIND2018"]*WindInstalled/WindMonitored2018 
data["SUN2017"] = data["SUN2017"]*SunInstalled/SunMonitored2017 
data["SUN2018"] = data["SUN2018"]*SunInstalled/SunMonitored2018 
data["AGG2017"] = data["WIND2017"]+data["SUN2017"]
data["AGG2018"] = data["WIND2018"]+data["SUN2018"]

fig, ax = plt.subplots(1, 1)
quantile = np.linspace(0,1)
for i in range(1,8):
    agg = data.loc[range((i-1)*24*4,i*24*4)]["AGG2017"]
    plt.plot(quantile,agg.quantile(quantile),label=i)
plt.legend(bbox_to_anchor=(1, 1), title="Day")
fig.suptitle('Quantile Function AGGREGATOR')
plt.xlabel('Risk [-]')
plt.ylabel('Load Factor [%]')
plt.show()   

