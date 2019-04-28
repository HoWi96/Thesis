# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 18:17:25 2019

@author: HoWi96
"""

#%% IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% PREPROCESS DATA
def preprocessData():
    
    solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")["RealTime"]
    windRaw = pd.read_csv("Data/WindForecastJune2017.csv")["RealTime"]
    
    SOLAR_MONITORED = 2952.78
    SOLAR_INSTALLED = 30
    WIND_MONITORED = 2424.07
    WIND_INSTALLED = 100
    
    wind = windRaw*WIND_INSTALLED/WIND_MONITORED
    solar = solarRaw*SOLAR_INSTALLED/SOLAR_MONITORED
    agg = wind + solar
    df = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})
    return df

# In[] PROCESS DATA
def experimentParameterTime(uncertainty = 0.2):
    data = preprocessData()["aggregator"]
    hours = int(data.shape[0]/4)
    totalEnergy = sum(data)/4

    #15min,30min,1h,2h,3h, 4h,8h,24h,72h,120h 
    periods = [.25,.5,1,2,3,4,5,8,12,16,24,48,72,120,720] #divisors of 720 
    varEnergy = np.zeros(len(periods))
    for i in range(len(periods)):
        p = periods[i]
        for n in range(int(hours/p)):
            # total energy = certain energy/period*periods*duration/period
             varEnergy[i] += data[int(n*4*p):int((n+1)*4*p)].quantile(uncertainty)*p
            
    fig, ax = plt.subplots()
    plt.plot(periods,varEnergy/totalEnergy*100,label = uncertainty*100)
    plt.legend()
    plt.ylabel('Ratio of total produced energy [%]')
    plt.xlabel('Duration of the delivery period [h]')
    plt.title('Effect of delivery period duration \n on produced energy for an uncertainty as indicated by legend.')
    ax.set_ylim(0,120)
    plt.show()
    
    
def experimentParameterUncertainty(period = 4):
    data = preprocessData()["aggregator"]
    hours = int(data.shape[0]/4)
    totalEnergy = sum(data)/4
    
    uncertainty = np.linspace(0,1,20)
    varEnergy = np.zeros(len(uncertainty))
    for i in range(len(uncertainty)):
        for n in range(int(hours/period)):
            # total energy = certain energy/period*periods*duration/period
             varEnergy[i] += data[int(n*4*period):int((n+1)*4*period)].quantile(uncertainty[i])*period
            
    fig, ax = plt.subplots()
    plt.plot(uncertainty*100,varEnergy/totalEnergy*100,label = period)
    plt.legend()
    plt.ylabel('Ratio of total produced energy [%]')
    plt.xlabel('Uncertainty [%]')
    plt.title('Effect of uncertainty on produced energy \n for a duration of hours indicated by legend')
    ax.set_ylim(0,120)
    plt.show()
    
# In[] MAIN
if __name__ == "__main__":
    plt.close("all")
    
#    #2D PLOTS
#    plt.close('all')
#    experimentParameterUncertainty(1)
#    experimentParameterUncertainty(4)
#    experimentParameterUncertainty(720)
#    experimentParameterTime(uncertainty = 0.01)
#    experimentParameterTime(uncertainty = 0.2)
#    experimentParameterTime(uncertainty = 0.4)
    
    #3D PLOTS
#    #Total Overview  
#    uncertainty = np.linspace(0,1,20)
#    periods = np.array([.25,.5,1,2,3,4,5,8,12,16,24,48,72,120,720])
        
    #Region of Interest
    uncertainty = np.linspace(0,.5,10)
    periods = np.array([.25,.5,1,2,3,4,5,8,12,24])
    
    #Process Data
    def processEnergyRatio(uncertainty,periods):
        data = preprocessData()["aggregator"]
        hours = int(data.shape[0]/4)
        totalEnergy = sum(data)/4
        varEnergy = np.zeros((len(uncertainty),len(periods),))
        
        for i in range(len(uncertainty)):
            for j in range(len(periods)):
                
                for n in range(int(hours/periods[j])):
                    # total energy = certain energy/period*periods*duration/period
                    varEnergy[i,j] += data[int(n*4*periods[j]):int((n+1)*4*periods[j])].quantile(uncertainty[i])*periods[j]
        return varEnergy/totalEnergy*100
       
    X,Y = np.meshgrid(periods,uncertainty)
    Z = processEnergyRatio(uncertainty,periods)
    
    
    #3D Surface Plot
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y*100, Z, rstride=1, cstride=1,cmap='plasma',edgecolor='none')
    ax.set_title('Ratio of Offered Energy to Total Available Energy')
    ax.set_ylabel('Uncertainty [%]')
    ax.set_xlabel('Delivery Period [h]')
    ax.set_zlabel('Energy Ratio [%]')
    
    
    
    