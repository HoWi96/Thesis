# -*- coding: utf-8 -*-
"""
@date: 12/05/2019
@author: Holger
"""

#%% SET_UP

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% PREPROCESS DATA

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

#%% RELIABILITY

#Volume Reliability Estimation Function
#Output: (1) volume 
#Input: (1) interval (2) reliability
def calculateVolume(interval,errorbin,step,rel=0.99):

    #Initialize Parameters
    uncertaintyGuess = [0,1]
    count = 0
    rel_eff = -1
    volRef = interval.quantile(1-rel)
    volRefError = errorbin[volRef-volRef%step]
    uncertaintyGuessNew = -1
    volGuess = -1
    difference = -1
    intervalLength = len(interval)
    
    #Keep iterating while 
    #1 reliability is too far away
    #2 counter does not exceed 10 iterations
    while abs(rel_eff - rel) >.001 and count <10:
        
        #Calculate effective volume
        uncertaintyGuessNew = sum(uncertaintyGuess)/2
        volGuess =  volRef + volRefError.quantile(uncertaintyGuessNew)
    
        #calculate effective reliability
        uncertainty = np.zeros(intervalLength)
        for i,vol in enumerate(interval):
            difference = vol - volGuess
            values = errorbin[vol-vol%step]
            uncertainty[i] = sum(i<-difference for i in values)/len(values)
        rel_eff = 1-uncertainty.mean()
        
        #Iterate
        if rel_eff > rel:
            uncertaintyGuess[0] = uncertaintyGuessNew
        else:
            uncertaintyGuess[1] = uncertaintyGuessNew
              
        #Increase counter
        count+=1   
        
    return volGuess

#%% PROCESS
    
#Volume Bidding Function Given Market Constraints
#OUTPUT: (1) Bidded volumes (2) Illustration bidded volumes
#INPUT: (1) All Market Parameters
def bidVolume(df, TIME_TOTAL,TIME_HORIZON, TIME_GRANULARITY, VOLUME_GRANULARITY, VOLUME_MIN,RELIABILITY):

    #Dictionary with bins of errors
    indexbin = {}
    errorbin = {}
    step = 4
    minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
    maxbin = df[TIME_HORIZON].max()
    for i,x in enumerate(np.arange(minbin,maxbin,step)):
        indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
        errorbin[x] = df[0][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
        
    #volume = f(reliability,interval)
    bid = []
    for i in range(0,int(TIME_TOTAL/TIME_GRANULARITY)):
        interval = df[TIME_HORIZON][int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)]
        volume = calculateVolume(interval,errorbin,step,RELIABILITY)
        if volume < 0: 
            volume = 0
        bid = np.concatenate((bid, np.ones(int(TIME_GRANULARITY*4))*volume))   
    
    #Adjust for volume minimum
    bid2 = bid - bid%VOLUME_GRANULARITY
    
    #Adjust for volume minimum
    bid2[bid2<VOLUME_MIN] = 0
    
    #Illustrate bidding
    labelString =  ( str(TIME_HORIZON) + "h-Ahead,\n"
                   + str(TIME_GRANULARITY) + "h Resolution,\n"
                   + str(VOLUME_GRANULARITY) + "MW Resolution,\n"
                   + str(VOLUME_MIN) + "MW Minimum,\n"
                   + str(RELIABILITY*100) + "% Reliable")
    
    plt.plot(np.arange(0,TIME_TOTAL,0.25),
             bid2, 
             label = labelString,
             linestyle = "-", 
             linewidth=1.0)
    
    #Return bidding
    return bid2

#%% TESTS

plt.close("all")    

## REFERENCE PRODUCTION
#realTime = df[0][:TIME_TOTAL*4]
#plt.plot(np.arange(0,TIME_TOTAL,0.25), realTime, label = "Real-Time Production",linestyle = "-",linewidth=2.0)
#
## REFERENCE FORECAST
#TIME_HORIZON = 24
#forecast = df[TIME_HORIZON][:TIME_TOTAL*4]
#plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast, label = str(TIME_HORIZON)+"h-ahead Forecast",linestyle = "--")
 
#SPECIFICATIONS
TIME_TOTAL = 168
volume = bidVolume(df, TIME_TOTAL, 0, 0.25, 0.01, 0.01, 0.80)
volume = bidVolume(df, TIME_TOTAL, 24, 4, 1, 1, 0.80)

plt.legend()
plt.xlabel("Time [h]")
plt.ylabel("Volume [MW]")
plt.title("Downward Reserves 100MWp Wind\n\n"+"Time total "+str(TIME_TOTAL)+"h")
