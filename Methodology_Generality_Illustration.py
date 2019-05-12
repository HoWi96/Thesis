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
time = np.arange(0,72,0.25)

axes[0].plot(time,wind,color = "blue")
axes[0].fill_between(time,wind,np.where(wind>10, wind-10, 0),color = "blue",alpha = 0.1)
axes[0].plot(time,np.where(wind>10, wind-10, 0), color = "orange")
axes[0].fill_between(time,np.where(wind>10, wind-10, 0),0,color = "orange",alpha = 0.1)

axes[1].plot(time,solar,color = "blue")
axes[1].fill_between(time,solar,np.where(solar>10, solar-10, 0),color = "blue",alpha = 0.1)
axes[1].plot(time,np.where(solar>10, solar-10, 0), color = "orange")
axes[1].fill_between(time,np.where(solar>10, solar-10, 0),0,color = "orange",alpha = 0.1)


axes[2].fill_between(time,100,demand,color="orange",label = "Downward Flexibility",alpha = 0.1)
axes[2].plot(time,demand,label = "Real-Time Consumption",color = "blue")
axes[2].fill_between(time,30,demand,color="blue",label = "Upward Flexibility",alpha = 0.1)
axes[2].fill_between(time,30,0,color="green",label = "Shedding Limit (30MW)",alpha = 0.1)

#Annotations
titles = ["Flexibility Wind 100MWp","Flexibility Solar 100MWp","Flexibility Demand 100MWp"]

for i in (0,1,2):
    axes[i].set_title(titles[i])
    axes[i].set_ylim(0,100)
    axes[i].set_ylabel("Volume [MW]")
    axes[i].set_xlabel("Time [h]")
    axes[i].legend(("Real-Time Production","Curtailed Real-Time Production","Upward Flexibility (10MW)","Downward Flexibility"))
axes[2].legend()
