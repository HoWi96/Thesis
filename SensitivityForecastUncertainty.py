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

fig, axes = plt.subplots(2, 3)
wdata5h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,0], xlim = (-40,40),  title = "Forecast Error Wind GCT 5h")
wdata24h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,1], xlim = (-40,40),  title = "Forecast Error Wind GCT 24h")
wdata168h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[0,2], xlim = (-40,40), title = "Forecast Error Wind GCT 168h")
sdata3h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,0],xlim = (-40,40),  title = "Forecast Error Solar GCT 3h")
sdata24h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,1],xlim = (-40,40),  title = "Forecast Error Solar GCT 24h")
sdata168h.plot(kind='hist',bins = 20, color='lightblue', ax = axes[1,2],xlim = (-40,40),  title = "Forecast Error Solar GCT 168h")



