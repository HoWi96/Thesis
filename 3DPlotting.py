# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:42:02 2019

@author: user
"""
#SOURCE: https://medium.com/@sebastiannorena/3d-plotting-in-python-b0dc1c2e5e38
#TUTORIAL: https://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

plt.close("all")

###################
#######ORDERED DATA
###################

#3D Lines
zline = np.linspace(0,15,1000)
xline = np.cos(zline)
yline = np.sin(zline)
fig = plt.figure()
ax = plt.axes(projection="3d")
ax.plot3D(xline,yline,zline,'gray')

#3D Points
zdata = 15 * np.random.random(100)
xdata = np.cos(zdata) + 0.1 * np.random.randn(100)
ydata = np.sin(zdata) + 0.1 * np.random.randn(100)
ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap="Greens");
ax.set_title("3D lines and points")

#3D Contour Plot
def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

x = np.linspace(-6, 6, 30)
y = np.linspace(-6, 6, 30)

X,Y = np.meshgrid(x,y)
Z = f(X,Y)

fig = plt.figure()
ax = plt.axes(projection="3d")
ax.contour3D(X,Y,Z,50,cmap = 'coolwarm')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_title('Contour Plot')

#3D Wireframes
fig = plt.figure()
ax = plt.axes(projection = '3d')
ax.plot_wireframe(X,Y,Z,color = 'red')
ax.set_title('Wireframes')

#3D Surface Plot
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,cmap='coolwarm',edgecolor='none')
ax.set_title('Surface Plot')

"""
Color Maps cmap = https://matplotlib.org/examples/color/colormaps_reference.html
"""

##################
####UNORDERED DATA
##################
theta = 2*np.pi*np.random.random(1000)
r = 6*np.random.random(1000)
x = np.ravel(r*np.cos(theta))
y = np.ravel(r*np.sin(theta))
z = f(x,y)
fig = plt.figure()
ax = plt.axes(projection = '3d')
ax.plot_trisurf(x,y,z,cmap = 'viridis',edgecolor = 'none')
ax.set_title('Surface Triangulation')

















