# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 12:28:57 2018

@author: user
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.special



#Import DATA
data = pd.read_csv("AggregateNovember.csv") #https://chrisalbon.com/python/data_wrangling/pandas_dataframe_importing_csv/
print(data.head()) # Print the first 5 values
data.describe() # Describe most important parameters of data
x = np.linspace(0, 6000)

#Plot DATA
data.plot()
plt.xlabel('Time [15\']')
plt.ylabel('Power [MW]')
plt.show()


#Calculate Gamma
mean, var = data.mean(), data.var()
α, β = mean ** 2 / var, var / mean
#Fit Gamma
args = stats.gamma.fit(data)

"""
argsGamma = stats.gamma.fit(data)
GammaDistribution = stats.gamma.pdf(x, *argsGamma)
kdeDistribution = stats.kde.gaussian_kde(data.values.ravel())
argsNorm = stats.norm.fit(data)
Normal Distribution = stats.norm.pdf(x, loc=loc_param, scale=scale_param)
"""

"""
PDF
"""
fig,ax = plt.subplots()
#Plot Gamma
plot1a = plt.plot(x, stats.gamma.pdf(x, α, 0, β))
plot1b = plt.plot(x, stats.gamma.pdf(x, *args)) #* unpacks list/tuple; ** unpacks dictionary

#Plot Histogram
plot2 = data.plot(kind='hist',bins = 200, density=True, color='lightblue',ax = ax)
#data.plot(kind='hist', , bins=500, density=True, color='lightblue')

#Plot Kernel Density Estimation
#plot3 = data.dropna().plot(kind='kde', style='r--', ax = ax)
plot3 = data.plot(kind='kde', style='r--', ax = ax)


# non-parametric pdf
nparam_density = stats.kde.gaussian_kde(data.values.ravel())
#x = np.linspace(0, 200, 6000)
nparam_density = nparam_density(x)
plot4 = plt.plot(x,nparam_density,'k--')

# parametric fit: assume normal distribution
argsNorm = stats.norm.fit(data)
param_density = stats.norm.pdf(x, *argsNorm)
plot5 = plt.plot(x,param_density,'g--')
fig.suptitle('Probability Density Function')
plt.xlabel('Power [MW]')
plt.show()

"""
CDF
"""
fig1,ax1 = plt.subplots()
data.plot(cumulative = 'True', kind='hist', bins=500, density=True, color='lightblue',ax = ax1)
#data.dropna().plot(cumulative = 'True', kind='kde', style='r--', ax = ax1)
#data.plot(Cumulative = 'True', kind='gamma', style='r--', ax = ax1)
fig1.suptitle('Cumulative Distribution Function')
plt.xlabel('Power [MW]')
plt.show()

"""
Quantile Function aka percent-point function aka inverse CDF
"""
fig, ax = plt.subplots(1, 1)
quantile = np.linspace(0,1)
plt.plot(quantile,data.quantile(quantile))
# This is nothing less than a normalized LDC!
fig.suptitle('Quantile Function')
plt.xlabel('Risk [-]')
plt.ylabel('Power [MW]')
plt.show()

"""
Binomial distribution
"""
fig, ax = plt.subplots(1, 1)
n,p = 2, 0.8
print(stats.binom.pmf(0,2,0.8)) #risico 0 geslaagde activaties
print(stats.binom.cdf(2,2,0.8)) #risico op 1 of minder geslaagde activaties

print(stats.binom.ppf(0.01, 4, 0.8)) #aantal geslaagde activaties nodig inverse CDF
stats.binom(n,p)
mean, var, skew, kurt = stats.binom.stats(n, p, moments='mvsk')
#x = np.arange(stats.binom.ppf(0.01, n, p),stats.binom.ppf(0.99, n, p))
x = np.arange(0,3)
ax.plot(x, stats.binom.pmf(x, n, p), 'bo', ms=8, label='binom pmf')
ax.vlines(x, 0, stats.binom.pmf(x, n, p), colors='b', lw=5, alpha=0.5)
fig.suptitle('Binomial PMF')
plt.xlabel('Number Succesful Activations')
plt.ylabel('Probability [-]')
plt.show()


"""
Poisson distribution
"""
fig, ax = plt.subplots(1, 1)
year = 365 #15 minutes
mu = 2/year
print(stats.poisson.cdf(0, mu))
print(stats.poisson.cdf(1, mu))
print(stats.poisson.cdf(2, mu))
print(stats.poisson.cdf(3, mu))

mean, var, skew, kurt = stats.poisson.stats(mu, moments='mvsk')
#x = np.arange(stats.poisson.ppf(0, mu), stats.poisson.ppf(0.99, mu))
x = np.arange(0, 10)
ax.plot(x, stats.poisson.pmf(x, mu), 'bo', ms=8, label='poisson pmf')
ax.vlines(x, 0, stats.poisson.pmf(x, mu), colors='b', lw=5, alpha=0.5)
fig.suptitle('Poisson PMF')
plt.xlabel('Number Activations')
plt.ylabel('Probability [-]')
plt.show()

"""
Estimate value
"""
risk = np.linspace(0,1)
volume = data.quantile(risk).iloc[:,0].values #MW
allowance = 102.3/55 #EUR/MW
deploymentPrice = 20 #EUR/MW
activation_duration = 1 # 1u
EPEX = 69 #EUR/MW

#Revenues, assume no reported non-availability
capacityPayment = 365*24*volume*allowance
activationPayment = -activation_duration*volume*min([EPEX-250, 0, deploymentPrice-100])
sanctionPayment = activation_duration*volume*allowance*120
#revenues for 1 actiation
revenues1 = capacityPayment + (1-risk)*activationPayment - risk*sanctionPayment
#revenues for 2 activations (r1+r2)**2
a = np.multiply((1-risk),(1-risk)) + 2*np.multiply((1-risk),risk)
b = np.multiply(risk,risk) + 2*np.multiply((1-risk),risk)
revenues2 = capacityPayment + a*activationPayment - b*sanctionPayment

plt.plot(risk,revenues1)
plt.plot(risk,revenues2) 
#biggest income factor is capacityPayment, hence similar to quantile function...
#To Change: 
#1) Value estimates 
#2) Incorporate period out (e.g. after 3 times: 20%^3*0)
#3) Incorporate non-availability...

StopN = 3
revenues3 = (risk**StopN)*0+(1-risk**StopN)*revenues2
plt.plot(risk,revenues3) 
plt.xlabel('Risk [-]')
plt.ylabel('Revenues [EUR]')
plt.title('Expected Revenues')
plt.show()

#For different possible activations
for n in range(0,100+1,10):
    activationRevenues = 0
    for k in range(0,n+1):
        activationRevenues += scipy.special.binom(n,k)*np.power(risk,n-k)*np.power(1-risk,k)*((n-k)*-sanctionPayment+k*activationPayment)
    plt.plot(risk,capacityPayment + activationRevenues)
    #plt.legend("activations: "+n)
plt.xlabel('Risk [-]')
plt.ylabel('Revenues [EUR]')
plt.title('Expected Revenues')
plt.show()

#Share value amongst wind and sun. Proposed: fair division of total gains (1-risk)*volume?


 





