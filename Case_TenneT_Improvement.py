# -*- coding: utf-8 -*-
"""
Created on 27/04/2019
@author: Holger
"""

#IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Methodology_Integration_Volumes import calculateVolume
import PreprocessData as pre

solarRaw,windRaw,demandRaw,allRaw2016 = pre.importData()
solar,wind,agg,demand = pre.preprocessData(solarRaw,windRaw,demandRaw,allRaw2016)
df0 = pd.DataFrame(data={"solar":solar["0"],"wind":wind["0"],"agg":agg["0"],"demand":demand["0"],
                        "solar25":solar["0"]*0.25,"wind75":wind["0"]*0.75})

#%%#####################################################################
# VOLUMES 
########################################################################

#%%PROCESS
print("Process Volumes")

#Initialize---------

#cases
TENNET = 1
if TENNET == 1:
    print("TenneT 2018 selected")
    #Constraints
    TIME_GRANULARITY = 720#h
    TIME_HORIZON = str(8760)#h
    VOLUME_GRANULARITY = 5#MW
    VOLUME_MIN = 20#MW
else:
    print("Elia 2020 selected")
    TIME_GRANULARITY = 4#h
    TIME_HORIZON = str(24)#h
    VOLUME_GRANULARITY = 1#MW
    VOLUME_MIN = 1#MW
    suptitle = (r"$\bf Case \: Elia \: 2020$"+"\nSimulation Time 720h\n"+
            "24h-Ahead Forecast, 4$\Delta$h Resolution, 1$\Delta$MW Resolution, 1MW Minimum ")

#Product Characteristics
TIME_TOTAL = int(solar.shape[0]/4)#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)

#quantiles
step = 0.05
reliability = 1-np.arange(0,1+step/2,step)
bidVolume = np.zeros((reliability.shape[0],df0.shape[1]))

#Compute------------------

#iterate over all sources
for idx,df in enumerate([solar,wind,agg,demand,solar*0.25,wind*0.75]):
    print("Processing Source "+str(idx))
    
    # (1) Initialize errorbins
    indexbin = {}
    errorbin = {}
    step = 4
    minbin = round(df[TIME_HORIZON].min()- df[TIME_HORIZON].min()%step)
    maxbin = df[TIME_HORIZON].max()
    
    # (2) Compute Errorbins
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
            interval = df[TIME_HORIZON][int(i*4*TIME_GRANULARITY):int((i+1)*4*TIME_GRANULARITY)+1]
            volume = calculateVolume(interval,errorbin,step,rel)
            if volume < 0: 
                volume = 0
            bid = np.concatenate((bid, np.ones(int(TIME_GRANULARITY*4))*volume))
    
        # (4) Adjust to volume resolution
        bid2 = bid - bid%VOLUME_GRANULARITY
        
        # (5) Adjust to volume minimum
        bid2[bid2<VOLUME_MIN] = 0
        
        # (6) Take volume mean
        bidVolume[k,idx] = bid2.mean()
    
#%%ILLUSTRATE
print("Illustrate Volumes")

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]

#compute
plt.close("all")
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

#iterate over sources
for k,source in enumerate(["solar","wind","agg","demand"]):
    
    #mean bid volume
    MBV = bidVolume[:,k]
    
    #mean effective volume
    MEV = np.ones(reliability.shape)*df0[source].mean()
    
    #Reliable bid volume
    RBV = np.ones(reliability.shape)*bidVolume[0,k]
    
    axes[int(k/2),k%2].plot(reliability*100,MBV,linewidth=1.5,color = "C0")
    axes[int(k/2),k%2].plot(reliability*100,MEV,linewidth=1,linestyle = "--",color = "C0")
    axes[int(k/2),k%2].fill_between(reliability*100,MBV,RBV,color = "C0",alpha = 0.1)
    axes[int(k/2),k%2].fill_between(reliability*100,0,RBV,color = "C1",alpha = 0.1)
    
    axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Unreliable Volume","Mean Reliable Volume"))
    axes[int(k/2),k%2].set_xlabel('Reliability [%]')
    axes[int(k/2),k%2].set_ylabel('Bid Volume [MW]')
    axes[int(k/2),k%2].set_ylim(0,44)
    axes[int(k/2),k%2].set_title(titles[k]) 
    
    #mean added volume
    if source == "agg":
        reference = bidVolume[:,4]+bidVolume[:,5]
        
        axes[int(k/2),k%2].fill_between(reliability*100,MBV,reference,color = "C2",alpha = 0.2)
        axes[int(k/2),k%2].legend(("Mean Bid Volume", "Mean Effective Volume","Mean Unreliable Volume","Mean Reliable Volume","Mean Added Volume"))
        axes[int(k/2),k%2].plot(reliability*100,reference,linewidth=1,linestyle ='--',color = "C2")
        
    axes[int(k/2),k%2].plot(reliability*100,RBV,linewidth=1,linestyle = "--",color = "C1")
#%%#####################################################################
# FINANCIALS
########################################################################

#%% PROCESS
print("Process Financials")

#initialize
#reliability = reliability
#volumes = bidVolume
step = 0.2
reliability = 1-np.arange(0,1+step/2,step)
volumes = np.array([[  5.79444444,  10.78888889,  10.02222222,  18.79444444, 1.06111111, 7.7],
                   [ 13.46666667,  19.33333333,  18.7       ,  26.33888889,3.23333333,  14.37222222],
                   [ 17.42222222,  21.97222222,  21.11666667,  28.30555556,4.16666667,  16.36111111],
                   [ 21.58333333,  24.34444444,  23.39444444,  30.4       ,5.06666667,  18.18333333],
                   [ 26.31111111,  27.41111111,  26.18333333,  32.83333333,6.32777778,  20.47222222],
                   [ 39.47777778,  41.55555556,  38.52222222,  38.3       ,11.66666667,  31.67777778]])

#compute
if TENNET == 1:
    #Bids
    CAPACITY_REMUNERATION = 6 #EUR/MW/h
    
    #Market Parameters
    CAPACITY_DURATION = 720#h
    ACTIVATION_DURATION = 1#h
    ACTIVATION_PENALTY = 120*CAPACITY_REMUNERATION #EUR/MWh/activation
    
    #External Determined
    EPEX_SPOT_PRICE = 100 #EUR/MW
    ACTIVATION_REMUNERATION = 250-EPEX_SPOT_PRICE #EUR/MWh/activation
    ACTIVATIONS = 2/12 #activations/M
    suptitle = (r"$\bf Case \: TenneT \: 2018$"+"\nSimulation Time 720h\n"+
            "6€/MW/h Capacity Remuneration, 150€/MWh Activation Remuneration\n"+ 
            "0.17/M Activations, 1h Activation Duration, 0% Capacity Penalty, 720€ Activation Penalty")
    ########################
    
    #Capacity Remuneration
    capacityRemuneration = CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    
    #Revenues per activation
    activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    
    #Costs per activation
    activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*volumes
    
    #Revenues
    capacityRevenues=   capacityRemuneration
    capacityCosts = np.zeros(capacityRemuneration.shape)
    activationRevenues= ACTIVATIONS*np.matmul(np.diag(reliability),activationRemuneration)
    activationCosts=    ACTIVATIONS*np.matmul(np.diag(1-reliability),activationPenalty)
    
else:
    #Bids
    CAPACITY_REMUNERATION = 6 #EUR/MW/h
    ACTIVATION_REMUNERATION = 150 #EUR/MWh/activation
    
    #Market Parameters
    ACTIVATIONS = 12/12 #activations/M
    ACTIVATION_DURATION = 4#h
    CAPACITY_DURATION = 720#h
    CAPACITY_PENALTY = 150#%
    
    #External Determined
    ACTIVATION_PENALTY = 150 #EUR/MWh/activation
    suptitle = (r"$\bf Case \: Elia \: 2020$"+"\nSimulation Time 720h\n"+
            "6€/MW/h Capacity Remuneration, 150€/MWh Activation Remuneration\n"+ 
            "1/M Activations, 4h Activation Duration, 150% Capacity Penalty, 150€ Activation Penalty")

    ########################
    
    #Capacity Remuneration
    capacityRemuneration = CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    
    #Revenues per activation
    activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    
    #Costs per activation
    activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*(volumes-volumes[0,:])
    capacityPenalty = CAPACITY_PENALTY/100*(capacityRemuneration-capacityRemuneration[0,:])
    
    #revenues
    capacityRevenues =   np.matmul(np.diag(1-(1-reliability)**3), capacityRemuneration) + 0 * (1-reliability)**3
    capacityCosts =      np.matmul(np.diag(1-(1-reliability)**3), np.matmul(np.diag(1-reliability),capacityPenalty))
    activationRevenues = np.matmul(np.diag(1-(1-reliability)**3), ACTIVATIONS*np.matmul(np.diag(reliability),activationRemuneration))
    activationCosts =    np.matmul(np.diag(1-(1-reliability)**3), ACTIVATIONS*np.matmul(np.diag(1-reliability),activationPenalty))
    
#revenues
revenues = capacityRevenues + activationRevenues - activationCosts  - capacityCosts
    
#%% ILLUSTRATE
print("Illustrate Financials")

#initialize
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

for k,source in enumerate(["solar","wind","agg","demand"]):
    axes[int(k/2),k%2].plot(reliability*100, revenues[:,k]/10**3,linewidth=2.5,)
    axes[int(k/2),k%2].plot(reliability*100, capacityRevenues[:,k]/10**3, linestyle = "-",linewidth=1)
    axes[int(k/2),k%2].plot(reliability*100, activationRevenues[:,k]/10**3, linestyle = "-",linewidth=1)
    axes[int(k/2),k%2].plot(reliability*100, (capacityCosts[:,k]+activationCosts[:,k])/10**3, linestyle = "-",linewidth=1)
    
    
    axes[int(k/2),k%2].set_xlabel("Reliability [%]")
    axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
    axes[int(k/2),k%2].set_title(titles[k])
    axes[int(k/2),k%2].legend(("Mean Revenues", "Mean Capacity Remuneration","Mean Activation Remuneration","Mean Activation Penalty"))
    
        #mean added volume
    if source == "agg":
        reference = (revenues[:,4]+revenues[:,5])
        
        axes[int(k/2),k%2].fill_between(reliability*100,revenues[:,2]/10**3,reference/10**3,color = "turquoise",alpha = 0.2)
        axes[int(k/2),k%2].legend(("Mean Revenues", "Mean Capacity Remuneration","Mean Activation Remuneration","Mean Activation Penalty","Mean Added Value"))
        axes[int(k/2),k%2].plot(reliability*100,reference/10**3,linewidth=1,linestyle ='--',color = "turquoise")

    ##RECOMMENDATION ------------------
    x = reliability[np.argmax(revenues[:,k])]*100
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
    
   
print("Finished Case Study")
print("\a")
