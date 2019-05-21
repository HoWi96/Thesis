# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:45:52 2019
@title: Assess Uncertainty on forecast vs uncertainty on time
@author: HoWi96
"""
#%% IMPORTS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")
allRaw2016 = pd.read_csv("Data/data2016.csv")

#%% PREPROCESS

WIND_INST = 2403.17
SOLAR_INST= 2952.78
DEMAND_PK= 11742.29

WIND_INST2016 = 1960.91
SOLAR_INST2016= 2952.78
DEMAND_PK2016 = 11589.6

solar = solarRaw.loc[:, solarRaw.columns != "DateTime"]*100/SOLAR_INST
solar["8760h-ahead"] = allRaw2016["solar"]*100/SOLAR_INST2016

wind = windRaw.loc[:, windRaw.columns != "DateTime"]*100/WIND_INST
wind["8760h-ahead"] = allRaw2016["wind"]*100/WIND_INST2016

demand = demandRaw.loc[:, demandRaw.columns != "DateTime"]*100/DEMAND_PK
demand["8760h-ahead"] = allRaw2016["load"]*100/DEMAND_PK2016

agg = solar*0.25+wind*0.75

#%% Create Errorbins
plt.close("all")
RELIABILITY = 90
lostVolume = np.zeros((5,4))

for j,source in enumerate([solar,wind,agg,demand]):
    for i,horizon in enumerate(["RealTime","4h-ahead","24h-ahead","168h-ahead","8760h-ahead"]):
        df = source[horizon]
        new = np.zeros(df.shape)
    
        #Dictionary with bins of errors
        indexbin = {}
        errorbin = {}
        step = 4
        minbin = round(df.min()- df.min()%step)
        maxbin = df.max()
        for x in np.arange(minbin,maxbin,step):
            indexbin[x] = np.where(np.column_stack((df>(x-step*1.5),df<(x+step*1.5))).all(axis=1))[0]
            errorbin[x] = source["RealTime"][indexbin[x]]-df[indexbin[x]]
        
        for k,vol in enumerate(source[horizon]):
            volRefError = errorbin[vol-vol%step]
            new[k] =  vol + volRefError.quantile((100-RELIABILITY)/100)
        
#        plt.figure()
#        plt.plot(df)
#        plt.plot(new)
        lostVolume[i,j] = np.mean(source["RealTime"]-new)

plt.close("all")
horizons = ["0","4","24","168","8760*"]
plt.plot(horizons,lostVolume)
plt.xlabel('Forecast Horizon [h]')
plt.ylabel('Lost Volume [MW]')
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 30MW)"]
plt.legend(titles)
plt.title("Lost Volume By Forecast Horizon"+
             "\nMean Effective Volume"+
             " (a) "+str(round(solar["RealTime"].mean(),1))+"MW"+
             " (b) "+str(round(wind["RealTime"].mean(),1))+"MW"+
             " (c) "+str(round(agg["RealTime"].mean(),1))+"MW"+
             " (d) "+str(round(demand["RealTime"].mean()-30,1))+"MW")
            
        

#Reliability quantile error bins
# adjust forecast
#subtract real-time
#mean
