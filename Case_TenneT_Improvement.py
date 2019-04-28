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


#%% DATA PREPROCESSING

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")

SOLAR_MONITORED = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_INSTALLED = 100

#Preprocess data
wind = windRaw["24h-ahead"]*WIND_INSTALLED/WIND_MONITORED
solar = solarRaw["24h-ahead"]*SOLAR_INSTALLED/SOLAR_MONITORED
agg = wind + solar
df = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})

#Preprocess error
windError = (windRaw["RealTime"]-windRaw["24h-ahead"])*WIND_INSTALLED/WIND_MONITORED
solarError = (solarRaw["RealTime"]-solarRaw["24h-ahead"])*SOLAR_INSTALLED/SOLAR_MONITORED
aggError = windError + solarError
dfError = pd.DataFrame(data={"wind":windError,"solar":solarError,"aggregator":aggError})

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

#Constraints
TIME_GRANULARITY = 4#h  TODO
TIME_TOTAL = 30*24#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)
VOLUME_GRANULARITY = 1 #MW
VOLUME_MIN = 1 #MW
RELIABILITY = 70 #%

#Product Characteristics
ACTIVATIONS = 2/12 #activations/M
ACTIVATION_DURATION = 1 #h
UNCERTAINTY = 20 #%

#Remuneration & Penalisation
EPEX_SPOT_PRICE = 70 #EUR/MW
ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
CAPACITY_REMUNERATION = 6 #EUR/MW/h
FINANCIAL_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation

# VOLUME ESTIMATION------------

quantiles = np.linspace(0,1,200)

#Time constraint
volumesC0 = df.copy()
volumesC0 = df[int(0*4*TIME_GRANULARITY):1*4*TIME_GRANULARITY].quantile(quantiles) #1Month
for i in range(1,TIME_GROUPS):
    volumesC0 += df[int(i*4*TIME_GRANULARITY):(i+1)*4*TIME_GRANULARITY].quantile(quantiles)
volumesC0 = volumesC0/TIME_GROUPS #taking the mean

##Forecast Horizon
#720h VS 168h VS 24h VS 4h
#TODO

#Forecast Uncertainty
#REMARK: commutative action with time constraint
volumesC1 = volumesC0.copy()
volumesC1 = volumesC1 + dfError.quantile(UNCERTAINTY/100) #Improvement: make error dependend of volume

#Volume constraint
volumesC2 = volumesC1.copy()
volumesC2 = volumesC1 - volumesC1%VOLUME_GRANULARITY
volumesC3 = volumesC2.copy(); volumesC3[volumesC1<VOLUME_MIN]=0

#Reliability constraint
volumesC4 = volumesC3.copy(); volumesC4[quantiles>(1-RELIABILITY/100)]=0

#Check uncertainty
plt.figure()
volumesC0["aggregator"].plot(label = "Compensated" + str(UNCERTAINTY)+"% Uncertainty")
df["aggregator"].plot(label = "24h Forecast")
plt.legend()

#Impact
plt.close("all")
plt.figure()
volumesC0["aggregator"].plot(label="C0 Granularity "+str(TIME_GRANULARITY) +"h",linestyle = ":")
volumesC1["aggregator"].plot(label="C1 Uncertainty "+str(UNCERTAINTY)+"%",linestyle = ":")
volumesC2["aggregator"].plot(label="C2 Granularity " + str(VOLUME_GRANULARITY)+"MW", linestyle = "--")
volumesC3["aggregator"].plot(label="C3 Minimum "+str(VOLUME_MIN)+"MW")
volumesC4["aggregator"].plot(label="C4 Reliability "+str(RELIABILITY)+"%")
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')
plt.title("Aggregator 130MWp")
plt.legend()

x = 1-RELIABILITY/100
y = volumesC1["aggregator"].quantile(x)
plt.plot([x], [y], 'o')
plt.annotate('C4 = Reliability ' + str(RELIABILITY) +"% \n"+ str(round(y,2))+ "MW",
            xy=(x,y),
            xytext=(.01,.01),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )
plt.show()

# VALUE ESTIMATION-------------

#TODO
#Proposal activation Penalty

#Reasonable reliabilities
#Assumption: ignore unreasonable reliabilities
quantiles = quantiles #np.array([0,0.003,0.01,0.05,0.10,0.15,0.20,0.50]) 
volumes = volumesC4

#Monthly Revenues
#Assumption: ignore reported non-availability

capacityRemuneration= TIME_TOTAL*CAPACITY_REMUNERATION*volumes
activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
activationPenalty = ACTIVATION_DURATION*FINANCIAL_PENALTY*volumes

#Components Expected Revenues Aggregator
plt.figure()
(capacityRemuneration["aggregator"]/10**3).plot(label = "capacity remuneration")
(ACTIVATIONS*activationRemuneration["aggregator"].multiply((1-quantiles),0)/10**3).plot(label = "activation remuneration")
(ACTIVATIONS*activationPenalty["aggregator"].multiply(quantiles,0)/10**3).plot(label = "financial penalty")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()
plt.show()

#Total Expected Revenues
#revenues1 = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
revenues1 = capacityRemuneration + ACTIVATIONS*(activationRemuneration.multiply((1-quantiles),0) - activationPenalty.multiply(quantiles,0))
(revenues1/10**3).plot()
((revenues1["aggregator"]-revenues1["wind"]-revenues1["solar"])/10**3).plot(label="added value aggregator")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()

#RECOMMENDATION ------------------
x = revenues1["aggregator"].idxmax()
y = revenues1["aggregator"][x]/10**3

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
