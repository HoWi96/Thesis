# -*- coding: utf-8 -*-
"""
Created on Sun May 26 23:34:08 2019

@author: user
"""
import numpy as np
import matplotlib.pyplot as plt

TENNET = 0
#%%#####################################################################
# FINANCIALS
########################################################################

#%% PROCESS
print("Process Financials")

#initialize
titles = ["(a) Solar PV 100MWp Down","(b) Wind 100MWp Down","(c) Aggregator 100MWp Down","(d) Demand 100MWp Up (SL = 50MW)"]
step = 0.05
reliability = 1-np.arange(0,1+step/2,step)

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

fig,axes = plt.subplots(2,2)

TESTS_ARRAY = [0,1,2,3]
plt.suptitle("Net Revenues - Amount Availibility Tests\nReference = 1")
#
#ALLOWED_FAILS_ARRAY = [0,1,2,3,5,10]
#plt.suptitle("Net Revenues - Allowed Fails")
#
#ACTIVATION_PENALTY_ARRAY = [10,40,70,100,130,160,200]
#plt.suptitle("Net Revenues - Activation Penalty \n reference = 10")

#ACTIVATION_DURATION_ARRAY = [1,2,4,8,16]
#plt.suptitle("Net Revenues - Activation Duration\nReference = 4")

#RATIO_MISSING_ARRAY = [1,1.3,1.6,1.9,2.2,2.5]
#plt.suptitle("Net Revenues - Ratio Missing Volumes\nReference = 1.3")

#compute
for n,TESTS in enumerate(TESTS_ARRAY):
    legend = TESTS
    #PARAMETERS#############################
    #Bids
    CAPACITY_REMUNERATION = 6 #EUR/MW/h
    ACTIVATION_REMUNERATION = 70 #EUR/MWh/activation
    
    #Market Parameters
    ACTIVATIONS = 2/12 #activations/M
    #TESTS = 12/12
    ACTIVATION_DURATION = 4#h
    CAPACITY_DURATION = 720#h
    RATIO_MISSING = 1.30#
    #ALLOWED_FAILS = 3
    
    #External Determined
    ACTIVATION_PENALTY = 100 #EUR/MWh/activation

    #############################
    #Remuneration
    capacityRemuneration = CAPACITY_DURATION*CAPACITY_REMUNERATION*volumes
    activationRemuneration = ACTIVATION_DURATION*ACTIVATION_REMUNERATION*volumes
    testPenalty = CAPACITY_DURATION*CAPACITY_REMUNERATION*RATIO_MISSING*(volumes-volumes[0,:])
    activationPenalty = ACTIVATION_DURATION*ACTIVATION_PENALTY*(volumes-volumes[0,:])

    #Revenues Components
    capacityRevenues = capacityRemuneration
    activationRevenues = ACTIVATIONS*activationRemuneration
    activationCosts = np.matmul(np.diag(1-reliability),ACTIVATIONS*activationPenalty)
    testCosts = np.matmul(np.diag(1-reliability),TESTS*testPenalty)
    
    #Net Revenues
    revenues = capacityRevenues + activationRevenues
    costs = activationCosts  + testCosts
    netRevenues = revenues - costs
    
        
    #%% ILLUSTRATE
    print("Illustrate Financials")

    #initialize
    for k,source in enumerate(["solar","wind","agg","demand"]):
        axes[int(k/2),k%2].plot(reliability*100, netRevenues[:,k]/10**3,linewidth=2.5,label = str(legend))
        axes[int(k/2),k%2].plot(reliability*100, capacityRevenues[:,k]/10**3,label = "capacity revenues")
        axes[int(k/2),k%2].plot(reliability*100, activationRevenues[:,k]/10**3,label = "activation revenues")
        axes[int(k/2),k%2].plot(reliability*100, activationCosts[:,k]/10**3, linestyle = "-",linewidth=1,label ="activation cost")
        axes[int(k/2),k%2].plot(reliability*100, testCosts[:,k]/10**3, linestyle = "-",linewidth=1,label ="testcost")        

        axes[int(k/2),k%2].set_xlabel("Reliability [%]")
        axes[int(k/2),k%2].set_ylabel("Revenues [k€/Month]")
        axes[int(k/2),k%2].legend()
        axes[int(k/2),k%2].set_ylim(0)
        axes[int(k/2),k%2].set_title(titles[k])
        
    
        ##RECOMMENDATION ------------------
        x = reliability[np.argmax(netRevenues[:,k])]*100
        y = np.amax(netRevenues[:,k])/10**3
        
        col = ["C0",'C1','C2','C3','C4','C5','C6','C7']
        axes[int(k/2),k%2].plot([x], [y], 'o',color =col[n])
