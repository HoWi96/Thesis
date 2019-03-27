# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:50:53 2019

@author: user
"""

# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.special
from mpl_toolkits import mplot3d


# In[] Upload Data

solarData = pd.read_csv("Data/SolarForecastJune2017.csv")
windData = pd.read_csv("Data/WindForecastJune2017.csv")
WINDINSTALLED = 2403.17
SOLARINSTALLED = 2952.78  

solar = solarData["RealTime"]*30/SOLARINSTALLED
wind = windData["RealTime"]*100/WINDINSTALLED

x = np.array([0.01,0.1,0.5,1,2,4,5,10,20])

i = 0
for size in x:
    test[0,i] = sum(solar%size)/sum(solar)*100
    test[1,i] = sum(wind%size)/sum(solar+wind)*100
    test[2,i] = sum((solar+wind)%size)/sum(solar+wind)*100
    i=i+1
    
    plt.close("all")
    plt.plot(x,test[0], label='solar')
    plt.plot(x,test[1], label='wind')
    plt.plot(x,test[2], label='aggregator')
    plt.legend()
    plt.xlabel('Volume size [MW]')
    plt.ylabel('Relative energy not offered [%]')






