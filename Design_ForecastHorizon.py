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
from scipy.stats import norm

# In[] UPLOAD DATA

solarData = pd.read_csv("Data/SolarForecastJune2017.csv")
windData = pd.read_csv("Data/WindForecastJune2017.csv")
demandData = pd.read_csv("Data/LoadForecastJune2017.csv")
data2016 = pd.read_csv("Data/data2016.csv")

WINDPEAK = 2403.17
SOLARPEAK = 2952.78
DEMANDPEAK = 11742.29

WIND_INST = 2424.07
SOLAR_INST = 2952.78
DEMAND_INST = 11742.29

WIND_INST2016 = 1960.91
SOLAR_INST2016 = 2952.78
DEMAND_INST2016 = 11589.6

# In[] PROCESS DATA

#Errors wind data
wdata5 =    windData["RealTime"]-windData["5h-ahead"]
wdata24 =   windData["RealTime"]-windData["24h-ahead"]
wdata168 =  windData["RealTime"]-windData["168h-ahead"]
wdata8760 = windData["RealTime"]-data2016["wind"]*WIND_INST/WIND_INST2016
wdata = pd.DataFrame(data={4:wdata5, 24:wdata24,168:wdata168,8760:wdata8760})/WIND_INST*100

#Errors solar data
sdata3 =    solarData["RealTime"]-solarData["3h-ahead"]
sdata24 =   solarData["RealTime"]-solarData["24h-ahead"]
sdata168 =  solarData["RealTime"]-solarData["168h-ahead"]
sdata8760 = solarData["RealTime"]-data2016["solar"]*SOLAR_INST/SOLAR_INST2016
sdata = pd.DataFrame(data={4:sdata3, 24:sdata24, 168:sdata168, 8760:sdata8760})/SOLAR_INST*100

#Errors demand data
ddata3 =    demandData["RealTime"]-demandData["3h-ahead"]
ddata24 =   demandData["RealTime"]-demandData["24h-ahead"]
ddata168 =  demandData["RealTime"]-demandData["168h-ahead"]
ddata8760 = demandData["RealTime"]-data2016["load"]*DEMAND_INST/DEMAND_INST2016
ddata = pd.DataFrame(data={4:ddata3, 24:ddata24, 168:ddata168, 8760:ddata8760})/DEMAND_INST*100

#Errors aggregator data
aggdata = (30*sdata + 100*wdata)/100

#%% DENSITY PLOTS
plt.close("all")
titles = ["Forecast Error Wind","Forecast Error Solar","Forecast Error Demand"]

fig, axes = plt.subplots(1,3)
wdata.plot.density(ax = axes[0])
sdata.plot.density(ax = axes[1])
ddata.plot.density(ax = axes[2])
for i in (0,1,2):
    axes[i].set_title(titles[i])
    axes[i].set_xlabel("$\Delta$P [%MW]")
    axes[i].set_xlim(-50,50)
    

#%% QUANTILE PLOTS
fig,axes = plt.subplots(1,3)
x = np.linspace(0,1,100)
axes[0].plot(x*100,wdata.quantile(x)+100)
axes[1].plot(x*100,sdata.quantile(x)+100)
axes[2].plot(x*100,ddata.quantile(x)+100)

for i in (0,1,2):
    axes[i].set_ylabel("$\Delta$P [%MW]")
    axes[i].set_xlabel("Uncertainty [%]")
    axes[i].set_title(titles[i])
    axes[i].legend((4,24,168,8760))

#%% VOLUME IMPACT PLOTS
windSd = np.sqrt(np.diag(np.cov(wdata,rowvar=False)))
solarSd = np.sqrt(np.diag(np.cov(sdata,rowvar=False)))
demandSd = np.sqrt(np.diag(np.cov(ddata,rowvar=False)))
aggregatorSd = np.sqrt(np.diag(np.cov(aggdata,rowvar=False)))
print(windSd)
print(solarSd)
print(demandSd)
print(aggregatorSd)

horizons = ("4","24","168","8760")
quantileSd = norm.cdf(-1)

fig,axes = plt.subplots(1,3)
axes[0].plot(horizons,windSd,label="$\sigma_{error}$")
axes[0].plot(horizons,np.abs(wdata.quantile(quantileSd)),label="$\sigma_{quantile}$")

axes[1].plot(horizons,solarSd,label="$\sigma_{error}$")
axes[1].plot(horizons,np.abs(sdata.quantile(quantileSd)),label="$\sigma_{quantile}$")

axes[2].plot(horizons,demandSd,label="$\sigma_{error}$")
axes[2].plot(horizons,np.abs(ddata.quantile(quantileSd)),label="$\sigma_{quantile}$")

for i in (0,1,2):
    axes[i].set_ylabel("$\sigma_{error}$ [%]")
    axes[i].set_xlabel("time horizon [h]")
    axes[i].set_title(titles[i])
    axes[i].legend()
    
#%% WIND PLOTS

fig,axes = plt.subplots(1,2)
fig.suptitle("Downward Reserves 100MWp Wind")
             
#aggdata.plot.density(ax = axes[0])
#axes[0].set_xlabel("$\Delta$P [MW]")
#axes[0].set_title("Error Density Plot")
#axes[0].set_xlim(-50,50)

axes[1].plot(100-x*100,wdata.quantile(x))
axes[1].set_title("Error Quantile Plot")
axes[1].set_xlabel("Reliability [%]")
axes[1].set_ylabel("$\Delta$P [MW]")
axes[1].legend(('4h','24h','168h','8760h'))

RELIABILITY = .90
#axes[0].plot(horizons,aggregatorSd,label="$\sigma_{error}$")
axes[0].plot(horizons,np.abs(wdata.quantile(1-RELIABILITY)),label="Reliability "+str(RELIABILITY*100)+"%")
axes[0].set_ylabel("Lost Volume [MW]")
axes[0].set_xlabel("Forecast Horizon [h]")
axes[0].set_title("Lost Volume By Forecast Horizon")
axes[0].legend()

#%% AGGREGATOR PLOTS

fig,axes = plt.subplots(1,2)
fig.suptitle("Aggregator 130MWp")
             
#aggdata.plot.density(ax = axes[0])
#axes[0].set_xlabel("$\Delta$P [MW]")
#axes[0].set_title("Error Density Plot")
#axes[0].set_xlim(-50,50)

axes[1].plot(x*100,aggdata.quantile(x))
axes[1].set_title("Error Quantile Plot")
axes[1].set_xlabel("Uncertainty [%]")
axes[1].set_ylabel("$\Delta$P [MW]")
axes[1].legend((4,24,168,8760))

UNCERTAINTY = 30
#axes[0].plot(horizons,aggregatorSd,label="$\sigma_{error}$")
axes[0].plot(horizons,np.abs(aggdata.quantile(UNCERTAINTY/100)))
axes[0].set_ylabel("Lost Volume [MW]")
axes[0].set_xlabel("Time Horizon [h]")
axes[0].set_title("Lost Volume By Time Horizon\nUncertainty= "+str(UNCERTAINTY)+"%")
    
#%% DESCRIPTIVE STATISTICS

#Mean error (should be 0)
np.mean(wdata) #24 -0.96%
np.mean(sdata) #24 +0.09%
np.mean(ddata) #24 +0.12%
np.mean(aggdata) #24 -0.71%
    
#correlation between errors in time --> reuse models
np.corrcoef(wdata,rowvar=False) #5 ~24 & 168 ~ 8760
np.corrcoef(sdata,rowvar=False) #3~24 & 168 ~8760
np.corrcoef(ddata,rowvar=False) #24~168
