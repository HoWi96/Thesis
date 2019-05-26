# -*- coding: utf-8 -*-
"""
Created: May 2019
@author: Holger
"""

#%%IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})
dfArray = np.array(df)

#%% PROCESS

#initialize
granularities = np.arange(0.01,5,0.01)
volumeRes = np.zeros((granularities.shape[0],dfArray.shape[1]))
volumeMin = np.zeros((granularities.shape[0],dfArray.shape[1]))

#compute
for j,gran in enumerate(granularities):
    
    #compute volume resolution
    volumeRes[j,:] = (dfArray-dfArray%gran).mean(axis=0)
    
    #compute volume minimum
    dfArrayCopy = dfArray.copy()
    np.place(dfArrayCopy,[dfArray<gran],0)
    volumeMin[j,:] = dfArrayCopy.mean(axis=0)

#%% ILLUSTRATE

#initialize
plt.close("all")
xlabels = ['Volume Resolution [$\Delta$MW]','Volume Minimum [MW]']
suptitles = [(r"$\bf Impact \: Volume \: Resolution$"+"\nSimulation Time 720h\n"+ "0h-Ahead Forecast, "+ "0.25$\Delta$h Resolution, "+ " - % Reliability, "+ "0.01MW Minimum "),
             (r"$\bf Impact \: Volume \: Minimum$"   +"\nSimulation Time 720h\n"+ "0h-Ahead Forecast, "+ "0.25$\Delta$h Resolution, "+ " - % Reliability, "+ "0.01$\Delta$MW Resolution")]

#compute
for i,volume in enumerate([volumeRes,volumeMin]):
    fig,axes = plt.subplots(2,2)
    titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
    plt.suptitle(suptitles[i])
    
    for k,source in enumerate(["solar","wind","agg","demand"]):
        
        #mean bid volume
        MBV = volume[:,k]
        
        #mean effective volume
        MEV = np.ones(len(granularities))*df[source].mean()
        
        axes[int(k/2),k%2].plot(granularities,MBV,linewidth=1.5)
        axes[int(k/2),k%2].plot(granularities,MEV,linewidth=1.5)
        axes[int(k/2),k%2].fill_between(granularities,MBV,MEV,color = "orange",alpha = 0.1)
        axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Lost Volume"))
        axes[int(k/2),k%2].set_xlabel(xlabels[i])
        axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
        axes[int(k/2),k%2].set_ylim(0,32)
        axes[int(k/2),k%2].set_title(titles[k]) 
        
        #mean added volume
        if source == "agg":
            reference = volume[:,4]+volume[:,5]
            
            axes[int(k/2),k%2].plot(granularities,reference,linewidth=1.5,linestyle ='--')
            axes[int(k/2),k%2].fill_between(granularities,MBV,reference,color = "green",alpha = 0.2)
            axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Seperated Volume","Mean Lost Volume","Mean Added Volume"))
