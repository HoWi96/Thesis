# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:49:15 2018

@author: Holger
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import scipy.stats as stats
import scipy.special

data = pd.read_csv("DataJune2017.csv")
description = data.describe()
#stdSun2018 = description["SUN2018"]["std"]

#SCALE DATA
#----------
SunMonitored = 2952.78
WindMonitored = 2424.07
SunInstalled = 30
WindInstalled = 100

data["WIND2017"] = data["WIND2017"]*WindInstalled/WindMonitored
data["SUN2017"] = data["SUN2017"]*SunInstalled/SunMonitored 
data["AGG2017"] = data["WIND2017"]+data["SUN2017"]

"""
Plot scaled data
"""
data.plot()
plt.legend(bbox_to_anchor=(1, 1))
plt.xlabel('Time [15\']')
plt.ylabel('Power [MW]')
plt.show()

"""
Quantile Function aka percent-point function aka inverse CDF
Link percentile and volume
"""
fig, ax = plt.subplots(1, 1)
quantile = np.linspace(0,1)
quantilePlot = plt.plot(quantile,data.quantile(quantile))
quantilePlot = plt.plot(quantile,data["WIND2017"].quantile(quantile)+data["SUN2017"].quantile(quantile))
plt.legend(quantilePlot, list(data),bbox_to_anchor=(1, 1))
#plt.plot(quantile, data["SUN2017"].quantile(quantile)+data["WIND2017"].quantile(quantile), label="SUM2017")
# This is nothing less than a normalized LDC!
fig.suptitle('Quantile Function')
plt.xlabel('Percentile [-]')
plt.ylabel('Power [MW]')
plt.show()

"""
Estimate value
"""
percentile = np.linspace(0,1)
volume = data["AGG2017"].quantile(percentile).values #MW

#Assumption
activation_duration = 1 # 1h
averagePrice = 6 #EUR/MW/h
EPEX = 70 #EUR/MW
deploymentPrice = 20 #EUR/MW/h

#Revenues, assume no reported non-availability
capacityPayment = 365/12*24*volume*averagePrice
activationPayment = -activation_duration*volume*min([EPEX-250, 0, deploymentPrice-100])
sanction = -activation_duration*volume*120*averagePrice

#Plot Revenues for 1 activations VS power available
revenues1 = percentile**2*2*sanction+capacityPayment+(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*(sanction+activationPayment)  
volume = data["AGG2017"].quantile(percentile).values
fig, ax1 = plt.subplots()
ax1.plot(percentile,revenues1,'b')
ax2 = ax1.twinx()
ax2.plot(percentile,volume,'r.')
fig.suptitle('Revenues vs Contracted Volume')
ax1.set_xlabel('Percentile [-]')
ax1.set_ylabel('Expected Revenues [EUR/month]', color='b')
ax2.set_ylabel('Power [MW]', color='r')
plt.show()

#Plot Revenues for 2 activation VS components
fig, ax1 = plt.subplots()
ax1.plot(percentile,revenues1,label = "Expected Revenues")
ax1.plot(percentile,capacityPayment,label = "Capacity Payment")
ax1.plot(percentile,percentile**2*2*sanction+(1-percentile)*percentile*2*sanction,label = "Expected Sanction")
ax1.plot(percentile,(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*activationPayment,label = "Expected Activation Payment")
plt.legend(bbox_to_anchor=(1, 1))
plt.xlabel('Percentile [-]')
plt.ylabel('Expected Revenues [EUR/month]')
plt.title('Revenues components')
plt.show()

#EXCLUSION FROM PARTICIPATION AFTER X TIMES
revenues1 = percentile**2*2*sanction+capacityPayment+(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*(sanction+activationPayment)  
revenues2 = percentile**2*0+(1-percentile**2)*capacityPayment+(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*(sanction+activationPayment)
plt.plot(percentile,revenues2, label = "Reference")
plt.plot(percentile,revenues1, label = "Exclusion")  
plt.legend(bbox_to_anchor=(1, 1))
plt.xlabel('Percentile [-]')
plt.ylabel('Expected Revenues [EUR/month]')
plt.title('Expected Reveneus')
plt.show()

#DIFFERENT ACTIVATION AMOUNTS
for n in range(0,12+1,2):
    activationRevenues = 0
    for k in range(0,n+1):
        activationRevenues += scipy.special.binom(n,k)*np.power(percentile,n-k)*np.power(1-percentile,k)*((n-k)*sanction+k*activationPayment)
    plt.plot(percentile,capacityPayment + activationRevenues,label = n)
    plt.legend(bbox_to_anchor=(1, 1), title = "Amount Activations")

    #plt.legend("activations: "+n)
plt.xlabel('Percentile [-]')
plt.ylabel('Expected Revenues [EUR/month]')
plt.title('Expected Revenues')
plt.show()

"""
Recommendation
"""
volume100=130.
volume20=data["AGG2017"].quantile(0.20)
volume1=data["AGG2017"].quantile(0.01)
volume = np.array([volume100,volume20,volume1])

percentile = np.array([1.,0.2,0.01])

capacityPayment = 365*24*volume*averagePrice/12
activationPayment = -activation_duration*volume*min([EPEX-250, 0, deploymentPrice-100])
sanctionPayment = -activation_duration*volume*averagePrice*120

revenues = percentile**2*2*sanctionPayment+capacityPayment+(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*(sanctionPayment+activationPayment)  
print("Percentile: ", percentile)
print("volumes: ",volume)
print("revenues: ",revenues)
print()

"""
Value Distribution
"""

volume = np.array([30,data["SUN2017"].quantile(0.20),data["SUN2017"].quantile(0.01),100,data["WIND2017"].quantile(0.20),data["WIND2017"].quantile(0.01)])
percentile = np.array([1.,0.2,0.01,1.,0.2,0.01])

capacityPayment = 365*24*volume*averagePrice/12
activationPayment = -activation_duration*volume*min([EPEX-250, 0, deploymentPrice-100])
sanctionPayment = -activation_duration*volume*averagePrice*120

revenues = percentile**2*2*sanctionPayment+capacityPayment+(1-percentile)**2*2*activationPayment+(1-percentile)*percentile*2*(sanctionPayment+activationPayment)  
print("Percentile: ", percentile)
print("volumes: ",volume)
print("revenues: ",revenues)


#Quantile
volumeQuantile = data[["SUN2017", "WIND2017","AGG2017"]].quantile(0.20)
volumeInstalled = [30,100,130]
volumeMonthly = data[["SUN2017", "WIND2017","AGG2017"]].mean()
volumeActivation = data["SUN2017"]/(data["SUN2017"]+data["WIND2017"])