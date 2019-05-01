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

volume = pd.DataFrame(index = x, data={"wind":np.zeros(x.shape),
                                       "solar":np.zeros(x.shape),
                                       "agg":np.zeros(x.shape)})

for i,size in enumerate(x):
    volume["wind"][i] = (solar%size).mean()
    volume["solar"][i] = (wind%size).mean()
    volume["agg"][i] = (agg%size).mean()
    
plt.close("all")

volume.plot()
plt.xlabel('Volume Granularity [$\Delta$MW]')
plt.ylabel('Lost Volume [MW]')
plt.title("Lost Volume By Volume Granularity")
