# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:45:52 2019
@title: Assess Uncertainty on forecast vs uncertainty on time
@author: HoWi96
"""
#IMPORTS

import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

#PREPROCESS
solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)

#%%PROCESS

#initialize
RELIABILITY = 95
bidVolume = np.zeros((5,4))
horizons = ["0","4","24","168","8760"]

#compute
for j,source in enumerate([solar,wind,agg,demand]):
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
        bidVolume[i,j] = np.mean(new)

#%% ILLUSTRATE

plt.close("all")
fig,axes = plt.subplots(2,2)
horizons = ["0","4","24","168","8760*"]
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
plt.suptitle("Impact Forecast Horizon\nSimulation Time 720h, Reliability "+str(RELIABILITY)+"%")

for k,source in enumerate([solar,wind,agg,demand]):
    
    #mean bid volume
    MBV = bidVolume[:,k]
    
    #mean effective volume
    MEV = np.ones(len(horizons))*source["0"].mean()
    
    axes[int(k/2),k%2].plot(horizons,MBV,linewidth=1.5)
    axes[int(k/2),k%2].plot(horizons,MEV,linewidth=1.5)
    axes[int(k/2),k%2].fill_between(horizons,MBV,MEV,color = "orange",alpha = 0.1)
    axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Lost Volume"))
    axes[int(k/2),k%2].set_xlabel('Forecast Horizon [h]')
    axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
    axes[int(k/2),k%2].set_ylim(0,32)
    axes[int(k/2),k%2].set_title(titles[k]) 
