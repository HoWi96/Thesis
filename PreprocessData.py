# -*- coding: utf-8 -*-
"""
Created on Sat May 25 18:54:05 2019

@author: user
"""

import pandas as pd

#%%IMPORT DATA
def importData():
    solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
    windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
    demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")
    allRaw2016 = pd.read_csv("Data/data2016.csv")
    
    return (solarRaw,windRaw,demandRaw,allRaw2016)

#%% PREPROCESS
def preprocessData(solarRaw,windRaw,demandRaw,allRaw2016):
    
    #Installed capacity
    WIND_INST = 2403.17
    SOLAR_INST= 2952.78
    DEMAND_PK= 11742.29
    WIND_INST2016 = 1960.91
    SOLAR_INST2016= 2952.78
    DEMAND_PK2016 = 11589.6
    
    #solar preprocess
    solar = solarRaw.loc[:, solarRaw.columns != "DateTime"]*100/SOLAR_INST
    solar["8760"] = allRaw2016["solar"]*100/SOLAR_INST2016
    
    #wind preprocess
    wind = windRaw.loc[:, windRaw.columns != "DateTime"]*100/WIND_INST
    wind["8760"] = allRaw2016["wind"]*100/WIND_INST2016
    
    #demand preprocess
    demand = demandRaw.loc[:, demandRaw.columns != "DateTime"]*100/DEMAND_PK
    demand["8760"] = allRaw2016["load"]*100/DEMAND_PK2016
    demand = demand-50 #SL = 50MW
    
    #aggregator preprocess
    aggregator = solar*0.25+wind*0.75
    
    return solar,wind,aggregator,demand

if __name__ == "__main__":
    solarRaw,windRaw,demandRaw,allRaw2016 = importData()
    solar,wind,aggregator,demand = preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
    