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
import scipy.special
from mpl_toolkits import mplot3d

# In[] Upload Data

solarData = pd.read_csv("Data/SolarForecastJune2017.csv")
windData = pd.read_csv("Data/WindForecastJune2017.csv")
WINDINSTALLED = 2403.17
SOLARINSTALLEDD = 2952.78    

