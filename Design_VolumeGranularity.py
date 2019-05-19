# -*- coding: utf-8 -*-
"""
Created: May 2019
@author: Holger
"""

#%%IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")["RealTime"]
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")["RealTime"]
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")["RealTime"]

#%% Preprocess Data Data

WINDINSTALLED = 2403.17
SOLARINSTALLED = 2952.78
DEMANDPEAK = 11742.29  

solar = solarRaw*100/SOLARINSTALLED
wind = windRaw*100/WINDINSTALLED
demand = demandRaw*100/DEMANDPEAK
agg = solar*0.25 + wind*0.75
x = np.linspace(0,5,200)

plt.close("all")
fig, axes = plt.subplots(2,1)

titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up"]

for i,data in enumerate([solar,wind,agg,demand-30]):

    volume = pd.DataFrame(index = x, data={"gran":np.zeros(x.shape),"min":np.zeros(x.shape)})

    for j,size in enumerate(x):
        volume["gran"][j] = (data%size).mean()
        volume["min"][j] = data[data<size].sum()/data.shape[0]
        
    axes[0].plot(volume["gran"]/data.mean()*100,linewidth=3)
#    axes[0,i].set_xlabel('Volume Granularity [$\Delta$MW]')
#    axes[0,i].set_ylabel('Lost Volume [%]')
#    axes[0,i].set_xlim(0,5)
#    axes[0,i].set_ylim(0,10)
#    axes[0,i].set_title(titles[i]+"\nMean Effective Volume "+str(round(data.mean(),1)) +"MW")
    
    axes[1].plot(volume["min"].fillna(0)/data.mean()*100,linewidth=3)
 
axes[0].legend(titles)
axes[0].set_xlabel('Volume Granularity [$\Delta$MW]')
axes[0].set_ylabel('Lost Volume [%]')
axes[0].set_xlim(0,5)
axes[0].set_title('Lost Volume Versus Volume Granularity')

axes[1].legend(titles)
axes[1].set_xlabel('Volume Minimum [MW]')
axes[1].set_ylabel('Lost Volume [%]')
axes[1].set_xlim(0,5)
axes[1].set_title('Lost Volume Versus Volume Minimum')

fig.suptitle("Mean Effective Volume"+
             " (a) "+str(round(solar.mean(),1))+"MW"+
             " (b) "+str(round(wind.mean(),1))+"MW"+
             " (c) "+str(round(agg.mean(),1))+"MW"+
             " (d) "+str(round((demand-30).mean(),1))+"MW")

