# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 11:04:57 2019

@author: user
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

#%% DATA EXPLORATION
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

#%% SYSTEM COST

# Cost [€] = SI [MW] * MP [€/MW] recalculated to 15min
systemCostSI = np.abs(SI)*np.where(SI>0,-MDP,MIP)/4
systemCostNRV = np.abs(NRV)*np.where(SI>0,-MDP,MIP)/4
systemCostACE = np.abs(ACE)*np.where(SI>0,-MDP,MIP)/4

#The montly cost of SI in €
print("The monthly SI system cost is: {0:1.3e}".format(np.sum(systemCostSI)),"€" )
print("The monthly NRV system cost is: {0:1.3e}".format(np.sum(systemCostNRV)),"€" )
print("The monthly ACE system cost is: {0:1.3e}".format(np.sum(systemCostACE)),"€" )

#The QH Cost of SI in €
plt.figure()
plt.plot(systemCostSI, label = 'SI')
plt.plot(systemCostNRV,label = 'NRV')
plt.plot(systemCostACE,label = 'ACE')
plt.title("System Cost")
plt.legend()

#%% PLAYER COST

#ALPHA can be neglected, in some cases 70% total cost
#ALPHA is an incentive, not a real cost
MAX = np.maximum(imbalance["POS"],imbalance["NEG"])
ALPHA_rel = ALPHA/MAX[MAX>8]*100
plt.figure()
plt.plot(ALPHA_rel)

playerCostALPHA = np.abs(NRV)*ALPHA/4
print("The monthly ALPHA player cost is: {0:1.3e}".format(np.sum(playerCostALPHA)),"€" )
print("This is {0:2.2f}".format(np.sum(playerCostALPHA)/np.sum(systemCostNRV)*100),"% of NRV system cost, which is non-negligible")

#%% CONTRIBUTION UNCERTAINTY

solar = pd.read_csv("Data/SolarForecastJune2017.csv")
wind = pd.read_csv("Data/WindForecastJune2017.csv")
demand = pd.read_csv("Data/LoadForecastJune2017.csv")

#error is always an overestimation
solarErr = solar["RealTime"]-solar["24h-ahead"]
windErr = wind["RealTime"]-wind["24h-ahead"]
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
plt.xlabel("Solar Error + Wind Error - Demand Error")
plt.ylabel("System Imbalance")
plt.title("Scatter Plot")

#Correlation between SI and Forecast Uncertainty
np.vstack((solarErr+windErr-demandErr,SI))
dataError24h = np.vstack((solarErr+windErr-demandErr,SI))
print("\n MEAN \n % overestimation wind + % overestimation solar + % overestimation demand \n", np.mean(dataError24h,1))
print("\n COVARIANCE MATRIX \n |Forecast Uncertainty         |System Imbalance  \n", np.cov(dataError24h))
print("\n CORRELATION MATRIX \n |Forecast Uncertainty         |System Imbalance  \n", np.corrcoef(dataError24h))

# Solar vs Wind vs Demand
solarErrTot = np.sum(np.abs(solarErr))
windErrTot = np.sum(np.abs(windErr))
demandErrTot = np.sum(np.abs(demandErr))
ErrTot = solarErrTot + windErrTot + demandErrTot
print("\n Solar contribition {0:2.2f}".format(solarErrTot/ErrTot*100),"%"
      "\n wind contribition {0:2.2f}".format(windErrTot/ErrTot*100),"%"
      "\n Demand contribition {0:2.2f}".format(demandErrTot/ErrTot*100),"%")

#Price of Solar
#Price of Wind
#Price of Demand
