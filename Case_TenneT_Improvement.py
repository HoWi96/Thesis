# -*- coding: utf-8 -*-
"""
Created on 27/04/2019
@author: Holger
"""

#%% IMPORTS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Methodology_Integration_Volumes import calculateVolume

solarRaw = pd.read_csv("Data/SolarForecastJune2017.csv")
windRaw = pd.read_csv("Data/WindForecastJune2017.csv")
demandRaw = pd.read_csv("Data/LoadForecastJune2017.csv")
allRaw2016 = pd.read_csv("Data/data2016.csv")

#%% DATA PREPROCESSING

WIND_INST = 2403.17
SOLAR_INST= 2952.78
DEMAND_PK= 11742.29
WIND_INST2016 = 1960.91
SOLAR_INST2016= 2952.78
DEMAND_PK2016 = 11589.6

#Preprocess data
solar = solarRaw.loc[:, solarRaw.columns != "DateTime"]*100/SOLAR_INST
solar[str(8760)] = allRaw2016["solar"]*100/SOLAR_INST2016

wind = windRaw.loc[:, windRaw.columns != "DateTime"]*100/WIND_INST
wind[str(8760)] = allRaw2016["wind"]*100/WIND_INST2016

demand = demandRaw.loc[:, demandRaw.columns != "DateTime"]*100/DEMAND_PK
demand[str(8760)] = allRaw2016["load"]*100/DEMAND_PK2016
demand = demand - 30 #shedding limit

agg = solar*0.25+wind*0.75

#Place data in a dataframe, easy to handle
df = agg

#%%#####################
########################
# VOLUMES 
########################
########################
#Constraints
TIME_GRANULARITY = 24#h
TIME_HORIZON = str(168)#h
VOLUME_GRANULARITY = 1#MW
VOLUME_MIN = 1#MW

#Product Characteristics
TIME_TOTAL = int(df.shape[0]/4)#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)
########################
plt.close("all")
plt.figure()

for df in [solar,wind,demand,agg]:
    # (1) Initialize errorbins
    indexbin = {}
    errorbin = {}
    step = 4
    minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
    maxbin = df[TIME_HORIZON].max()
    
    # (2) Create Errorbins
    for i,x in enumerate(np.arange(minbin,maxbin,step)):
        indexbin[x] = np.where(np.column_stack((df[TIME_HORIZON]>(x-step*1.5),df[TIME_HORIZON]<(x+step*1.5))).all(axis=1))[0]
        errorbin[x] = df[str(0)][indexbin[x]]-df[TIME_HORIZON][indexbin[x]]
        
    # (3) Get a volume for each interval volume = f(reliability,interval)
    
    #quantiles
    reliability = 1-np.arange(0,1,.1)
    volumeReliability = np.zeros(reliability.shape)
    
    #loop over all reliabilities
    for k,rel in enumerate(reliability):
        bid = []
        
        #loop over intervals
        for i in range(0,int(TIME_TOTAL/TIME_GRANULARITY)):
            interval = df[TIME_HORIZON][int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)]
            volume = calculateVolume(interval,errorbin,step,rel)
            if volume < 0: 
                volume = 0
            bid = np.concatenate((bid, np.ones(int(TIME_GRANULARITY*4))*volume))
    
        # (4) Adjust to volume resolution
        bid2 = bid - bid%VOLUME_GRANULARITY
        
        # (5) Adjust to volume minimum
        bid2[bid2<VOLUME_MIN] = 0
        
        # (6) Take mean for reliability
        volumeReliability[k] = bid2.mean()
    plt.plot(reliability*100,volumeReliability)
    plt.plot(reliability*100,np.ones(reliability.shape)*df[str(0)].mean(),linestyle = "--")
    
#%%########################
# ILLUSTRATE

##Reference Case Of ideal market
#

#Illustrate bidding

titles = ["(a) Solar PV 100MWp Down",
          "(a) Ideal Market",
          "(b) Wind 100MWp Down",
          "(b) Ideal Market",
          "(c) Aggregator 100MWp Down",
          "(c) Ideal Market",
          "(d) Demand 100MWp Up (SL = 30MW)",
          "(d) Ideal Market"]
plt.legend(titles)
plt.xlabel('Reliability [%]')
plt.ylabel('Volume [MW]')
plt.title("Downward Reserves 100MWp Aggregator\n"+
          str(TIME_HORIZON) + "h-Ahead Forecast,\n" +
          str(TIME_GRANULARITY) + "h Resolution,\n" +
          str(VOLUME_GRANULARITY) + "MW Resolution,\n" +
          str(VOLUME_MIN) + "MW Minimum,\n" +
          str(TIME_TOTAL) + "h Total Time")

RELIABILITY = 90
#Label preferred time quantile
x = RELIABILITY
y = volumeReliability[reliability== RELIABILITY/100][0]
plt.plot([x], [y], 'o')
plt.annotate('Reliability ' + str(RELIABILITY) +"% \n"+ str(round(y,2))+ "MW",
            xy=(x,y),
            xytext=(.4,.2),
            textcoords = "figure fraction",
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='left',
            verticalalignment='bottom',
            )

##%%#####################
#########################
## FINANCIALS 
#########################
#########################
##Activation Frequency
#TIME_DURATION = 24#h
#ACTIVATIONS = 2/12 #activations/M
#ACTIVATION_DURATION = 1#h
#
##financials
#EPEX_SPOT_PRICE = 70 #EUR/MW
#CAPACITY_REMUNERATION = 6 #EUR/MW/h
#ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
#ACTIVATION_PENALTY = 50*120*CAPACITY_REMUNERATION #EUR/MWh/activation
#########################
#
#
#quantiles = quantiles #np.array([0,0.003,0.01,0.05,0.10,0.15,0.20,0.50]) 
#volumes = volumesC3
#
##Monthly Revenues
##Assumption: ignore reported non-availability
#capacityRemuneration= TIME_TOTAL*CAPACITY_REMUNERATION*volumes
#activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
#activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*volumes
#
##revenues = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
##Binomial distribution of succesful activations with chance selected reliability
#revenues = capacityRemuneration + ACTIVATIONS*(activationRemuneration.multiply((1-quantiles),0) - activationPenalty.multiply(quantiles,0))
#
##%%########################
## ILLUSTRATE
#
#plt.figure()
#(capacityRemuneration/10**3).plot(label = "capacity remuneration")
#(ACTIVATIONS*activationRemuneration.multiply((1-quantiles),0)/10**3).plot(label = "activation remuneration")
#(ACTIVATIONS*activationPenalty.multiply(quantiles,0)/10**3).plot(label = "financial penalty")
#(revenues/10**3).plot(label = "Expected revenues")
#plt.xlabel("Quantiles")
#plt.ylabel("Revenues [k€/Month]")
#plt.legend()
#plt.show()
#
##RECOMMENDATION ------------------
#x = revenues.idxmax()
#y = revenues[x]/10**3
#
#plt.plot([x], [y], 'o')
#plt.annotate('financial optimum '+str(round(y,2))+"k€/M",
#            xy=(x,y),
#            xytext=(0.65,0.9),
#            textcoords = "figure fraction",
#            arrowprops=dict(facecolor='black', shrink=0.05),
#            horizontalalignment='left',
#            verticalalignment='bottom',
#            )
#plt.show()
#
##%% BREAKEVEN SANCTIONS VS REMUNERATION
#
#breakeven = capacityRemuneration/activationPenalty
#breakeven = 720/120
