# -*- coding: utf-8 -*-
"""
Created on 27/04/2019
@author: Holger
"""

#%% SET_UP

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% DATA PREPROCESSING

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
data2016 = pd.read_csv("Data/data2016.csv")

SOLAR_MONITORED = 2952.78
SOLAR_MONITORED2016 = 2952.78
SOLAR_INSTALLED = 30
WIND_MONITORED = 2424.07
WIND_MONITORED2016 = 1960.91
WIND_INSTALLED = 100

#Preprocess data
wind8760 = data2016["wind"]*WIND_INSTALLED/WIND_MONITORED2016
solar8760 = data2016["solar"]*SOLAR_INSTALLED/SOLAR_MONITORED2016
agg8760 = wind8760 + solar8760

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

#Place data in a dataframe, easy to handle
df = pd.DataFrame(data={0:agg,4:agg4,24:agg24,168:agg168,8760:agg8760})
dfComponents = pd.DataFrame(data={"wind":wind,"solar":solar,"aggregator":agg})

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

quantiles = np.arange(0,1.01,.01)

plot1 = plt.plot(quantiles*100,dfComponents.quantile(quantiles))
addedValue = dfComponents["aggregator"].quantile(quantiles) - dfComponents["solar"].quantile(quantiles) - dfComponents["wind"].quantile(quantiles)
plot2 =plt.plot(quantiles*100,addedValue)

plt.plot([65], [addedValue[0.65]], 'o')

labels = list(dfComponents)
labels.append("Added Value Aggregator")
plot = plot1+plot2
plt.legend(plot, labels)
plt.xlabel('Quantiles [%]')
plt.ylabel('Power [MW]')

#%% CONSTANTS VOLUMES

#Constraints
TIME_GRANULARITY = 24#h
TIME_HORIZON = 24#h
VOLUME_GRANULARITY = 1#MW
VOLUME_MIN = 1#MW

ACTIVATION_DURATION = 1#h
UNCERTAINTY = 25
TIME_QUANTILE = 5 

#Product Characteristics
TIME_TOTAL = 30*24#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)

#%% VOLUME ESTIMATION

quantiles = np.arange(0,1,.0025)

#C1 TIME GRANULARITY------------
volumes = df[TIME_HORIZON]
volumesC0 = volumes[int(0*4*TIME_GRANULARITY):int(1*4*TIME_GRANULARITY)].quantile(quantiles) #1Month
for i in range(1,TIME_GROUPS):
    volumesC0 += volumes[int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)].quantile(quantiles)

#taking the mean
volumesC0 = volumesC0/TIME_GROUPS 

# C2 TIME HORIZON---------------
#REMARK: commutative property with time granularity

#Make a dictionary of indexbins and errorbins
indexbin = {}
errorbin = {}
errSd = list()
errN = list()
step = 4
minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
maxbin = df[TIME_HORIZON].max()
fig,axes = plt.subplots(5,5)

#Iterate over all bins
for i,x in enumerate(np.arange(minbin,maxbin,step)):
    indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
    errorbin[x] = df[0][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
    errSd.append(errorbin[x].std())
    errN.append(len(errorbin[x]))
    
    if i !=25:
        #error density plot + standard deviation per bin
        errorbin[x].plot.density(ax = axes[int(i/5),i%5])
        axes[int(i/5),i%5].set_title("Error bin of " + str(x) + "MW")
    
#Illustrate standard deviation + amount of sample per bin
fig,axes = plt.subplots(1,2)
axes[0].plot(np.arange(minbin,maxbin,step),errSd)
axes[1].plot(np.arange(minbin,maxbin,step),errN)

#add forecast error
volumesC1 = volumesC0.copy()
keys = (volumesC1-volumesC1%step).astype("int")
volumesC1 = volumesC1 + [errorbin[key].quantile(UNCERTAINTY/100) for key in keys]
volumesC1[volumesC1<0]=0

# VOLUME CONSTRAINT----------------

#volume granularity
volumesC2 = volumesC1 - volumesC1%VOLUME_GRANULARITY

#volume minimum
volumesC3 = volumesC2.copy(); volumesC3[volumesC1<VOLUME_MIN]=0



# ILLUSTRATE-----------------------

#make plot
plt.figure()

plt.axhline(df[0].mean(),label="Unconstrained Real Time")

volumesC0.plot(label="C1 Granularity "+str(TIME_GRANULARITY) +"h",linestyle = ":")

volumesC1.plot(label="C2 Horizon "+str(TIME_HORIZON)+"h",linestyle = ":")

volumesC3.plot(label="C3a Granularity " + str(VOLUME_GRANULARITY)+"MW"+
               "\nC3b Minimum "+str(VOLUME_MIN)+"MW",linestyle = "--")

plt.xlabel('Time Quantile [%]')
plt.ylabel('Volume [MW]')
plt.title("Downward Reserves 130MWp Aggregator\n\n"+
          "Time total "+str(TIME_TOTAL)+"h, Uncertainty "+str(UNCERTAINTY)+"%, Time quantile "+str(TIME_QUANTILE)+"%")
plt.legend()

#Label preferred time quantile
x = TIME_QUANTILE/100
y = volumesC3[x]
plt.plot([x], [y], 'o')
plt.annotate('Time Quantile ' + str(TIME_QUANTILE) +"% \n"+ str(round(y,2))+ "MW",
            xy=(x,y),
            xytext=(.4,.2),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )
plt.show()

#%% CONSTANTS FINANCIALS 

#Activation Frequency
TIME_DURATION = 24#h
ACTIVATIONS = 2/12 #activations/M

#financials
EPEX_SPOT_PRICE = 70 #EUR/MW
CAPACITY_REMUNERATION = 6 #EUR/MW/h
ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
ACTIVATION_PENALTY = 50*120*CAPACITY_REMUNERATION #EUR/MWh/activation


#%% VALUE ESTIMATION

quantiles = quantiles #np.array([0,0.003,0.01,0.05,0.10,0.15,0.20,0.50]) 
volumes = volumesC3

#Monthly Revenues
#Assumption: ignore reported non-availability
capacityRemuneration= TIME_TOTAL*CAPACITY_REMUNERATION*volumes
activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*volumes

#revenues = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
#Binomial distribution of succesful activations with chance selected reliability
revenues = capacityRemuneration + ACTIVATIONS*(activationRemuneration.multiply((1-quantiles),0) - activationPenalty.multiply(quantiles,0))

#Components Expected Revenues Aggregator
plt.figure()
(capacityRemuneration/10**3).plot(label = "capacity remuneration")
(ACTIVATIONS*activationRemuneration.multiply((1-quantiles),0)/10**3).plot(label = "activation remuneration")
(ACTIVATIONS*activationPenalty.multiply(quantiles,0)/10**3).plot(label = "financial penalty")
(revenues/10**3).plot(label = "Expected revenues")
plt.xlabel("Quantiles")
plt.ylabel("Revenues [k€/Month]")
plt.legend()
plt.show()

#RECOMMENDATION ------------------
x = revenues.idxmax()
y = revenues[x]/10**3

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
