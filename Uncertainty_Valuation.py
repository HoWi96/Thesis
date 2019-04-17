# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 11:04:57 2019

@author: user
@summary: 
    1. Exploration imbalance data
    2. System Cost of Imbalance
    3. Player Cost of Imbalance
    4. Contribution of Forecast Uncertainty to Imbalance
"""



# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

# In[] UPLOAD DATA

imbalance = pd.read_excel("Data/ImbalanceJune2017.xlsx")

SI = imbalance["SI"]
NRV = imbalance["NRV"]
ALPHA = imbalance["ALPHA"]
MIP = imbalance["MIP"]
MDP = imbalance["MDP"]
POS = imbalance["POS"]
NEG = imbalance["NEG"]
#The area control error is the sum of the gross SI and the NRV
#and can be regarded as the net SI
ACE = SI + NRV

#%% EXPLORATION IMBALANCE DATA
plt.close("all")

#The system cost
plt.figure()
plt.plot(MDP, label = "MDP")
plt.plot(MIP, label = "MIP")
plt.legend()
plt.title("System Cost")

#The player cost
plt.figure()
plt.plot(POS, label = "POS")
plt.plot(NEG, label = "NEG")
plt.plot(ALPHA, label = "ALPHA")
plt.legend()
plt.title("Player Cost")

#The imbalance
plt.figure()
plt.plot(SI, label = "gross SI")
plt.plot(NRV, label = "NRV")
plt.plot(ACE, label = 'ACE/net SI')
plt.legend()
plt.title("Imbalance")

#%% SYSTEM COST OF IMBALANCE

# Cost [€] = SI [MW] * MP [€/MW] recalculated to 15min
systemCostSI = np.abs(SI)*np.where(SI>0,-MDP,MIP)/4
systemCostNRV = np.abs(NRV)*np.where(SI>0,-MDP,MIP)/4
systemCostACE = np.abs(ACE)*np.where(SI>0,-MDP,MIP)/4

#The montly cost of SI in €
print("The monthly SI system cost is: {0:1.2e}".format(np.sum(systemCostSI)),"€" )
print("The monthly NRV system cost is: {0:1.2e}".format(np.sum(systemCostNRV)),"€" )
print("The monthly ACE system cost is: {0:1.2e}".format(np.sum(systemCostACE)),"€" )

#The QH Cost of SI in €
plt.figure()
plt.plot(systemCostSI, label = 'SI')
plt.plot(systemCostNRV,label = 'NRV')
plt.plot(systemCostACE,label = 'ACE')
plt.title("System Cost")
plt.legend()

#%% PLAYER COST OF IMBALANCE

#ALPHA is an incentive to the players, not a system cost
playerCostALPHA = np.abs(NRV)*ALPHA/4
print("The monthly ALPHA player cost is: {0:1.2e}".format(np.sum(playerCostALPHA)),"€" )
print("This is {0:2.2f}".format(np.sum(playerCostALPHA)/np.sum(systemCostNRV)*100),"% of NRV system cost, which is non-negligible")

#%% CONTRIBUTION OF FORECAST UNCERTAINTY TO IMBALANCE

solar = pd.read_csv("Data/SolarForecastJune2017.csv")
wind = pd.read_csv("Data/WindForecastJune2017.csv")
demand = pd.read_csv("Data/LoadForecastJune2017.csv")

#error is always an overestimation
#ERROR = SUPPLY - EXPECTED SUPPLY
solarErr = solar["RealTime"]-solar["24h-ahead"]
windErr = wind["RealTime"]-wind["24h-ahead"]
#ERROR = DEMAND - EXPECTED DEMAND
demandErr = demand["RealTime"]-demand["24h-ahead"]

#Exploration data
plt.figure()
plt.plot(solarErr,SI,'o',label='Solar Error')
plt.plot(windErr,SI,'o',label='Wind Error')
plt.plot(demandErr,SI,'o', label = 'Demand Error')
plt.ylabel("System Imbalance")
plt.legend()
plt.title("Scatter Plot")

plt.figure()
plt.plot(solarErr+windErr-demandErr,SI,'o')
plt.xlabel("Total Forecast Error = Solar Error + Wind Error - Demand Error")
plt.ylabel("System Imbalance")
plt.title("Scatter Plot")

#Correlation between SI and Forecast Uncertainty
np.vstack((solarErr+windErr-demandErr,SI))
dataError24h = np.vstack((solarErr+windErr-demandErr,SI))
print("\n MEAN \n % overestimation wind + % overestimation solar + % overestimation demand \n", np.mean(dataError24h,1))
print("\n COVARIANCE MATRIX \n |Forecast Uncertainty         |System Imbalance  \n", np.cov(dataError24h))
print("\n CORRELATION MATRIX \n |Forecast Uncertainty         |System Imbalance  \n", np.corrcoef(dataError24h))

"""
A 55% correlation is less than expected. Possible reasons:
    1. Adaption outside demand, wind and solar
    2. Outage Supply
    3. Losses Transmission System
    3. International Import and Export
"""

# Solar vs Wind vs Demand
# ASSUMPTION: every source of uncertainty need to be balanced separately for cost estimation
# ARGUMENT: Valuation for a worst case scenario
solarErrTot = np.sum(np.abs(solarErr))
windErrTot = np.sum(np.abs(windErr))
demandErrTot = np.sum(np.abs(demandErr))
ErrTot = solarErrTot + windErrTot + demandErrTot
print("\n Solar contribition {0:2.2f}".format(solarErrTot/ErrTot*100),"%"
      "\n wind contribition {0:2.2f}".format(windErrTot/ErrTot*100),"%"
      "\n Demand contribition {0:2.2f}".format(demandErrTot/ErrTot*100),"% \n")

#Price of Solar
systemCostSolar = np.abs(solarErr)*np.where(solarErr>0,-MDP,MIP)/4
systemCostWind = np.abs(windErr)*np.where(windErr>0,-MDP,MIP)/4
systemCostDemand = np.abs(demandErr)*np.where(-demandErr>0,-MDP,MIP)/4
systemCostSolarTot = np.sum(systemCostSolar)
systemCostWindTot = np.sum(systemCostWind)
systemCostDemandTot = np.sum(systemCostDemand)
systemCostUncertainty = systemCostSolarTot + systemCostWindTot + systemCostDemandTot



#The montly cost of SI in €
print("The monthly solar uncertainty cost is: {0:1.2e}".format(np.sum(systemCostSolar)),"€" )
print("The monthly wind uncertainty cost is: {0:1.2e}".format(np.sum(systemCostWind)),"€" )
print("The monthly demand uncertainty cost is: {0:1.2e}".format(np.sum(systemCostDemand)),"€" )
print("\n Solar cost contribition {0:2.2f}".format(systemCostSolarTot/systemCostUncertainty*100),"%"
      "\n wind cost contribition {0:2.2f}".format(systemCostWindTot/systemCostUncertainty*100),"%"
      "\n Demand cost contribition {0:2.2f}".format(systemCostDemandTot/systemCostUncertainty*100),"%")

