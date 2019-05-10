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

#%% Preprocess Data Data

WINDINSTALLED = 2403.17
SOLARINSTALLED = 2952.78  

solar = solarRaw*30/SOLARINSTALLED
wind = windRaw*100/WINDINSTALLED
agg = solar + wind
x = np.linspace(0,5,200)

volume = pd.DataFrame(index = x, data={"wind_gran":np.zeros(x.shape),
                                       "wind_min":np.zeros(x.shape),
                                       "solar":np.zeros(x.shape),
                                       "agg":np.zeros(x.shape)})

for i,size in enumerate(x):
    volume["wind_gran"][i] = (solar%size).mean()
    volume["wind_min"][i] = wind[wind<size].mean()
    volume["solar"][i] = (wind%size).mean()
    volume["agg"][i] = (agg%size).mean()
    
    

    
plt.close("all")

fig, axes = plt.subplots(1,2)

#%% WIND PLOT 100MWp

axes[0].plot(volume["wind_gran"])
axes[0].set_xlabel('Volume Granularity [$\Delta$MW]')
axes[0].set_ylabel('Lost Volume [MW]')
axes[0].set_title("Lost Volume By Volume Granularity")

axes[1].plot(volume["wind_min"].fillna(0))
axes[1].set_xlabel('Volume Minimum [MW]')
axes[1].set_ylabel('Lost Volume [MW]')
axes[1].set_title("Lost Volume By Volume Minimum")

fig.suptitle("Downward Reserves 100MWp Wind")
