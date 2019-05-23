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

print("START Case TenneT")

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

#%%#####################
########################
# VOLUMES 
########################
########################

#Constraints
TIME_GRANULARITY = 720#h
TIME_HORIZON = str(8760)#h
VOLUME_GRANULARITY = 5#MW
VOLUME_MIN = 20#MW

#Product Characteristics
TIME_TOTAL = int(solar.shape[0]/4)#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)
########################

#quantiles
step = 0.1
reliability = 1-np.arange(0,1+step/2,step)
volumeReliability = np.zeros((reliability.shape[0],4))

#[solar,wind,agg,demand]
for idx,df in enumerate([solar]):
    print("Processing Source "+str(idx))
    
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
    
    #loop over all reliabilities
    for k,rel in enumerate(reliability):
        print(rel)
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
        volumeReliability[k,idx] = bid2.mean()
    
#%%########################
# ILLUSTRATE
        
print("Processing illustration")

##Reference Case Of ideal market
plt.close("all")
plt.figure()

for idx,df in enumerate([solar,wind,agg,demand]):
    plt.plot(reliability*100,volumeReliability[:,idx])

#Illustrate bidding

titles = ["(a) Solar PV 100MWp Down",
          "(b) Wind 100MWp Down",
          "(c) Aggregator 100MWp Down",
          "(d) Demand 100MWp Up (SL = 30MW)"]
plt.legend(titles)
plt.xlabel('Reliability [%]')
plt.ylabel('Volume [MW]')
plt.xlim((0,100))
plt.ylim(0)
plt.title("TenneT mFRR 20XX\n\n"+
          str(TIME_HORIZON) + "h-Ahead Forecast, " +
          str(TIME_GRANULARITY) + "h Resolution, " +
          str(VOLUME_GRANULARITY) + "MW Resolution, " +
          str(VOLUME_MIN) + "MW Minimum, " +
          str(TIME_TOTAL) + "h Total Time")

col = ['C0', 'C1', 'C2', 'C3']
for idx,df in enumerate([solar,wind,agg,demand]):
    plt.plot(reliability*100,np.ones(reliability.shape)*df[str(0)].mean(),linestyle = "--",color = col[idx])

#%%#####################
########################
# FINANCIALS 
########################
########################
TENNET = 0

print("START Financials")


reliability = reliability
volumes = volumeReliability

if TENNET == 1:
    print("TenneT 2018 selected")
    #Activation Frequency
    ACTIVATIONS = 2/12 #activations/M
    ACTIVATION_DURATION = 1#h
    CAPACITY_DURATION = 720#h
    
    #financials
    EPEX_SPOT_PRICE = 70 #EUR/MW
    CAPACITY_REMUNERATION = 6 #EUR/MW/h
    ACTIVATION_REMUNERATION = max(250-EPEX_SPOT_PRICE,0) #EUR/MWh/activation
    ACTIVATION_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation
        
    ########################
    
    #Monthly Revenues
    #Assumption: ignore reported non-availability
    capacityRemuneration =      CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    activationRemuneration =    ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    activationPenalty =         ACTIVATION_DURATION*ACTIVATION_PENALTY*volumes
    
    #revenues = capacityRemuneration + E[activationRemuneration] - E[finacialPenalty]
    #Binomial distribution of succesful activations with chance selected reliability
    capacityRevenues = capacityRemuneration
    activationRevenues = ACTIVATIONS*(np.matmul(np.diag(reliability),activationRemuneration))
    activationCosts = ACTIVATIONS*np.matmul(np.diag(1-reliability),activationPenalty)
    
else:
    print("Elia 2020 selected")
    #Activation Frequency
    ACTIVATIONS = 4 #activations/M
    ACTIVATION_DURATION = 4#h
    CAPACITY_DURATION = 720#h
    
    #financials
    CAPACITY_REMUNERATION = 6 #EUR/MW/h
    ACTIVATION_REMUNERATION = 150 #EUR/MWh/activation
    ACTIVATION_PENALTY = 100 #EUR/MWh/activation
    
    #capacity remuneration on the full volume bid
    capacityRemuneration =      CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    capacityRemuneration100 =   np.tile(CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes[0,:],(11,1))
    
    #activation remuneration on the full volume bid
    activationRemuneration =    ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    activationRemuneration100 = np.tile(ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes[0,:],(11,1))
    
    #activation penalty settled via reserve market on missed volumes
    activationPenalty =         ACTIVATION_DURATION*ACTIVATION_PENALTY*(volumes-volumes[0,:])
    
    capacityRevenues = (np.matmul(np.diag(reliability),capacityRemuneration)+
                        np.matmul(np.diag(1-reliability),capacityRemuneration100))
    activationRevenues = ACTIVATIONS*(np.matmul(np.diag(reliability),activationRemuneration) + 
                                      np.matmul(np.diag(1-reliability),activationRemuneration100))
    activationCosts = np.matmul(np.diag(1-reliability),activationPenalty)
  
#revenues
revenues = capacityRevenues + activationRevenues - activationCosts
    
#%%########################
# ILLUSTRATE
fig,axes = plt.subplots(2,2)
titles = ["(a) Solar PV 100MWp Down",
          "(b) Wind 100MWp Down",
          "(c) Aggregator 100MWp Down",
          "(d) Demand 100MWp Up (SL = 30MW)"]

for k,source in enumerate(volumes.transpose()):
    axes[int(k/2),k%2].plot(reliability, capacityRevenues[:,k]/10**3, label = "Capacity Remuneration")
    axes[int(k/2),k%2].plot(reliability, activationRevenues[:,k]/10**3, label = "Activation Remuneration")
    axes[int(k/2),k%2].plot(reliability, activationCosts[:,k]/10**3, label = "Activation Penalty")
    axes[int(k/2),k%2].plot(reliability, revenues[:,k]/10**3, label = "Expected revenues")
    
    axes[int(k/2),k%2].set_xlabel("Reliability")
    axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
    axes[int(k/2),k%2].set_title(titles[k])
    axes[int(k/2),k%2].legend()

    ##RECOMMENDATION ------------------
    x = reliability[np.argmax(revenues[:,k])]
    y = np.amax(revenues[:,k])/10**3
    
    axes[int(k/2),k%2].plot([x], [y], 'o')
    axes[int(k/2),k%2].annotate(str(round(y,2))+"k€/M",
                                    xy=(x,y),
                                    #xytext=(0.4,0.8),
                                    #textcoords = "figure fraction",
                                    arrowprops=dict(facecolor='black', shrink=0.05),
                                    horizontalalignment='left',
                                    verticalalignment='bottom'
                                    )

    
print("STOP Financials")
print("\a")

#%% BREAKEVEN SANCTIONS VS REMUNERATION

breakeven = capacityRemuneration/activationPenalty
breakeven = 720/120
