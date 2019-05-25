# -*- coding: utf-8 -*-
"""
@date: 12/05/2019
@author: Holger
"""

#%% IMPORT

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    volRefError = errorbin[interval.quantile(0.5)-interval.quantile(0.5)%step]
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
        interval = df[TIME_HORIZON][int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)+1]
        volume = calculateVolume(interval,errorbin,step,RELIABILITY)
        if volume < 0: 
            volume = 0
        bid = np.concatenate((bid, np.ones(int(TIME_GRANULARITY*4))*volume))   
    
    #Adjust for volume minimum
    bid2 = bid - bid%VOLUME_GRANULARITY
    
    #Adjust for volume minimum
    bid2[bid2<VOLUME_MIN] = 0
    
    #Illustrate bidding
    labelString =  ( "--------------------------\n"
                    + str(TIME_HORIZON) + "h-Ahead Forecast,\n"
                    + str(TIME_GRANULARITY) + "h Resolution,\n"
                    + str(VOLUME_GRANULARITY) + "MW Resolution,\n"
                    + str(VOLUME_MIN) + "MW Minimum,\n"
                    + str(RELIABILITY*100) + "% Reliable")
    
    plt.plot(np.arange(0,TIME_TOTAL,0.25),
             bid2, 
             label = labelString,
             linestyle = "-", 
             linewidth=1)
    
    #Return bidding
    return bid2

#%%  TESTS
    
if __name__ == "__main__":
    
    print("START Methodology Intergation Volumes")
    
    #%% IMPORT
    solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
    windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
    demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")
    allRaw2016 = pd.read_csv("Data/data2016.csv")
    
    #%% PREPROCESS DATA
    
    WIND_INST = 2403.17
    SOLAR_INST= 2952.78
    DEMAND_PK= 11742.29
    
    WIND_INST2016 = 1960.91
    SOLAR_INST2016= 2952.78
    DEMAND_PK2016 = 11589.6
    
    solar = solarRaw.loc[:, solarRaw.columns != "DateTime"]*100/SOLAR_INST
    solar["8760"] = allRaw2016["solar"]*100/SOLAR_INST2016
    
    wind = windRaw.loc[:, windRaw.columns != "DateTime"]*100/WIND_INST
    wind["8760"] = allRaw2016["wind"]*100/WIND_INST2016
    
    demand = demandRaw.loc[:, demandRaw.columns != "DateTime"]*100/DEMAND_PK
    demand["8760"] = allRaw2016["load"]*100/DEMAND_PK2016
    
    agg = solar*0.25+wind*0.75
    
    #Place data in a dataframe, easy to handle
    df = pd.DataFrame(data={0:wind["0"],
                            4:wind["4"],
                            24:wind["24"],
                            168:wind["168"],
                            8760:wind["8760"]})
    
    #%% ILLUSTRATE
    plt.close("all")    
    
    TIME_TOTAL = 168
    
    # REFERENCE PRODUCTION
    realTime = df[0][:TIME_TOTAL*4]
    plt.plot(np.arange(0,TIME_TOTAL,0.25), realTime, label = "Realtime Generation",linestyle = ":",linewidth=1.5)
    
    # REFERENCE FORECAST
#    TIME_HORIZON = 24
#    forecast = df[TIME_HORIZON][:TIME_TOTAL*4]
#    plt.plot(np.arange(0,TIME_TOTAL,0.25), forecast, label = "--------------------------\n"+str(TIME_HORIZON)+"h-Ahead Forecast",linestyle = "-",linewidth=1)
    
    #SPECIFICATIONS
    #volume = bidVolume(df, TIME_TOTAL, 24, 0.25, 0.01, 0.01, 0.95)
    #volume = bidVolume(df, TIME_TOTAL, 24, 12.00, 0.01, 0.01, 0.95)
    volume = bidVolume(df, TIME_TOTAL, 24, 12.00, 1, 5, 0.95)
    
    plt.legend()
    plt.xlabel("Time [h]")
    plt.ylabel("Volume [MW]")
    plt.ylim((0,100))
    plt.title("Downward Reserves 100MWp Wind, "+"Time Total "+str(TIME_TOTAL)+"h")
    plt.legend(bbox_transform=plt.gcf().transFigure)
    
    print("\a")
    print("STOP Methodology Intergation Volumes")
