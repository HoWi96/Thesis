# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 14:45:18 2019

@author: user
"""
# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.special

# In[] GLOBAL CONSTANTS
ACTIVATIONS = 2 #activations/Y
ACTIVATION_DURATION = 1 #h
CAPACITY_REMUNERATION = 6 #EUR/MW/h
FINANCIAL_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation

# In[] PREPROCESS DATA
def preprocessData():
    solar = pd.read_csv("Data/SolarForecastJune2017.csv")["RealTime"]
    wind = pd.read_csv("Data/WindForecastJune2017.csv")["RealTime"]
    agg = solar + wind
    return agg

# In[] PROCESS DATA
def processData(quantiles, volume):

    financialPenalty = -ACTIVATION_DURATION*FINANCIAL_PENALTY*volume

    #Penalty via binomial model
    sanctionA = 0
    for k in range(0,ACTIVATIONS+1):
        sanctionA += scipy.special.binom(ACTIVATIONS,k)*np.power(quantiles,ACTIVATIONS-k)*np.power(1-quantiles,k)*((ACTIVATIONS-k)*financialPenalty)

    #Penalty via expected value of binomial model
    sanctionB = ACTIVATIONS*financialPenalty*quantiles

    return sanctionA, sanctionB
    
# In[] MAIN

if __name__ == "__main__":
    
    agg = preprocessData()
    quantiles = np.linspace(0,.5,20)
    sanctionA, sanctionB = processData(quantiles,agg.quantile(quantiles))

    plt.close("all")
    plt.plot(quantiles*100, sanctionA/10**6, label = "Expected Sanction Method Binomial Model")
    plt.plot(quantiles*100, sanctionB/10**6, label = "Expected Sanction Method Expected Value")
    plt.legend()
    plt.xlabel('Quantiles [%]')
    plt.ylabel('Expected Revenues [M€/month]')
