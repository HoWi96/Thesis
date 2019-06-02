# -*- coding: utf-8 -*-
"""
Created on Sun May 26 23:34:08 2019

@author: user
"""
import numpy as np
import matplotlib.pyplot as plt

#%% PROCESS
print("START monitoring design")

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]

volumes = np.array([[  5.79444444,  10.78888889,  10.02222222,  18.79444444, 1.06111111,   7.7       ],
                    [  9.88333333,  16.        ,  15.66111111,  23.87777778,2.28888889,  11.86666667],
                   [ 11.20555556,  17.50555556,  17.05      ,  24.96666667,2.64444444,  12.96111111],
                   [ 12.33333333,  18.52777778,  17.91666667,  25.73333333,2.93333333,  13.72777778],
                   [ 13.46666667,  19.33333333,  18.7       ,  26.33888889,3.23333333,  14.37222222],
                   [ 14.53888889,  20.04444444,  19.33888889,  26.94444444,3.42777778,  14.93333333],
                   [ 15.52777778,  20.71666667,  19.98333333,  27.41111111,3.71111111,  15.46111111],
                   [ 16.47777778,  21.33333333,  20.54444444,  27.87777778,3.92222222,  15.95      ],
                   [ 17.42222222,  21.97222222,  21.11666667,  28.30555556,4.16666667,  16.36111111],
                   [ 18.36666667,  22.56111111,  21.71111111,  28.74444444,4.42777778,  16.8       ],
                   [ 19.45555556,  23.15      ,  22.28888889,  29.27777778,4.62777778,  17.30555556],
                   [ 20.51666667,  23.72777778,  22.83888889,  29.83333333,4.85      ,  17.73333333],
                   [ 21.58333333,  24.34444444,  23.39444444,  30.4       ,5.06666667,  18.18333333],
                   [ 22.64444444,  25.00555556,  24.05555556,  30.93888889,5.42777778,  18.67777778],
                   [ 23.66666667,  25.73888889,  24.63333333,  31.55555556,5.62222222,  19.2       ],
                   [ 24.87777778,  26.52222222,  25.38888889,  32.23333333,5.89444444,  19.76666667],
                   [ 26.31111111,  27.41111111,  26.18333333,  32.83333333,6.32777778,  20.47222222],
                   [ 27.8       ,  28.51111111,  27.16111111,  33.61111111,6.67222222,  21.28888889],
                   [ 29.60555556,  29.91111111,  28.43333333,  34.37777778,7.04444444,  22.40555556],
                   [ 32.08888889,  32.08333333,  30.38333333,  35.33333333,7.58888889,  24.06666667],
                   [ 39.47777778,  41.55555556,  38.52222222,  38.3       ,11.66666667,  31.67777778]])

plt.close("all")
fig,axes = plt.subplots(2,2)
accuracy = 0.05
reliabilities = 1-np.arange(0,1+0.01,accuracy)
sensitivities = enumerate([-0.5,0,0.5,1.5,3])

#parameter = "test"
#plt.suptitle(r"$\bf Sensitivity \: Analysis \: of \: Test \: Frequency$"+"\nExpected Net Revenues "+"\nSimulation Time 720h, test = 1/month, Penalty = 4320€/missing MW")

parameter = "penalty"
plt.suptitle(r"$\bf Sensitivity \: Analysis \: of \: Test \: Penalty$"+"\nExpected Net Revenues "+"\nSimulation Time 720h, test = 1/month, Penalty = 4320€/missing MW")

#compute
for n,sensitivity in sensitivities:
    print("sensitivity "+str(sensitivity))
    
    if parameter == "test":
        legend = sensitivity*100
        tests = 12/12*(1+sensitivity) #tests/month
        factor = 1 #€/MWh
    if parameter == "penalty":
        legend = sensitivity*100
        tests = 12/12 #tests/month
        factor = 1*(1+sensitivity) #€/MWh
        
    #CONSTANTS#
    bidCapacity = 6 #€/MW/h
    bidEnergy = 120 #€/MWh
    activations = 4/12 #activations/month
    durationCapacity = 720 #hours/week
    durationMonth = 720 #hours/month
    durationActivation = 0.5 #hour
    tariff = 120 #€/MWh
    
    #VOLUMES&RELIABILITY#
    volumeCapacity = np.zeros(volumes.shape)
    volumeMissing = np.zeros(volumes.shape)
    
    for k,reliability in enumerate(reliabilities):
        volumeCapacity[k] = volumes[k,:]
        volumeMissing[k] = volumes[k,:]-volumes[0,:]
           
    volumeActivation = volumeCapacity
    
    #FORMULAS#
    penaltyMonitoring = volumeMissing*factor*bidCapacity*durationMonth
    penaltyActivation = volumeMissing*tariff*durationActivation

    revenuesCapacity =  volumeCapacity*bidCapacity*durationCapacity
    revenuesEnergy =    activations*volumeActivation*bidEnergy*durationActivation
    costsMonitoring =   np.matmul(np.diag(1-reliabilities),tests*penaltyMonitoring)
    costsActivation =   np.matmul(np.diag(1-reliabilities),activations*penaltyActivation)
    
    revenuesTotal = revenuesCapacity + revenuesEnergy
    costsTotal = costsMonitoring + costsActivation
    revenuesNet = revenuesTotal - costsTotal
    
        
    #%% ILLUSTRATE
    col = ["C0",'C1','C2','C3','C4','C5','C6']

    #initialize
    for k,source in enumerate(["solar","wind","agg","demand"]):
        axes[int(k/2),k%2].plot(reliabilities*100, revenuesNet[:,k]/10**3,label = "Sensitivity "+str(legend)+"%",color =col[n],linewidth=2,)
        #axes[int(k/2),k%2].plot(reliabilities*100, revenuesTotal[:,k]/10**3,linestyle ="--",linewidth=0.5)
        #axes[int(k/2),k%2].plot(reliabilities*100, costsTotal[:,k]/10**3,linestyle = "--",linewidth=0.5)

        ##RECOMMENDATION ------------------
        x = reliabilities[np.argmax(revenuesNet[:,k])]*100
        y = np.amax(revenuesNet[:,k])/10**3
        axes[int(k/2),k%2].plot([x], [y], 'o',color =col[n])
        
        axes[int(k/2),k%2].set_xlabel("Reliability [%]")
        axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
        axes[int(k/2),k%2].legend()
        axes[int(k/2),k%2].set_ylim(0)
        axes[int(k/2),k%2].set_xlim(60,100)
        axes[int(k/2),k%2].set_title(titles[k])
