# -*- coding: utf-8 -*-
"""
@date: 12/05/2019
@author: Holger
"""

# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

# In[] PREPROCESS DATA

#upload data
solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")["RealTime"]
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")["RealTime"]
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")["RealTime"]

#monitored volumes
WIND_MON = 2424.07
SOLAR_MON= 2952.78
DEMAND_MON = 11742.29

#installed volumes
WIND_INS = 100
SOLAR_INS= 100
DEMAND_INS = 100

#rescale
START = 24*4*4
STOP = 24*7*4
wind = windRaw[START:STOP]*WIND_INS/WIND_MON
solar = solarRaw[START:STOP]*SOLAR_INS/SOLAR_MON
demand = demandRaw[START:STOP]*DEMAND_INS/DEMAND_MON

#%% ILLUSTRATION UP & DOWN

plt.close("all")
fig,axes = plt.subplots(3,1)

#Make different plots
time = np.arange(START/4,STOP/4,0.25)

axes[0].plot(time,wind)
axes[0].plot(time,np.where(wind>5, wind-5, 0))
axes[0].plot(time,np.ones(time.shape)*5)

axes[1].plot(time,solar)
axes[1].plot(time,np.where(solar>5, solar-5, 0))
axes[1].plot(time,np.where(solar>5, 5, 0))

axes[2].plot(time,demand)
axes[2].plot(time,np.where(demand>5, demand-5, 0))
axes[2].plot(time,np.ones(time.shape)*5)

#Annotations
titles = ["Wind Production","Solar Production","Demand Production"]

for i in (0,1,2):
    axes[i].set_title(titles[i])
    axes[i].set_ylim(0,100)
    axes[i].set_ylabel("Volume [MW]")
    axes[i].set_xlabel("Time [h]")
    axes[i].legend(("Production","Downward Reserves","Upward Reserves"))
