# -*- coding: utf-8 -*-
"""
@date: 12/05/2019
@author: Holger
"""

#%% IMPORT

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

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
        errorbin[x] = df["0"][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
        
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
    
    labelString =  ( "--------------------------\n"
                + str(TIME_HORIZON) + "h-Ahead Forecast,\n"
                + str(TIME_GRANULARITY) + "h Resolution,\n"
                + str(VOLUME_GRANULARITY) + "MW Resolution,\n"
                + str(VOLUME_MIN) + "MW Minimum,\n"
                + str(RELIABILITY*100) + "% Reliable")

    #Return bidding
    return bid2,labelString

def financialComputation(df,TIME_TOTAL,accuracy=0.1,figure = "optimum"):
    #CONSTANTS#
    bidCapacity = 6 #€/MW/h
    bidEnergy = 120 #€/MWh
    tests = 52/52 #tests/week
    activations = 4/52 #activations/week
    durationCapacity = 168 #hours/week
    durationMonth = 720 #hours/month
    durationActivation = 1 #hours
    tariff = 120 #€/MWh
    factor = 2
    
    #VOLUMES&RELIABILITY#
    realizedVolumes,ignore = bidVolume(df, TIME_TOTAL, str(0), 0.25, 0.01, 0.01, 0.5)
    reliabilities = np.arange(0,1+0.01,accuracy)
    volumeCapacity = np.zeros(reliabilities.shape)
    volumeMissing = np.zeros(reliabilities.shape)
    volumeLost = np.zeros(reliabilities.shape)
    
    for k,reliability in enumerate(reliabilities):
        volumes,labelString = bidVolume(df, TIME_TOTAL, str(24), 12.00, 5, 10, reliability)
        volumeCapacity[k] = np.mean(volumes)
        differenceVolumes = realizedVolumes-volumes
        volumeMissing[k] = -np.sum(differenceVolumes[differenceVolumes<0])/(TIME_TOTAL*4)
        volumeLost[k] = np.sum(differenceVolumes[differenceVolumes>0])/(TIME_TOTAL*4)   
    volumeActivation = volumeCapacity
    
    #FORMULAS#
    penaltyMonitoring = volumeMissing*factor*bidCapacity*durationMonth
    penaltyActivation = volumeMissing*tariff*durationActivation

    revenuesCapacity =  volumeCapacity*bidCapacity*durationCapacity
    revenuesEnergy =    activations*volumeActivation*bidEnergy*durationActivation
    costsMonitoring =   np.matmul(np.diag(1-reliabilities),tests*penaltyMonitoring)
    costsActivation =   np.matmul(np.diag(1-reliabilities),activations*penaltyActivation)
    
    revenuesTotal = revenuesCapacity + revenuesEnergy
    costsTotal = costsMonitoring + costsActivation
    revenuesNet = revenuesTotal - costsTotal
    
    #Illustrate
    plt.figure() 
    
    if figure == "optimum":
        
        plt.plot(reliabilities*100,revenuesNet/10**3, label = "Expected Net Revenues",linewidth = 2)
        plt.plot(reliabilities*100,revenuesTotal/10**3,label= "Expected Total Revenues",linestyle = "--")
        plt.plot(reliabilities*100,costsTotal/10**3, label = "Expected Total Costs",linestyle = "--")
        #The optimum
        x = reliabilities[np.argmax(revenuesNet)]*100
        y = np.amax(revenuesNet)/10**3
        plt.plot([x], [y], 'o',color = "C0", label = "Optimum of "+str(round(y,1))+"k€/week\nReliability "+str(round(x,1))+"%")
        plt.title(r"$\bf Financial \: Optimum$"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        
    if figure == "revenues":
        
        plt.plot(reliabilities*100,revenuesTotal/10**3,label= "Expected Total Revenues",linewidth = 2)
        plt.plot(reliabilities*100,revenuesCapacity/10**3,label= "Expected Capacity Revenues",linestyle = "--")
        plt.plot(reliabilities*100,revenuesEnergy/10**3,label= "Expected Energy Revenues",linestyle = "--")
        plt.title(r"$\bf Revenues \: Components$"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        
    if figure == "costs":
        
        plt.plot(reliabilities*100,costsTotal/10**3, label = "Expected Total Costs",linewidth = 2)
        plt.plot(reliabilities*100,costsMonitoring/10**3,label= "Expected Test Costs",linestyle = "--")
        plt.plot(reliabilities*100,costsActivation/10**3,label= "Expected Activation Costs",linestyle = "--")
        plt.title(r"$\bf Cost \: Components$"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        
    plt.xlim(0,100)
    plt.ylim(0)
    plt.legend() 
    plt.xlabel("Reliability [%]")
    plt.ylabel("Revenues [k€/Week]")  
    
    return revenuesNet,revenuesTotal,costsTotal,volumeMissing,volumeLost,volumeCapacity
    

#%%  TESTS
    
if __name__ == "__main__":
    
    print("START Methodology")
    
    #close all plots
    plt.close("all") 
    
    #PREPROCESS
    solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
    solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
    df = wind
    
    VOLUME_METHODOLOGY = True
    FINANCIALS_METHODOLOGY = False
    
    if VOLUME_METHODOLOGY == True:
        print("START Volumes")
    
        #select the simulation time
        TIME_TOTAL = 168
        
        #forecasted volumes
        forecast = df["24"][:TIME_TOTAL*4]
        plt.plot(np.arange(0,TIME_TOTAL,0.25),forecast, label = "24h-Ahead Forecast",linestyle = "-",linewidth=1)
        
        #realized volumes
        #realTime = df["0"][:TIME_TOTAL*4]
        #plt.plot(np.arange(0,TIME_TOTAL,0.25), realTime, label = "Realized Generation",linestyle = "-",linewidth=1)
        #plt.title(r"$\bf Forecast \: Procurement \: Period $"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        
        #bid volumes
        #volumes,labelString = bidVolume(df, TIME_TOTAL, str(24), 0.25, 0.01, 0.01, 0.95)
        #plt.title(r"$\bf Product \: Time \: Resolution $"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        #volumes,labelString = bidVolume(df, TIME_TOTAL, str(24), 12.00, 0.01, 0.01, 0.95)
        #plt.title(r"$\bf Product \: Time \: Resolution $"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        volumes,labelString = bidVolume(df, TIME_TOTAL, str(24), 12.00, 5, 10, 0.95)
        plt.title(r"$\bf Product \: Volume \: Resolution \: And \: Minimum$"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        
        #Illustrate bidding
        plt.plot(np.arange(0,TIME_TOTAL,0.25),volumes,label = labelString,linestyle = "-", linewidth=1)
        plt.legend()
        plt.xlabel("Time [h]")
        plt.ylabel("Volume [MW]")
        plt.ylim((0,100))
    
    if FINANCIALS_METHODOLOGY == True:
        print("START Financials")
        
        #compute the financial consequences
        revenuesNet,revenuesTotal,costsTotal,volumeMissing,volumeLost,volumeCapacity = financialComputation(df,TIME_TOTAL,accuracy=0.01,figure = "costs")
        
        #Illustrate effect on volumes
        reliabilities = np.arange(0,1+0.01,0.01)
        plt.figure()
        plt.plot(reliabilities*100,volumeCapacity,label = "Mean Offered Volume")
        plt.plot(reliabilities*100,volumeMissing, label = "Mean Missing Volume",linestyle = "--")
        plt.plot(reliabilities*100,volumeLost, label = "Mean Lost Volume",linestyle = "--")
        plt.title(r"$\bf Reliability \: Influences \: Bids$"+"\nSimulation 168h, Downward Reserves 100MWp Wind")
        plt.legend()
        plt.xlabel("Reliability [%]")
        plt.ylabel("Volume [MW]")
        plt.ylim(0)
        plt.xlim(0,100)
    
    
    print("STOP Methodology")
    print("\a")
