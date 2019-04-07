# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:45:52 2019
@title: Assess Uncertainty on forecast vs uncertainty on time
@author: HoWi96
"""

# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.special
from mpl_toolkits import mplot3d

# In[] Upload Data

solarData = pd.read_csv("Data/SolarForecastJune2017.csv")
windData = pd.read_csv("Data/WindForecastJune2017.csv")
WINDINSTALLED = 2403.17
SOLARINSTALLEDD = 2952.78    

#solarData.describe()
#solarData["3h-ahead"]
#solarData["24h-ahead"]
#solarData["168h-ahead"]
#solarData["RealTime"]
#
#windData.describe()
#windData["5h-ahead"]
#windData["24h-ahead"]
#windData["168h-ahead"]
#windData["RealTime"]

plt.close("all")
wdata5h = (windData["5h-ahead"]-windData["RealTime"])/WINDINSTALLED*100
wdata24h = (windData["24h-ahead"]-windData["RealTime"])/WINDINSTALLED*100
wdata168h = (windData["168h-ahead"]-windData["RealTime"])/WINDINSTALLED*100
sdata3h = (solarData["3h-ahead"]-solarData["RealTime"])/SOLARINSTALLEDD*100
sdata24h = (solarData["24h-ahead"]-solarData["RealTime"])/SOLARINSTALLEDD*100
sdata168h = (solarData["168h-ahead"]-solarData["RealTime"])/SOLARINSTALLEDD*100

title1 = "Forecast Error Wind GCT 5h"
title2 = "Forecast Error Wind GCT 24h"
title3 = "Forecast Error Wind GCT 168h"
title4 = "Forecast Error Solar GCT 3h"
title5 = "Forecast Error Solar GCT 24h"
title6 = "Forecast Error Solar GCT 168h"

fig, axes = plt.subplots(2, 3)
wdata5h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,0], xlim = (-40,40),  title = title1)
wdata24h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,1], xlim = (-40,40),  title = title2)
wdata168h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,2], xlim = (-40,40), title = title3)
sdata3h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,0],xlim = (-40,40),  title = title4)
sdata24h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,1],xlim = (-40,40),  title = title5)
sdata168h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,2],xlim = (-40,40),  title = title6)

x = np.linspace(0,1,50)
fig,axes = plt.subplots(2,3)
axes[0,0].plot(x,wdata5h.quantile(x)+100)
axes[0,1].plot(x,wdata24h.quantile(x)+100)
axes[0,2].plot(x,wdata168h.quantile(x)+100)
axes[1,0].plot(x,sdata3h.quantile(x)+100)
axes[1,1].plot(x,sdata24h.quantile(x)+100)
axes[1,2].plot(x,sdata168h.quantile(x)+100)

axes[0,0].set_title(title1)
axes[0,1].set_title(title2)
axes[0,2].set_title(title3)
axes[1,0].set_title(title4)
axes[1,1].set_title(title5)
axes[1,2].set_title(title6)

for i,j in ([0,0],[0,1],[0,2],[1,0],[1,1],[1,2]):
    axes[i,j].set_ylabel("$\Delta$P [%MW]")
    axes[i,j].set_xlabel("Uncertainty [%]")
    
## Descriptive Statistics
dataError24h = np.vstack((wdata24h,sdata24h))
#print(np.mean(wdata24h), "% overestimation wind")
#print(np.mean(sdata24h), "% overestimation solar")
#print(np.std(wdata24h), "% standard deviation wind")
#print(np.std(sdata24h), "% stadard deviation solar")
print(np.mean(dataError24h,1)," % overestimation wind + % overestimation solar")
print(np.cov(dataError24h),"covariance matrix wind (Row1) and solar (Row2)")
print(np.corrcoef(dataError24h),"correlation matrix wind (Row1) and solar (Row2)")
fig,ax = plt.subplots()
ax.plot(sdata24h,wdata24h,'o',color="black")
ax.set_xlabel("Solar Data Overestimation 24h [%]")
ax.set_ylabel("Wind Data Overestimation 24h [%]")
ax.set_title("Simultaneous Error 24h")



