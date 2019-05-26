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
solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")["0"]
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")["0"]
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")["0"]

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
agg = solar*0.25 + wind*0.75

#%% ILLUSTRATION UP & DOWN

#initialize
time = np.arange(0,72,0.25)
titles = ["(a) Solar PV 100MWp","(b) Wind 100MWp","(c) Aggregator 100MWp","(d) Demand 100MWp (SL = 50MW)"]
suptitle = (r"$\bf Flexibility \: by \: Uncertain \: Sources$"+"\nSimulation Time 72h")

#compute
plt.close("all")
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

#Make different plots
axes[0,0].plot(time,wind,color = "blue")
axes[0,0].fill_between(time,wind,np.where(wind>10, wind-10, 0),color = "blue",alpha = 0.1)
axes[0,0].plot(time,np.where(wind>10, wind-10, 0), color = "orange")
axes[0,0].fill_between(time,np.where(wind>10, wind-10, 0),0,color = "orange",alpha = 0.1)

axes[0,1].plot(time,solar,color = "blue")
axes[0,1].fill_between(time,solar,np.where(solar>10, solar-10, 0),color = "blue",alpha = 0.1)
axes[0,1].plot(time,np.where(solar>10, solar-10, 0), color = "orange")
axes[0,1].fill_between(time,np.where(solar>10, solar-10, 0),0,color = "orange",alpha = 0.1)

axes[1,0].plot(time,agg,color = "blue")
axes[1,0].fill_between(time,agg,np.where(agg>10, agg-10, 0),color = "blue",alpha = 0.1)
axes[1,0].plot(time,np.where(agg>10, agg-10, 0), color = "orange")
axes[1,0].fill_between(time,np.where(agg>10, agg-10, 0),0,color = "orange",alpha = 0.1)
axes[1,0].plot(time,0.25*solar,color = "gold",linestyle =":",linewidth =3)
#axes[1,0].fill_between(time,0,0.25*solar,color = "gold",alpha = 0.1)
legendAgg = ("Potential Realtime Generation", "Effective Realtime Generation","Solar PV 25MWp", "Upward Flexibility 10MW","Downward Flexibility")

axes[1,1].fill_between(time,100,demand,color="orange",alpha = 0.1)
axes[1,1].plot(time,demand,color = "blue")
axes[1,1].fill_between(time,50,demand,color="blue",alpha = 0.1)
axes[1,1].fill_between(time,50,0,color="green",alpha = 0.1)
legendDemand = ("Effective Realtime Consumption","Downward Flexibility", "Upward Flexibility", "Shedding Limit 50MW")

#Annotations
for j in range(4):
    axes[int(j/2),j%2].set_title(titles[j])
    axes[int(j/2),j%2].set_ylim(0,100)
    axes[int(j/2),j%2].set_ylabel("Volume [MW]")
    axes[int(j/2),j%2].set_xlabel("Time [h]")
    axes[int(j/2),j%2].legend(("Potential Realtime Generation","Effective Realtime Generation","Upward Flexibility 10MW ","Downward Flexibility"))
axes[1,0].legend(legendAgg)
axes[1,1].legend(legendDemand)
