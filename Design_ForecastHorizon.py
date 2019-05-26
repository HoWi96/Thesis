# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:45:52 2019
@title: Assess Uncertainty on forecast vs uncertainty on time
@author: HoWi96
"""
#IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

#PREPROCESS
solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df0 = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})

#%%PROCESS

#initialize
RELIABILITY = 95
horizons = ["0","4","24","168","8760"]
volume = np.zeros((len(horizons),df0.shape[1]))

#compute
for j,source in enumerate([solar,wind,agg,demand,solar*0.25,wind*0.75]):
    for i,horizon in enumerate(horizons):
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
            errorbin[x] = source["0"][indexbin[x]]-df[indexbin[x]]
        
        for k,vol in enumerate(source[horizon]):
            volRefError = errorbin[vol-vol%step]
            new[k] =  vol + volRefError.quantile((100-RELIABILITY)/100)
        volume[i,j] = np.mean(new)

#%% ILLUSTRATE

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
suptitle = (r"$\bf Impact \: Forecast \: Horzion$"+"\nSimulation Time 720h\n"+ "0h-Ahead Forecast, "+ "95% Reliability, "+ "0.01$\Delta$MW Resolution, "+ "0.01MW Minimum ")

#compute
plt.close("all")
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

#iterate over sources
for k,source in enumerate(["solar","wind","agg","demand"]):
    
    #mean bid volume
    MBV = volume[:,k]
    
    #mean effective volume
    MEV = np.ones(len(horizons))*df0[source].mean()
    
    axes[int(k/2),k%2].plot(horizons,MBV,linewidth=1.5)
    axes[int(k/2),k%2].plot(horizons,MEV,linewidth=1.5)
    axes[int(k/2),k%2].fill_between(horizons,MBV,MEV,color = "orange",alpha = 0.1)
    axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Lost Volume"))
    axes[int(k/2),k%2].set_xlabel('Forecast Horizon [h]')
    axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
    axes[int(k/2),k%2].set_ylim(0,31)
    axes[int(k/2),k%2].set_title(titles[k]) 
    
    #mean added volume
    if source == "agg":
        reference = volume[:,4]+volume[:,5]
        
        axes[int(k/2),k%2].plot(horizon,reference,linewidth=1.5,linestyle ='--')
        axes[int(k/2),k%2].fill_between(horizon,MBV,reference,color = "green",alpha = 0.2)
        axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Seperated Volume","Mean Lost Volume","Mean Added Volume"))