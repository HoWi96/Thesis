# -*- coding: utf-8 -*-
"""
@date: 12/05/2019
@author: Holger
"""

#%% SET_UP

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% DATA PREPROCESSING

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
data2016 = pd.read_csv("Data/data2016.csv")

SOLAR_MONITORED = 2952.78
SOLAR_MONITORED2016 = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_MONITORED2016 = 1960.91
WIND_INSTALLED = 100

#Preprocess data
wind8760 = data2016["wind"]*WIND_INSTALLED/WIND_MONITORED2016
solar8760 = data2016["solar"]*SOLAR_INSTALLED/SOLAR_MONITORED2016
agg8760 = wind8760 + solar8760

wind168 = windRaw["168h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar168 = solarRaw["168h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg168 = wind168 + solar168

wind24 = windRaw["24h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar24 = solarRaw["24h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg24 = wind24 + solar24

wind5 = windRaw["5h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar3 = solarRaw["3h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg4 = wind5 + solar3

wind = windRaw["RealTime"]*WIND_INSTALLED/WIND_MONITORED
solar = solarRaw["RealTime"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg = wind + solar

#Place data in a dataframe, easy to handle
df = pd.DataFrame(data={0:wind,4:wind5,24:wind24,168:wind168,8760:wind8760})

#%% PARAMETERS
TIME_TOTAL = 168
TIME_HORIZON = 24
TIME_GRANULARITY = 4

VOLUME_GRANULARITY = 1
VOLUME_MIN = 1

UNCERTAINTY = 30
TIME_QUANTILE = 0

#%% PROCESS

# STEP 1 Retrieve a single valued forecast
forecast = wind[:TIME_TOTAL*4]

### STEP 2 Incorporate level of uncertainty
#2.1 Make a dictionary of errorbins
indexbin = {}
errorbin = {}
step = 4
minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
maxbin = df[TIME_HORIZON].max()
for i,x in enumerate(np.arange(minbin,maxbin,step)):
    indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
    errorbin[x] = df[0][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
    
# 2.2 Add forecast error
keys = (forecast-forecast%step).astype("int")
forecast2 = forecast + [errorbin[key].quantile(UNCERTAINTY/100) for key in keys]
forecast2[forecast2<0]=0

### STEP 3 Time Constraints
forecast3 = []
for i in range(0,int(TIME_TOTAL/TIME_GRANULARITY)):
    forecast3 = np.concatenate((forecast3, np.ones(int(TIME_GRANULARITY*4))*forecast2[int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)].quantile(TIME_QUANTILE/100)))

### STEP 4 Volume Constraints
forecast4 = forecast3 - forecast3%VOLUME_GRANULARITY
forecast4[forecast4<VOLUME_MIN] = 0

### STEP 5 Illustrations
plt.close("all")
plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast, label = "Unconstrained",linestyle = ":",linewidth=2.0)
plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast2, label = "Horizon Constrained",linestyle = "-")
plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast3, label = "Time Constrained",linestyle = ":",linewidth=2.0)
plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast4, label = "Volume Constrained",linestyle = "-")
plt.legend()
plt.xlabel("Time [h]")
plt.ylabel("Volume [MW]")
plt.title("Downward Reserves 100MWp Wind\n\n"+"Time total "+str(TIME_TOTAL)+"h")
