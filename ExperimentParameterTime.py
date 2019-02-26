# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 18:17:25 2019

@author: HoWi96
"""

# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.special
from mpl_toolkits.mplot3d import axes3d

# In[] PREPROCESS DATA
def preprocessData(dataPath="DataJune2017.csv"):
    data = pd.read_csv(dataPath)

    SunMonitored = 2952.78
    WindMonitored = 2424.07
    SunInstalled = 30
    WindInstalled = 100

    data["WIND2017"] = data["WIND2017"]*WindInstalled/WindMonitored
    data["SUN2017"] = data["SUN2017"]*SunInstalled/SunMonitored
    data["AGG2017"] = data["WIND2017"]+data["SUN2017"]
    return data

# In[] PROCESS DATA
def experimentParameterTime(uncertainty = 0.2):
    data = preprocessData(dataPath="DataJune2017.csv")["AGG2017"]
    hours = int(data.shape[0]/4)
    totalEnergy = sum(data)/4

    #15min,30min,1h,2h,3h, 4h,8h,24h,72h,120h 
    periods = [.25,.5,1,2,3,4,5,8,12,16,24,72,120,720] #divisors of 720 
    varEnergy = np.zeros(len(periods))
    for i in range(len(periods)):
        p = periods[i]
        for n in range(int(hours/p)):
            # total energy = certain energy/period*periods*duration/period
             varEnergy[i] += data[int(n*4*p):int((n+1)*4*p)].quantile(uncertainty)*p
            
    fig, ax = plt.subplots()
    plt.plot(periods,varEnergy/totalEnergy*100)
    plt.ylabel('Ratio of total produced energy [%]')
    plt.xlabel('Duration of the delivery period [h]')
    plt.title('Effect of delivery period duration \n on produced energy for an uncertainty of 20%.')
    ax.set_ylim(0,120)
    plt.show()
    
    
def experimentParameterUncertainty(period = 4):
    data = preprocessData(dataPath="DataJune2017.csv")["AGG2017"]
    hours = int(data.shape[0]/4)
    totalEnergy = sum(data)/4
    
    uncertainty = np.linspace(0,1,20)
    varEnergy = np.zeros(len(uncertainty))
    for i in range(len(uncertainty)):
        for n in range(int(hours/period)):
            # total energy = certain energy/period*periods*duration/period
             varEnergy[i] += data[int(n*4*period):int((n+1)*4*period)].quantile(uncertainty[i])*period
            
    fig, ax = plt.subplots()
    plt.plot(uncertainty*100,varEnergy/totalEnergy*100)
    plt.ylabel('Ratio of total produced energy [%]')
    plt.xlabel('Uncertainty [%]')
    plt.title('Effect of uncertainty \n on produced energy for a duration of 4h.')
    ax.set_ylim(0,120)
    plt.show()
    
# In[] MAIN
if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Grab some test data.
    X, Y, Z = axes3d.get_test_data(0.05)
    
    # Plot a basic wireframe.
    ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
    
    plt.show()

    
    
    
    
    


