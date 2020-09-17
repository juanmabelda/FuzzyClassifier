# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 16:07:03 2014

@author: juanma
"""

from .FuzzyVars import *
from scipy.optimize import fmin_slsqp
from numpy import percentile, array, diff

def optimize_partition(FClass, Variable, VarName, terms):
    '''Optimize the partition of a variable to reduce the ambiguity in the
    clasification of a Fuzzy Variable.
    
    Parameters
    ==========
    
    - FClass : The Fuzzy variable representing the classification.
    - Variable : A real continuous variable that we want to Fuzzify
    - VarName : The name of the Fuzzy Variable
    - term : A set of linguistic terms representing the partition
    
    
    Output
    =========
    
    - fuzzy_function : An optimum fuzzyfication function
    - fuzzy_var : The variable fuzzified according to the fuzzy_function
    
    
    Usage
    ==========

    >>> fuzzy_function, fuzzy_var = optimize_partition(FClass, Variable, terms)
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    the_var = Variable
    the_Fclass = FClass
    the_terms = terms
    the_Name = VarName
    nTerms = len(terms)

    min_val = min(the_var)
    max_val = max(the_var)

    
    # This functions makes the optimization according to the parameters
    def do_fuzzification(p_pars):
        fuzz_func = dict()
        
        # Parameters came proportional to the remaining segment
        mini_val = min_val
        D = max_val-mini_val
        pars = []
        for c in range(nTerms):
            temp = D * p_pars[c] + mini_val
            D = max_val - temp
            mini_val = temp
            
            pars.append(temp)
        

        # Creating the terms from the parameters
        fzFunc, fzVar = points_partition(the_var, the_Name, pars, the_terms)
        
        return (fzVar, fzFunc)

    # This is the function to be optimized    
    def class_amb(pars):
        
        fzVar, temp = do_fuzzification(pars)
        
        try:
            out = ClassAmbiguity(the_Fclass, fzVar)
        except:
            out = 1
            
        return out
        
    # Default values
    default_pars = []
    the_bounds = []
    
    # We need one more point than linguistic terms
    for c in range(nTerms):
        temp = (1./(nTerms + 1 - c))
        default_pars.append(temp)
        the_bounds.append((0.1,0.9))
        
    # Now we do the optimization
    new_pars = fmin_slsqp(class_amb, x0 = default_pars, bounds = the_bounds)

        
    fzVar, fzFunc = do_fuzzification(new_pars)
    
    return (fzFunc, fzVar)
    
def points_partition(Variable, VarName, points, terms):
    '''Partition of a variable where splitting points are provided.
    
    Parameters
    ==========
    
    - Variable : A real continuous variable that we want to Fuzzify
    - VarName : The name of the Fuzzy Variable
    - Points : An array of points defining the cutting points
    - term : A set of linguistic terms representing the partition
    
    
    Output
    =========
    
    - fFunc : The fuzzyfication function
    - fVar : The variable fuzzified according to the fuzzy_function
    
    
    Usage
    ==========

    >>> fFunc, fVar = percentile_partition(Variable, VarName, points, terms)
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   '''
    

    if len(terms) != len(points):
        raise("Inconsisten Dimensions")

    nPoints = len(terms)
    
    # Creating the terms from the parameters  
    fuzz_func = dict()
    for c in range(nPoints):
        if c == 0:
            func = cFF(lff, points[0], points[1])
        elif c == (nPoints - 1):
            func = cFF(rff, points[c-1], points[c])
        else:
            func = cFF(cff, points[c-1],points[c],points[c+1])
            
        fuzz_func[terms[c]] = func

    fzFunc = Fuzzification(VarName,**fuzz_func)
    fzVar = fzFunc(Variable)
        
    
    return (fzFunc, fzVar)



def percentile_partition(Variable, VarName, terms):
    '''Partition of a variable with quantile criteria.
    Each membership is designed to contain the same namber of samples within.
    The quantile dependes on the number of linguistic terms of the partition.
    If the number of partitions implies quantiles at the same point, the
    number of terms is automatically decreased.
    
    Parameters
    ==========
    
    - Variable : A real continuous variable that we want to Fuzzify
    - VarName : The name of the Fuzzy Variable
    - term : A set of linguistic terms representing the partition
    
    
    Output
    =========
    
    - fuzzy_function : The fuzzyfication function
    - fuzzy_var : The variable fuzzified according to the fuzzy_function
    
    
    Usage
    ==========

    >>> fuzzy_function, fuzzy_var = percentile_partition(FClass, Variable, terms)
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    nPoints = len(terms)
    perc_pts = ((array(range(nPoints)) + 1.) / (nPoints + 1)) * 100.
    cut_pts = [percentile(Variable, p) for p in perc_pts]
    
    if min(diff(cut_pts)) == 0.:
        if len(terms) > 2:
            terms.remove(terms[1])
            return percentile_partition(Variable, VarName, terms)
        else:
            cut_pts = [min(Variable), max(Variable)]
        
    # Creating the terms from the parameters 
    fzFunc, fzVar = points_partition(Variable, VarName, cut_pts, terms)

    return (fzFunc, fzVar)
    
    
def C_crisp(category):
    '''Closure for fuzzy crisp functions'''
    the_category = category
    
    def crisp_function(value):
        '''Function fuzzifying a category of a Fuzzy function'''
        if value == category:
            return 1.
        else:
            return 0.
            
    output = crisp_function
    output.args = category
            
    return output

def crisp_partition(Variable, VarName, terms):
    '''Partition of a variable consisting of a set of different categories
    (such as in the case of gender).

    Parameters
    ===========

    - Variable : A list with the Variable we want to fuzzify
    - VarName  : The name of the fuzzy variable
    - terms    : Categories of classification

    Usage
    =========

    >>> my_func, my_var = crisp_partition(Gender, "Gender", ["Man", "Woman"])
    '''

    FuzzyCrisp = dict()
    for term in terms:
        FuzzyCrisp[str(term)] = C_crisp(term)
        
    Ffunc = Fuzzification(VarName, **FuzzyCrisp)
    
    Fvar = Ffunc(Variable)
        
    return (Ffunc, Fvar)
