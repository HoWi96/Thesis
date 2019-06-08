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
TENNET = 0
step = 0.02

if TENNET == 1:
    print("TenneT 2018 selected")
    #Constraints
    TIME_GRANULARITY = 720#h
    TIME_HORIZON = str(8760)#h
    VOLUME_GRANULARITY = 5#MW
    VOLUME_MIN = 20#MW
    suptitle = (r"$\bf Case \: TenneT \: 2018$"+"\nSimulation of 720h\n"+
            "GCT + 320h Start CP, 720h Contracting Period, 720h Resolution, 5MW Resolution, 20MW Minimum")
else:
    print("Elia 2020 selected")
    TIME_GRANULARITY = 4#h
    TIME_HORIZON = str(24)#h
    VOLUME_GRANULARITY = 1#MW
    VOLUME_MIN = 1#MW
    suptitle = (r"$\bf Case \: Elia \: 2020$"+"\nSimulation of 720h\n"+
            "GCT + 14h Start CP, 24h Contracting Period, 4h Resolution, 1MW Resolution, 1MW Minimum")

#Product Characteristics
TIME_TOTAL = int(solar.shape[0]/4)#h
TIME_GROUPS = int(TIME_TOTAL/TIME_GRANULARITY)

#quantiles
reliability = 1-np.arange(0,1.01,step)
bidVolume = np.zeros((reliability.shape[0],df0.shape[1]))
volumeMissing = np.zeros((reliability.shape[0],df0.shape[1]))
volumeLost = np.zeros((reliability.shape[0],df0.shape[1]))

#Compute------------------

#iterate over all sources
for idx,df in enumerate([solar,wind,agg,demand,solar*0.25,wind*0.75]):
    print("Processing Source "+str(idx))
    realizedVolumes = df["0"]
    
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
        
        differenceVolumes = realizedVolumes-bid2
        volumeMissing[k,idx] = -np.sum(differenceVolumes[differenceVolumes<0])/(TIME_TOTAL*4)
        volumeLost[k,idx] = np.sum(differenceVolumes[differenceVolumes>0])/(TIME_TOTAL*4)
    
#%%ILLUSTRATE
print("Illustrate Volumes")

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
col = ["C0",'C1','C2','C3','C4','C5','C6']

#compute
plt.close("all")
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

#iterate over sources
for k,source in enumerate(["solar","wind","agg","demand"]):
    axes[int(k/2),k%2].plot(reliability*100, bidVolume[:,k],label = "Mean Offered Volume")
    axes[int(k/2),k%2].plot(reliability*100, volumeMissing[:,k],label = "Mean Missing Volume")
    axes[int(k/2),k%2].plot(reliability*100, volumeLost[:,k],label = "Mean Lost Volume")
    
    if source == "agg":
         volumeRef = bidVolume[:,4]+bidVolume[:,5]
         volumeMissingRef = volumeMissing[:,4]+volumeMissing[:,5]
         volumeLostRef = volumeLost[:,4]+volumeLost[:,5]
         
         axes[int(k/2),k%2].plot(reliability*100,volumeRef, linestyle ='-.', label = "MOV - Sources seperated", color = col[0])
         axes[int(k/2),k%2].plot(reliability*100,volumeMissingRef,linestyle ='-.',label = "MMV - Sources seperated",color = col[1])
         axes[int(k/2),k%2].plot(reliability*100,volumeLostRef,linestyle ='-.', label = "MLV - Sources seperated",color = col[2])
     
    axes[int(k/2),k%2].legend()
    axes[int(k/2),k%2].set_xlabel("Reliability [%]")
    axes[int(k/2),k%2].set_ylabel("Volume [MW]")
    axes[int(k/2),k%2].set_ylim(0)
    axes[int(k/2),k%2].set_xlim(0,100)
    axes[int(k/2),k%2].set_title(titles[k])
     
print(np.round(bidVolume/np.matmul(np.ones((len(reliability),6)),np.diag(df0.mean())),3))

#%%#####################################################################
# FINANCIALS
########################################################################

#%% PROCESS
print("Process Financials")

#initialize
reliability = reliability
volumes = bidVolume

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
            "2/12 Activations/Y, 1h Activation Duration, 720€/MWh Activation Penalty")
    ########################
    
    #Capacity Remuneration
    capacityRemuneration = CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    
    #Revenues per activation
    activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    
    #Costs per activation
    activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*volumes
    
    #Revenues
    revenuesCapacity =   capacityRemuneration
    revenuesEnergy =     ACTIVATIONS*np.matmul(np.diag(reliability),activationRemuneration)
    costsMonitoring =   np.zeros(capacityRemuneration.shape)
    costsActivation =    ACTIVATIONS*np.matmul(np.diag(1-reliability),activationPenalty)
    
else:
    #Bids
    bidCapacity = 6 #EUR/MW/h
    bidEnergy = 120 #EUR/MWh/activation
    
    #Market Parameters
    durationActivation = 4#h
    durationCapacity = 720#h
    durationMonth = 720#h
    factor = 1.3#%
    activations = 2/12 #activations/M
    tests = 12/12 #activations/M
    volumeCapacity = volumes
    volumeActivation = volumes
    
    #External Determined
    tariff = 120 #EUR/MWh/activation
    suptitle = (r"$\bf Case \: Elia \: 2020$"+"\nSimulation Time 720h\n"+
            "6€/MW/h Capacity Remuneration, 120€/MWh Activation Remuneration\n"+ 
            "1 Test/M, 5.62k€/MW Test Penalty, 1/12 Activation/M, 4h Activation Duration, 120€/MWh Tariff")

    ########################
    
    #FORMULAS#
    penaltyMonitoring = volumeMissing*factor*bidCapacity*durationMonth
    penaltyActivation = volumeMissing*tariff*durationActivation

    revenuesCapacity =  volumeCapacity*bidCapacity*durationCapacity
    revenuesEnergy =    activations*volumeActivation*bidEnergy*durationActivation
    costsMonitoring =   np.matmul(np.diag(1-reliability),tests*penaltyMonitoring)
    costsActivation =   np.matmul(np.diag(1-reliability),activations*penaltyActivation)
    
revenuesTotal = revenuesCapacity + revenuesEnergy
costsTotal = costsMonitoring + costsActivation
revenuesNet = revenuesTotal - costsTotal
    
#%% ILLUSTRATE
print("Illustrate Financials")
print("\a")
print("Revision of code and illustrations needed")
#initialize
fig,axes = plt.subplots(2,2)
plt.suptitle(suptitle)

for k,source in enumerate(["solar","wind","agg","demand"]):
    axes[int(k/2),k%2].plot(reliability*100, revenuesNet[:,k]/10**3,linewidth=1.5,label = "Expected Net Revenues")
    axes[int(k/2),k%2].plot(reliability*100, revenuesTotal[:,k]/10**3, linestyle = "-", label = "Expected Total Revenues")
    axes[int(k/2),k%2].plot(reliability*100, costsTotal[:,k]/10**3, linestyle = "-", label = "Expected Total Costs")
    
    #mean added volume
    if source == "agg":
        revenuesRef = revenuesNet[:,4]+revenuesNet[:,5]
        axes[int(k/2),k%2].plot(reliability*100,revenuesRef/10**3, linestyle ='-.',linewidth = 0.5, color ="C0",label="ENR - Seperated Sources")
        
    axes[int(k/2),k%2].set_xlabel("Reliability [%]")
    axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
    axes[int(k/2),k%2].legend()
    axes[int(k/2),k%2].set_ylim(0)
    axes[int(k/2),k%2].set_xlim(0,100)
    axes[int(k/2),k%2].set_title(titles[k])
    
    ##RECOMMENDATION ------------------
    x = reliability[np.argmax(revenuesNet[:,k])]*100
    y = np.amax(revenuesNet[:,k])/10**3
    
    axes[int(k/2),k%2].plot([x], [y], 'o')
    axes[int(k/2),k%2].annotate(str(round(y,2))+"k€/M",
                                    xy=(x,y),
                                    #xytext=(0.4,0.8),
                                    #textcoords = "figure fraction",
                                    arrowprops=dict(facecolor='black', shrink=0.05),
                                    horizontalalignment='left',
                                    verticalalignment='bottom'
                                    )
    
print(str(reliability[np.argmax(revenuesNet,axis = 0)]))
    
   
print("Finished Case Study")
print("\a")
