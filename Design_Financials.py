# -*- coding: utf-8 -*-
"""
Created on Sun May 26 23:34:08 2019

@author: user
"""
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre
import pandas as pd

#PREPROCESS
solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})

#%% PROCESS
print("START monitoring design")

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
horizon = "24"
accuracy = 0.01
totalTime = 720
reliabilities = 1-np.arange(0,1+0.01,accuracy)
volume = np.zeros((len(reliabilities),df.shape[1]))
volumeMissing = np.zeros((len(reliabilities),df.shape[1]))
volumeLost = np.zeros((len(reliabilities),df.shape[1]))

print("START bid creation")
#compute
for j,source in enumerate([solar,wind,agg,demand,solar*0.25,wind*0.75]):
    print("Bid Creation Source "+str(j))
    realizedVolumes = np.ones(df.shape[0])*np.mean(source["0"])
    df = source[horizon]
    
    for i,reliability in enumerate(reliabilities):
        new = np.zeros(df.shape)
        
        #Dictionary with bins of errors
        indexbin = {}
        errorbin = {}
        step = 4
        minbin = round(df.min()- df.min()%step)
        maxbin = df.max()
        for x in np.arange(minbin,maxbin,step):
            indexbin[x] = np.where(np.column_stack((df>(x-step*1.5),df<(x+step*1.5))).all(axis=1))[0]
            errorbin[x] = source["0"][indexbin[x]]-df[indexbin[x]]
        
        #Compute volume with required reliability
        for k,vol in enumerate(source[horizon]):
            volRefError = errorbin[vol-vol%step]
            new[k] =  vol + volRefError.quantile(1-reliability)
         
        #Prepare volumes to return
        volume[i,j] = np.mean(new)
        differenceVolumes = realizedVolumes-new
        volumeMissing[i,j] = -np.sum(differenceVolumes[differenceVolumes<0])/(totalTime*4)
        volumeLost[i,j] = np.sum(differenceVolumes[differenceVolumes>0])/(totalTime*4)
        
print("Bids finished")

plt.close("all")

col = ["C0",'C1','C2','C3','C4','C5','C6']
fig,axes = plt.subplots(2,2)
suptitle = (r"$\bf Impact \: Reliability $"+"\nSimulation of 720h\n"+ "24h-Ahead Forecast, "+ "0.25h Resolution, " + "0.01MW Resolution, "+ "0.01MW Minimum ")
plt.suptitle(suptitle)
for k,source in enumerate(["solar","wind","agg","demand"]):
     axes[int(k/2),k%2].plot(reliabilities*100, volume[:,k],label = "MOV (Mean Offered Volume)")
     axes[int(k/2),k%2].plot(reliabilities*100, volumeMissing[:,k],label = "MMV (Mean Missing Volume)")
     axes[int(k/2),k%2].plot(reliabilities*100, volumeLost[:,k],label = "MLV (Mean Lost Volume)")

     if source == "agg":
         volumeRef = volume[:,4]+volume[:,5]
         volumeMissingRef = volumeMissing[:,4]+volumeMissing[:,5]
         volumeLostRef = volumeLost[:,4]+volumeLost[:,5]
         
         axes[int(k/2),k%2].plot(reliabilities*100,volumeRef, linestyle ='-.', label = "MOV - Sources seperated", color = col[0])
         axes[int(k/2),k%2].plot(reliabilities*100,volumeMissingRef,linestyle ='-.',label = "MMV - Sources seperated",color = col[1])
         axes[int(k/2),k%2].plot(reliabilities*100,volumeLostRef,linestyle ='-.', label = "MLV - Sources seperated",color = col[2])
     
     axes[int(k/2),k%2].legend()
     axes[int(k/2),k%2].set_xlabel("Reliability [%]")
     axes[int(k/2),k%2].set_ylabel("Volume [MW]")
     axes[int(k/2),k%2].set_ylim(0)
     axes[int(k/2),k%2].set_xlim(0,100)
     axes[int(k/2),k%2].set_title(titles[k])
     
#%%     
print("Start Financial Impact")

#%initialize
fig,axes = plt.subplots(2,2)
sensitivities = enumerate([-0.5,0,0.5,1.5,3])

volumeCapacity = volume
volumeActivation = volume
volumeMissing = volumeMissing

parameter = "penalty"
plt.suptitle(r"$\bf Sensitivity \: Analysis \: of \: Test \: Costs \: on \: Expected \: Net \: Revenues$"+"\nSimulation of 720h"+"\nReference Test Frequency = 1/month, Reference Test Penalty = 4.32k€/missing MW")

#compute
for n,sensitivity in sensitivities:
    print("sensitivity "+str(sensitivity))
    
    if parameter == "penalty":
        legend = sensitivity*100
        tests = 12/12 #tests/month
        factor = 1*(1+sensitivity) #€/MWh
        
    #CONSTANTS#
    bidCapacity = 6 #€/MW/h
    bidEnergy = 120 #€/MWh
    activations = 4/12 #activations/month
    durationCapacity = 720 #hours/week
    durationMonth = 720 #hours/month
    durationActivation = 0.5 #hour
    tariff = 120 #€/MWh

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
    
    # ILLUSTRATE
    col = ["C0",'C1','C2','C3','C4','C5','C6']

    #initialize
    for k,source in enumerate(["solar","wind","agg","demand"]):
        axes[int(k/2),k%2].plot(reliabilities*100, revenuesNet[:,k]/10**3,label = "Sensitivity "+str(legend)+"%",color =col[n])
        #axes[int(k/2),k%2].plot(reliabilities*100, revenuesTotal[:,k]/10**3,linestyle ="--",linewidth=0.5)
        #axes[int(k/2),k%2].plot(reliabilities*100, costsTotal[:,k]/10**3,linestyle = "--",linewidth=0.5)
        
        if source == "agg":
             revenuesRef = revenuesNet[:,4]+revenuesNet[:,5]
             axes[int(k/2),k%2].plot(reliabilities*100,revenuesRef/10**3, linestyle ='-.',linewidth = 0.5, color =col[n])

        ##RECOMMENDATION ------------------
        x = reliabilities[np.argmax(revenuesNet[:,k])]*100
        y = np.amax(revenuesNet[:,k])/10**3
        axes[int(k/2),k%2].plot([x], [y], 'o',color =col[n])
        
        axes[int(k/2),k%2].set_xlabel("Reliability [%]")
        axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
        axes[int(k/2),k%2].legend()
        axes[int(k/2),k%2].set_ylim(0)
        axes[int(k/2),k%2].set_xlim(60,100)
        axes[int(k/2),k%2].set_title(titles[k])
