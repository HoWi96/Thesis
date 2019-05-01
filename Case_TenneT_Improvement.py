# -*- coding: utf-8 -*-
"""
Created on 27/04/2019
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
from scipy.stats import norm

#%% DATA PREPROCESSING

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")

SOLAR_MONITORED = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_INSTALLED = 100

#Preprocess data
wind168 = windRaw["168h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar168 = solarRaw["168h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg168 = wind168 + solar168

wind24 = windRaw["24h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar24 = solarRaw["24h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg24 = wind24 + solar24

wind5 = windRaw["5h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar3 = solarRaw["3h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg4 = wind5 + solar3

wind = windRaw["RealTime"]*WIND_INSTALLED/WIND_MONITORED
solar = solarRaw["RealTime"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg = wind + solar


df = pd.DataFrame(data={0:agg,4:agg4,24:agg24,168:agg168})
dfComponents = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})
#dfError = pd.DataFrame(data={"wind":wind-wind24,"solar":solar-solar24,"aggregator":agg-agg24})

#%% DATA EXPLORATION

#Delete previous plots
plt.close("all")

#Visualisation Time Series
dfComponents.plot()
plt.ylabel("Power [MW]")
plt.xlabel("Time [15']")

#Visualisation Probability Density Function
dfComponents.plot.kde()
plt.xlabel("Power [MW]")

#visualisation Quantile Function
plt.figure()
quantiles = np.linspace(0,1,20)
plot = plt.plot(quantiles*100,dfComponents.quantile(quantiles))
plt.legend(plot, list(dfComponents))
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')

#%% FINANCIAL CONSIDERATIONS

#CONSTANTS--------------------

#Constraints
TIME_DURATION = 1#h
TIME_GRANULARITY = 1#h
TIME_HORIZON = 4#h
VOLUME_GRANULARITY = .1#MW
VOLUME_MIN = 1#MW
ACTIVATION_DURATION = 1#h

UNCERTAINTY = 15.87 #round(norm.cdf(-1)*100,2)
RELIABILITY = 97.72 #round(norm.cdf(2)*100,2)

#Product Characteristics
ACTIVATIONS = 2/12 #activations/M
TIME_TOTAL = 30*24#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)

#Remuneration & Penalisation
EPEX_SPOT_PRICE = 70 #EUR/MW
ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
CAPACITY_REMUNERATION = 6 #EUR/MW/h
FINANCIAL_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation

# VOLUME ESTIMATION------------

quantiles = np.linspace(0,1,200)
volumes = df[TIME_HORIZON]

#Time constraint
volumesC0 = volumes[int(0*4*TIME_GRANULARITY):1*4*TIME_GRANULARITY].quantile(quantiles) #1Month
for i in range(1,TIME_GROUPS):
    volumesC0 += volumes[int(i*4*TIME_GRANULARITY):(i+1)*4*TIME_GRANULARITY].quantile(quantiles)
volumesC0 = volumesC0/TIME_GROUPS #taking the mean

#Forecast Horizon + Forecast Uncertainty
#REMARK: commutative action with time constraint
#TODO Improvement: make error dependend of volume
volumesC1 = volumesC0.copy()
error = df[TIME_HORIZON]-df[0]
volumesC1 = volumesC1 + error.quantile(UNCERTAINTY/100) 

#Volume constraint
volumesC2 = volumesC1.copy()
volumesC2 = volumesC1 - volumesC1%VOLUME_GRANULARITY
volumesC3 = volumesC2.copy(); volumesC3[volumesC1<VOLUME_MIN]=0

#Reliability constraint
volumesC4 = volumesC3.copy(); volumesC4[quantiles>(1-RELIABILITY/100)]=0

#Impact
plt.close("all")
plt.figure()
volumesC0.plot(label="C0a Duration "+str(TIME_DURATION)+"h"+
               "\nC0b Granularity "+str(TIME_GRANULARITY) +"h",linestyle = ":")
volumesC1.plot(label="C1a Horizon "+str(TIME_HORIZON)+"h"+
               "\nC1b Uncertainty "+str(UNCERTAINTY)+"%",linestyle = ":")
volumesC3.plot(label="C2a Granularity " + str(VOLUME_GRANULARITY)+"MW"+
               "\nC2b Minimum "+str(VOLUME_MIN)+"MW",linestyle = "--")
volumesC4.plot(label="C3a Activation "+str(ACTIVATION_DURATION)+"h"
               "\nC3b Reliability "+str(RELIABILITY)+"%")
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')
plt.title("Aggregator 130MWp")
plt.legend()

x = 1-RELIABILITY/100
y = volumesC3.quantile(x)
plt.plot([x], [y], 'o')
plt.annotate('C4 = Reliability ' + str(RELIABILITY) +"% \n"+ str(round(y,2))+ "MW",
            xy=(x,y),
            xytext=(.2,.2),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )
plt.show()

# VALUE ESTIMATION-------------

#TODO
#Proposal penalty mechanism

#Reasonable reliabilities
#Assumption: ignore unreasonable reliabilities
quantiles = quantiles #np.array([0,0.003,0.01,0.05,0.10,0.15,0.20,0.50]) 
volumes = volumesC4

#Monthly Revenues
#Assumption: ignore reported non-availability
capacityRemuneration= TIME_TOTAL*CAPACITY_REMUNERATION*volumes
activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
activationPenalty = ACTIVATION_DURATION*FINANCIAL_PENALTY*volumes
#revenues1 = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
revenues1 = capacityRemuneration + ACTIVATIONS*(activationRemuneration.multiply((1-quantiles),0) - activationPenalty.multiply(quantiles,0))

#Components Expected Revenues Aggregator
plt.figure()
(capacityRemuneration/10**3).plot(label = "capacity remuneration")
(ACTIVATIONS*activationRemuneration.multiply((1-quantiles),0)/10**3).plot(label = "activation remuneration")
(ACTIVATIONS*activationPenalty.multiply(quantiles,0)/10**3).plot(label = "financial penalty")
(revenues1/10**3).plot(label = "Expected revenues")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()
plt.show()

#RECOMMENDATION ------------------
x = revenues1.idxmax()
y = revenues1[x]/10**3

plt.plot([x], [y], 'o')
plt.annotate('financial optimum '+str(round(y,2))+"k€/M",
            xy=(x,y),
            xytext=(0.65,0.9),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )
plt.show()

#%% BREAKEVEN SANCTIONS VS REMUNERATION

breakeven = capacityRemuneration/activationPenalty
breakeven = 720/120
