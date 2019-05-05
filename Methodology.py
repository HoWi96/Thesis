# -*- coding: utf-8 -*-
"""
Created on Sun May  5 11:03:30 2019

@author: user
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
df = pd.DataFrame(data={0:agg,4:agg4,24:agg24,168:agg168,8760:agg8760})
dfComponents = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})

#%% PARAMETERS

TIME_HORIZON = 24
TIME_GRANULARITY = 24

VOLUME_GRANULARITY = 2.5

UNCERTAINTY = 30
TIME_QUANTILE = 10

TIME_TOTAL = 168
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)

#%% PROCESS

plt.close("all")
plt.plot(np.arange(0,168,0.25),wind[:TIME_TOTAL*4],label = "Unconstrained Production")

# C1 TIME GRANULARITY------------
volumesC0 = []
for i in range(0,TIME_GROUPS):
    volumesC0 = np.concatenate((volumesC0, np.ones(TIME_GRANULARITY)*wind[int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)].quantile(TIME_QUANTILE/100)))
plt.plot(volumesC0, label = "Time Granularity "+str(TIME_GRANULARITY)+"h")

# C2 TIME HORIZON---------------
#REMARK: commutative property with time granularity
#Make a dictionary of indexbins and errorbins
indexbin = {}
errorbin = {}
step = 4
minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
maxbin = df[TIME_HORIZON].max()

#Iterate over all bins
for i,x in enumerate(np.arange(minbin,maxbin,step)):
    indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
    errorbin[x] = df[0][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]

#add forecast error
keys = (volumesC0-volumesC0%step).astype("int")
volumesC1 = volumesC0 + [errorbin[key].quantile(UNCERTAINTY/100) for key in keys]
volumesC1[volumesC1<0]=0

plt.plot(volumesC1, label = "Time Horizon " +str(TIME_HORIZON)+"h")

#C3 VOLUME GRANULARITY------------
volumesC2 = volumesC1 - volumesC1%VOLUME_GRANULARITY
plt.plot(volumesC2, label = "Volume Granularity "+str(VOLUME_GRANULARITY)+"MW")

plt.legend()
plt.xlabel("Time [h]")
plt.ylabel("Volume [MW]")
plt.title("Impact on 100MWp wind over 1 week\n"+"Uncertainty "+str(UNCERTAINTY)+"%, Time quantile "+str(TIME_QUANTILE)+"%")
