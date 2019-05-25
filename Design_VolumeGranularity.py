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
df = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"]})

#%% PROCESS

#initialize
granularities = np.arange(0,5,0.01)
volumeRes = np.zeros((granularities.shape[0],4))
volumeMin = np.zeros((granularities.shape[0],4))

#compute
for i,source in enumerate(["solar","wind","agg","demand"]):
    for j,size in enumerate(granularities):
        volumeRes[j,i] = (df[source]-df[source]%size).mean()
        volumeMin[j,i] = np.array(df[source][df[source]>size]).sum()/df[source].shape[0]
        print(np.array(df[source][df[source]>size]).shape)

#%% ILLUSTRATE

#initialize
plt.close("all")
xlabels = ['Volume Granularity [$\Delta$MW]','Volume Minimum [MW]']
suptitles = ["Impact Volume Resolution\nSimulation Time 720h","Impact Volume Minimum\nSimulation Time 720h"]

for i,volume in enumerate([volumeRes,volumeMin]):
    fig,axes = plt.subplots(2,2)
    titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
    plt.suptitle(suptitles[i])
    
    #compute
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
