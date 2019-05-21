# -*- coding: utf-8 -*-
"""
Created: May 2019
@author: Holger
"""

#%% IMPORTS
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
demand = demandRaw*100/DEMANDPEAK-30
agg = solar*0.25 + wind*0.75
x = np.arange(0,5,0.01)

df = pd.DataFrame(data={"solar":solar,"wind":wind,"agg":agg,"demand":demand})

#%% PROCESS DATA
plt.close("all")    

RELIABILITY = 90 
TIME_TOTAL = int(df.shape[0]/4)
#TIME_GRANULARITY = np.array([.25,.5,1,2,3,4,5,6,8,9,10,12,15,16,18,20,24,27,30,32,36,40,42,45,48])#h
TIME_GRANULARITY = np.arange(0.25,48,0.5)
TIME_GROUPS = np.array(TIME_TOTAL/TIME_GRANULARITY,dtype="int")

volume = np.zeros((TIME_GRANULARITY.size,4))

for i,gran in enumerate(TIME_GRANULARITY):
    for k in range(0,TIME_GROUPS[i]):
        volume[i] += np.array(df[int(k*4*gran):int((k+1)*4*gran)].quantile((100-RELIABILITY)/100))
    volume[i] = volume[i]/TIME_GROUPS[i] #taking the mean
    
volumedf = pd.DataFrame(index = TIME_GRANULARITY,
                         data = {"solar":   volume[:,0],
                                 "wind":    volume[:,1],
                                 "agg":     volume[:,2],
                                 "demand":  volume[:,3]})
    
(df.mean() - volumedf).plot(label = "Reliability "+str(RELIABILITY)+"%" )

plt.xlabel('Time Granularity [$\Delta$h]')
plt.ylabel('Lost Volume [MW]')
plt.title("Lost Volume By Time Resolution"+
             "\nMean Effective Volume"+
             " (a) "+str(round(solar.mean(),1))+"MW"+
             " (b) "+str(round(wind.mean(),1))+"MW"+
             " (c) "+str(round(agg.mean(),1))+"MW"+
             " (d) "+str(round(demand.mean(),1))+"MW")

titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 30MW)"]
plt.legend(titles)
        