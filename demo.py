# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:42:42 2020

@author: jmbelda
"""

from FuzzyTree import *
import pandas as pd

#%% Reading the data
data = pd.read_csv("./demo/airquality.csv", index_col=0)

#%% Vars in the file
variables = list(data.keys())


#%% Names of the vars
# LHS stands for Left Hand Side: Predictors
# RHS stands for Right Hand Side: Predicted

varRHS = variables[1:5]
varLHS = variables[0]
#varRHS.append(variables[0])

#%% Fuzzification

fnVars = {}  # Dictionary of fuzzification functions
fvVars = {}  # Dictionary of fuzzified variables

levels = ["1. Low", "2. Medium", "3. High"]

for v in  variables:
    fnVars[v], fvVars[v] = percentile_partition(data[v], v, levels)
    
    
#%% Drawing the variables
    
from numpy import linspace
from matplotlib.pyplot import *


fig = figure()
fig.tight_layout()




for c, v in enumerate(variables):
    subplot(3,2,c+1)
    
    # Creating an array for the extremes of the variable
    mini = min(data[v])
    maxi = max(data[v])    
    vals = linspace(mini, maxi, 500)
    
    # Fuzzyfiyng the array
    fuzzified = fnVars[v](vals)
        
    for l in levels:
        plot(vals, fuzzified[l], label=l)
        
    legend()
    title(v)

#%% Creating a fuzzy set
fs = FuzzySet(*fvVars.values())

#%% Building the FuzzyTree
Beta = 0.8
Alpha = 0.8
ft = FuzzyTree(fs, Beta, Alpha, varRHS, varLHS)
print(ft)

#%% Confussion matrix
ft.confussion_matrix(fvVars[varLHS], fs)

#%% Save a graphviz file for graphic output
ft.output_to_dot_graphviz('./draw_the_tree.dot')

#%% Showing the fuzzification (matplotlib)
show()

