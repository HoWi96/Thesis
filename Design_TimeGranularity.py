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

#%% PREPROCESS DATA

SOLAR_MONITORED = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_INSTALLED = 100

wind = windRaw*WIND_INSTALLED/WIND_MONITORED
solar = solarRaw*SOLAR_INSTALLED/SOLAR_MONITORED
agg = wind + solar

df = pd.DataFrame(data={"wind":wind,"solar":solar,"agg":agg})

#%% PROCESS DATA
plt.close("all")    

TIME_QUANTILE = 10 #round(norm.cdf(2)*100,2)
#TIME_QUANTILE = 84.13 #round(norm.cdf(1)*100,2)
TIME_TOTAL = 720.#h
TIME_GRANULARITY = np.array([.25,.5,1,2,3,4,5,6,8,9,10,12,15,16,18,20,24,30,40,48,50,60,72,80,90,120,144,180])#h
TIME_GROUPS = np.array(TIME_TOTAL/TIME_GRANULARITY,dtype="int")

volume = np.zeros((TIME_GRANULARITY.size,3))

for i,gran in enumerate(TIME_GRANULARITY):
    for k in range(0,TIME_GROUPS[i]):
        volume[i] += np.array(df[int(k*4*gran):int((k+1)*4*gran)].quantile(TIME_QUANTILE/100))
    volume[i] = volume[i]/TIME_GROUPS[i] #taking the mean
    
volumedf = pd.DataFrame(index = TIME_GRANULARITY,
             data = {"wind":volume[:,0],
                     "solar":volume[:,1],
                     "agg":volume[:,2]})
    
(volumedf["wind"].max() - volumedf["wind"]).plot(label = "Reliability "+str(100-TIME_QUANTILE)+"%" )
plt.xlabel('Time Granularity [$\Delta$h]')
plt.ylabel('Lost Volume [MW]')
plt.title("Lost Volume By Time Granularity")
plt.suptitle("Downward Reserves 100MWp Wind")
plt.legend()
        