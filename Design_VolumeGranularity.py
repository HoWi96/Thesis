# -*- coding: utf-8 -*-
"""
Created: May 2019
@author: Holger
"""

#IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import PreprocessData as pre

#PREPROCESS
solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})
dfArray = np.array(df)

#%% PROCESS

#initialize
granularities = np.array([0.25,0.5,1,2,4,8])
#granularities = np.arange(0.01,10.01,0.01)
volumeRes = np.zeros((granularities.shape[0],df.shape[1]))
volumeMin = np.zeros((granularities.shape[0],df.shape[1]))

#compute
for j,gran in enumerate(granularities):
    
    #compute volume resolution
    volumeRes[j,:] = (df-df%gran).mean()
    
    #compute volume minimum
    volumeMin[j,:] = df.where(df>gran,0).mean()

#%% ILLUSTRATE

#initialize
xlabels = ['Volume Resolution [MW]','Volume Minimum [MW]']
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
suptitles = [(r"$\bf Impact \: Volume \: Resolution$"+"\nSimulation of 720h\n"+ "0h-Ahead Forecast, "+ "0.25h Resolution, "+ "-% Reliability, "+ "0.01MW Minimum "),
             (r"$\bf Impact \: Volume \: Minimum$"   +"\nSimulation of 720h\n"+ "0h-Ahead Forecast, "+ "0.25h Resolution, "+ "-% Reliability, "+ "0.01MW Resolution")]
    
#compute
plt.close("all")

#iterate over volumes
for i,volume in enumerate([volumeRes,volumeMin]):
    #compute
    fig,axes = plt.subplots(2,2)
    plt.suptitle(suptitles[i])
    
    #iterate over sources
    for k,source in enumerate(["solar","wind","agg","demand"]):
        
        #mean bid volume
        MBV = volume[:,k]
        
        #mean Realized volume
        MEV = np.ones(len(granularities))*df[source].mean()
        
        axes[int(k/2),k%2].plot(granularities,MBV,linewidth=1.5)
        axes[int(k/2),k%2].plot(granularities,MEV,linewidth=1.5)
        axes[int(k/2),k%2].fill_between(granularities,MBV,MEV,color = "orange",alpha = 0.1)
        axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Realized Volume","Mean Lost Volume"))
        axes[int(k/2),k%2].set_xlabel(xlabels[i])
        axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
        axes[int(k/2),k%2].set_ylim(0,31)
        axes[int(k/2),k%2].set_title(titles[k]) 
        
        #mean added volume
        if source == "agg":
            reference = volume[:,4]+volume[:,5]
            
            axes[int(k/2),k%2].plot(granularities,reference,linewidth=1.5,linestyle ='--')
            axes[int(k/2),k%2].fill_between(granularities,MBV,reference,color = "green",alpha = 0.2)
            axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Realized Volume","Mean Seperated Volume","Mean Lost Volume","Mean Added Volume"))
            
print(np.round(volumeRes/np.matmul(np.ones((len(granularities),6)),np.diag(df.mean())),3))
print(np.round(volumeMin/np.matmul(np.ones((len(granularities),6)),np.diag(df.mean())),3))
