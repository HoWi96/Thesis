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
EXPECTED_ACTIVATIONS = 2 #activations
EXPECTED_FAILURE = 0.5 #50%
EXPECTED_ACTIVATION_DURATION = 1 #h
CAPACITY_REMUNERATION_PRICE = 6 #EUR/MW/h
EPEX_SPOT_PRICE = 70 #EUR/MW

# In[] PREPROCESS DATA
def preprocessData(dataPath="Data/DataJune2017.csv"):
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
def processData(percentile, volume):

    #capacityRemuneration = 365/12*24*volume*CAPACITY_REMUNERATION_PRICE
    #activationRemuneration = EXPECTED_ACTIVATION_DURATION*volume*(250-EPEX_SPOT_PRICE)
    sanction = -EXPECTED_ACTIVATION_DURATION*volume*120*CAPACITY_REMUNERATION_PRICE

    #Calculation via Binomial Model
    sanctionA = 0
    for k in range(0,EXPECTED_ACTIVATIONS+1):
        sanctionA += scipy.special.binom(EXPECTED_ACTIVATIONS,k)*np.power(percentile,EXPECTED_ACTIVATIONS-k)*np.power(1-percentile,k)*((EXPECTED_ACTIVATIONS-k)*sanction)

    #Expected Value
    sanctionB = EXPECTED_ACTIVATIONS*percentile*sanction

    return sanctionA, sanctionB

# In[] VALIDATION MODEL
def validationModel():
    dataPath = "Data/DataJune2017.csv"
    data = preprocessData(dataPath)

    percentile = np.linspace(0,1,10)
    volume = data["AGG2017"].quantile(percentile).values
    sanctionA, sanctionB = processData(percentile,volume)

    #PLOT
    fig, ax1 = plt.subplots()
    ax1.plot(percentile,sanctionA,label = "Expected Sanction Method Binomial Model")
    ax1.plot(percentile,sanctionB,label = "Expected Sanction Method Expected Value")
    #ax1.plot(percentile,percentile**2*2*sanction+(1-percentile)*percentile*2*sanction,label = "Expected Sanction")
    #ax1.plot(percentile,(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*activationPayment,label = "Expected Activation Payment")
    plt.legend()#bbox_to_anchor=(1, 1))
    plt.xlabel('Percentile [-]')
    plt.ylabel('Expected Revenues [EUR/month]')
    plt.title('Revenues components')
    plt.show()
    
# In[] AMOUNT BREAKEVEN SANCTIONS
def amountBreakevenSanctions():
    """
    For breakeven, the total amount of sanctions need to be equal to the total capacity remuneration.
    WORST CASE SCENARIO
    """
    dataPath = "Data/DataJune2017.csv"
    data = preprocessData(dataPath)

    percentile = np.linspace(0,1,10)
    volume = data["AGG2017"].quantile(percentile).values

    capacityRemuneration = 365/12*24*volume*CAPACITY_REMUNERATION_PRICE
    sanction = volume*120*CAPACITY_REMUNERATION_PRICE
    failedActivationsBreakeven = capacityRemuneration/sanction

     #PLOT
    fig, ax = plt.subplots()
    ax.plot(percentile,failedActivationsBreakeven,label = "Activations")
    #ax.plot(percentile,sanction,label = "Sanction")
    #ax.plot(percentile,percentile**2*2*sanction+(1-percentile)*percentile*2*sanction,label = "Expected Sanction")
    #ax.plot(percentile,(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*activationPayment,label = "Expected Activation Payment")
    plt.legend()#bbox_to_anchor=(1, 1))
    plt.xlabel('Percentile [-]')
    plt.ylabel('Monthly Activations')
    plt.title('Revenues components')
    plt.show()

# In[] MAIN

if __name__ == "__main__":
    validationModel()
    amountBreakevenSanctions()






