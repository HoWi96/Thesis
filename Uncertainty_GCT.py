# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:45:52 2019
@title: Assess Uncertainty on forecast vs uncertainty on time
@author: HoWi96
"""

# In[] IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

# In[] UPLOAD DATA

solarData = pd.read_csv("Data/SolarForecastJune2017.csv")
windData = pd.read_csv("Data/WindForecastJune2017.csv")
demandData = pd.read_csv("Data/LoadForecastJune2017.csv")
WINDPEAK = 2403.17
SOLARPEAK = 2952.78
DEMANDPEAK = 11742.29

# In[] PROCESS DATA

#Errors wind data
wdata5h = (windData["5h-ahead"]-windData["RealTime"])/WINDPEAK*100
wdata24h = (windData["24h-ahead"]-windData["RealTime"])/WINDPEAK*100
wdata168h = (windData["168h-ahead"]-windData["RealTime"])/WINDPEAK*100

#Errors solar data
sdata3h = (solarData["3h-ahead"]-solarData["RealTime"])/SOLARPEAK*100
sdata24h = (solarData["24h-ahead"]-solarData["RealTime"])/SOLARPEAK*100
sdata168h = (solarData["168h-ahead"]-solarData["RealTime"])/SOLARPEAK*100

#Errors demand data
ddata3h = (demandData["3h-ahead"]-demandData["RealTime"])/DEMANDPEAK*100
ddata24h = (demandData["24h-ahead"]-demandData["RealTime"])/DEMANDPEAK*100
ddata168h = (demandData["168h-ahead"]-demandData["RealTime"])/DEMANDPEAK*100

# In[] PLOTS

# HISTOGRAMS Wind, Solar, Demand
plt.close("all")
fig, axes = plt.subplots(3, 3)
axes[0,0].hist(wdata5h, bins = 20)
axes[0,1].hist(wdata24h, bins = 20)
axes[0,2].hist(wdata168h, bins = 20)
axes[1,0].hist(sdata3h, bins = 20)
axes[1,1].hist(sdata24h, bins = 20)
axes[1,2].hist(sdata168h,bins = 20)
axes[2,0].hist(ddata3h, bins = 20)
axes[2,1].hist(ddata24h, bins = 20)
axes[2,2].hist(ddata168h, bins = 20)

titles = ["Forecast Error Wind GCT 5h", "Forecast Error Wind GCT 24h", "Forecast Error Wind GCT 168h", 
          "Forecast Error Solar GCT 3h", "Forecast Error Solar GCT 24h", "Forecast Error Solar GCT 168h",
          "Forecast Error Demand GCT 3h", "Forecast Error Demand GCT 24h", "Forecast Error Demand GCT 168h"]

for i,j in ([0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]):
    axes[i,j].set_title(titles[i+j])
    axes[i,j].set_xlim = (-40,40)
    
# QUANTILE PLOTS Wind, Solar, Demand
fig,axes = plt.subplots(3,3)
x = np.linspace(0,1,50)
axes[0,0].plot(x,wdata5h.quantile(x)+100)
axes[0,1].plot(x,wdata24h.quantile(x)+100)
axes[0,2].plot(x,wdata168h.quantile(x)+100)
axes[1,0].plot(x,sdata3h.quantile(x)+100)
axes[1,1].plot(x,sdata24h.quantile(x)+100)
axes[1,2].plot(x,sdata168h.quantile(x)+100)
axes[2,0].plot(x,ddata3h.quantile(x)+100)
axes[2,1].plot(x,ddata24h.quantile(x)+100)
axes[2,2].plot(x,ddata168h.quantile(x)+100)

for i,j in ([0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]):
    axes[i,j].set_ylabel("$\Delta$P [%MW]")
    axes[i,j].set_xlabel("Uncertainty [%]")
    axes[i,j].set_title(titles[i+j])

#SCATTER PLOTS
#plot wind vs solar
fig,axes = plt.subplots(3)
axes[0].plot(sdata24h,wdata24h,'o',color="black")
axes[0].set_xlabel("Solar Data Overestimation 24h [%]")
axes[0].set_ylabel("Wind Data Overestimation 24h [%]")
#plot demand vs solar
axes[1].plot(sdata24h,ddata24h,'o',color="black")
axes[1].set_xlabel("Solar Data Overestimation 24h [%]")
axes[1].set_ylabel("Demand Data Overestimation 24h [%]")
#plot demand vs wind
axes[2].plot(wdata24h,ddata24h,'o',color="black")
axes[2].set_xlabel("Wind Data Overestimation 24h [%]")
axes[2].set_ylabel("Demand Data Overestimation 24h [%]")
fig.suptitle("Simultaneous Error 24h")

# In[] DESCRIPTIVE STATISTICS
dataError24h = np.vstack((wdata24h,sdata24h,ddata24h))
print("\n MEAN \n % overestimation wind + % overestimation solar + % overestimation demand \n", np.mean(dataError24h,1))
print("\n COVARIANCE MATRIX \n |wind          |solar          |demand  \n", np.cov(dataError24h))
print("\n CORRELATION MATRIX \n |wind         |solar          |demand  \n", np.corrcoef(dataError24h))
