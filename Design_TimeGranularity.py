# -*- coding: utf-8 -*-
"""
Created: May 2019
@author: Holger
"""

#%% IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})

#%% PROCESS 

#initialize
RELIABILITY = 95
granularities = np.arange(0.25,50,2)
groups = np.array(int(df.shape[0]/4)/granularities,dtype="int")
volume = np.zeros((granularities.shape[0],df.shape[1]))

#compute
for i,gran in enumerate(granularities):
    for k in range(0,groups[i]):
        volume[i] += np.array(df[int(k*4*gran):int((k+1)*4*gran)+1].quantile((100-RELIABILITY)/100))
    
    #take the mean of the volume
    volume[i] = volume[i]/groups[i]

#%% ILLUSTRATE

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
suptitle = (r"$\bf Impact \: Time \: Resolution$"+"\nSimulation Time 720h\n"+ "0h-Ahead Forecast, "+ "95% Reliability, "+ "0.01$\Delta$MW Resolution, "+ "0.01MW Minimum ")

#compute
plt.close("all")
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

#iterate over sources
for k,source in enumerate(["solar","wind","agg","demand"]):
    
    #mean bid volume
    MBV = volume[:,k]
    
    #mean effective volume
    MEV = np.ones(len(granularities))*df[source].mean()
    
    axes[int(k/2),k%2].plot(granularities,MBV,linewidth=1.5)
    axes[int(k/2),k%2].plot(granularities,MEV,linewidth=1.5)
    axes[int(k/2),k%2].fill_between(granularities,MBV,MEV,color = "orange",alpha = 0.1)
    axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Lost Volume"))
    axes[int(k/2),k%2].set_xlabel('Time Resolution [$\Delta$h]')
    axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
    axes[int(k/2),k%2].set_ylim(0,31)
    axes[int(k/2),k%2].set_title(titles[k]) 
    
    #mean added volume
    if source == "agg":
        reference = volume[:,4]+volume[:,5]
        
        axes[int(k/2),k%2].plot(granularities,reference,linewidth=1.5,linestyle ='--')
        axes[int(k/2),k%2].fill_between(granularities,MBV,reference,color = "green",alpha = 0.2)
        axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Seperated Volume","Mean Lost Volume","Mean Added Volume"))
