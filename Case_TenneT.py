# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:49:15 2018

@author: Holger
"""

#%% SET_UP

#Set correct working directory
from os import chdir, getcwd
wd=getcwd()
chdir(wd)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")["RealTime"]
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")["RealTime"]

#%% DATA PREPROCESSING
SOLAR_MONITORED = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_INSTALLED = 100

wind = windRaw*WIND_INSTALLED/WIND_MONITORED
solar = solarRaw*SOLAR_INSTALLED/SOLAR_MONITORED
agg = wind + solar
df = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})

#%% DATA EXPLORATION

#Delete previous plots
plt.close("all")

#Visualisation Time Series
df.plot()
plt.ylabel("Power [MW]")
plt.xlabel("Time [15']")

#Visualisation Probability Density Function
df.plot.kde()
plt.xlabel("Power [MW]")

#visualisation Quantile Function
plt.figure()
quantiles = np.linspace(0,1,20)
plot = plt.plot(quantiles*100,df.quantile(quantiles))
plt.legend(plot, list(df))
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')

#%% FINANCIAL CONSIDERATIONS

#CONSTANTS--------------------

#Product Characteristics
ACTIVATIONS = 2/12 #activations/M
TIME_GRANULARITY = 30*24 #h  
VOLUME_GRANULARITY = 5 #MW
RELIABILITY = 99 #%
ACTIVATION_DURATION = 1 #h

#Remuneration & Penalisation
EPEX_SPOT_PRICE = 70 #EUR/MW
ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
CAPACITY_REMUNERATION = 6 #EUR/MW/h
FINANCIAL_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation

# VALUE ESTIMATION-------------

#Reasonable reliabilities
#Assumption: ignore unreasonable reliabilities
quantiles = np.linspace(0,0.5,20) #np.array([0,0.003,0.01,0.05,0.10,0.15,0.20,0.50]) 

#Monthly Revenues
#Assumption: ignore reported non-availability
capacityRemuneration= TIME_GRANULARITY*CAPACITY_REMUNERATION*df.quantile(quantiles)
activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*df.quantile(quantiles)
financialPenalty = ACTIVATION_DURATION*FINANCIAL_PENALTY*df.quantile(quantiles)

#Components Expected Revenues Aggregator
(capacityRemuneration["aggregator"]/10**3).plot(label = "capacity remuneration")
(ACTIVATIONS*activationRemuneration["aggregator"].multiply((1-quantiles),0)/10**3).plot(label = "activation remuneration")
(ACTIVATIONS*financialPenalty["aggregator"].multiply(quantiles,0)/10**3).plot(label = "financial penalty")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()

#Total Expected Revenues
#revenues1 = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
revenues1 = capacityRemuneration + ACTIVATIONS*(activationRemuneration.multiply((1-quantiles),0) - financialPenalty.multiply(quantiles,0))
(revenues1/10**3).plot()
((revenues1["aggregator"]-revenues1["wind"]-revenues1["solar"])/10**3).plot(label="added value aggregator")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()

#RECOMMENDATION ------------------
x = revenues1["aggregator"].idxmax()
y = revenues1["aggregator"][x]/10**3

plt.plot([x], [y], 'o')
plt.annotate('financial optimum',
            xy=(x,y),
            xytext=(0.65,0.9),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )

#%% BREAKEVEN SANCTIONS VS REMUNERATION

breakeven = capacityRemuneration/financialPenalty
breakeven = 720/120
