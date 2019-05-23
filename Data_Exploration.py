# -*- coding: utf-8 -*-
"""
Created on Wed May 22 10:26:16 2019

@author: user
"""

#%% IMPORTS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")
allRaw2016 = pd.read_csv("Data/data2016.csv")

#%% DATA PREPROCESSING

WIND_INST = 2403.17
SOLAR_INST= 2952.78
DEMAND_PK= 11742.29

WIND_INST2016 = 1960.91
SOLAR_INST2016= 2952.78
DEMAND_PK2016 = 11589.6

#Preprocess solar
solar = solarRaw.loc[:, solarRaw.columns != "DateTime"]*100/SOLAR_INST
solar[str(8760)] = allRaw2016["solar"]*100/SOLAR_INST2016

#Preprocess wind
wind = windRaw.loc[:, windRaw.columns != "DateTime"]*100/WIND_INST
wind[str(8760)] = allRaw2016["wind"]*100/WIND_INST2016

#Preprocess demand
demand = demandRaw.loc[:, demandRaw.columns != "DateTime"]*100/DEMAND_PK
demand[str(8760)] = allRaw2016["load"]*100/DEMAND_PK2016
demand = demand - 30 #shedding limit

#Preprocess aggregator
agg = solar*0.3+wind*0.4+demand*0.3

#Reorganize in dataframe
df = pd.DataFrame(data={"wind":wind[str(0)],
                                  "solar":solar[str(0)],
                                  "aggregator":agg[str(0)],
                                  "demand":demand[str(0)]})

#%% DATA EXPLORATION

#Delete previous plots
plt.close("all")

#Visualisation Time Series
df.plot()
plt.ylabel("Power [MW]")
plt.xlabel("Time [15']")

#Visualisation Probability Density Function
df.plot.kde()
plt.xlabel("Power [MW]")

#visualisation Quantile Function
plt.figure()
quantiles = np.arange(0,1.01,.01)

#Plot all quantile plots
plot1 = plt.plot(quantiles*100,df.quantile(quantiles))

#Plot added value quantile plot
addedValue = df["aggregator"].quantile(quantiles) - df["solar"].quantile(quantiles) - df["wind"].quantile(quantiles)
plot2 =plt.plot(quantiles*100,addedValue)

plt.plot([np.where(addedValue>0)[0].max()], [addedValue[np.where(addedValue>0)[0].max()/100]], 'o')

labels = list(df)
labels.append("Added Value Aggregator")
plot = plot1+plot2
plt.legend(plot, labels)
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')

#%% ILLUSTRATE ERROR BINS
df = wind
TIME_HORIZON = str(8760)#h

indexbin = {}
errorbin = {}
errQ = list()
errN = list()
step = 4
x = 0
minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
maxbin = df[TIME_HORIZON].max()


for i,x in enumerate(np.arange(minbin,maxbin,step)):
    indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
    errorbin[x] = df[str(0)][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
    errQ.append(errorbin[x].quantile(0.9))
    errN.append(len(errorbin[x]))
    
#Illustrate standard deviation per bin
fig,axes = plt.subplots(1,2)
axes[0].plot(np.arange(minbin,maxbin,step),errQ)
axes[1].plot(np.arange(minbin,maxbin,step),errN)

#Illustrate error bins
fig,axes = plt.subplots(2,3)
for i,x in enumerate(np.arange(minbin,maxbin,16)):
    errorbin[x].plot.density(ax = axes[int(i/3),i%3])
    axes[int(i/3),i%3].set_title("Error bin of " + str(x) + "MW")
    
#%% Make some music
    
#import winsound
#duration = 2000  # milliseconds
#freq = 247  # Hz
#winsound.Beep(freq*2, duration)
#winsound.Beep(196*2, duration)
#winsound.Beep(247*2, duration)
#winsound.Beep(165*2, duration)
#winsound.Beep(196*2, duration)
#winsound.Beep(165*2, duration)
#winsound.Beep(247*2, duration)
#winsound.Beep(185*2, duration)
    