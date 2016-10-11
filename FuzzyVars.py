# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 17:48:54 2014

@author: JMBELDA
"""

from numpy import mean, log, iterable
from pylab import plot, show, axis, legend

def pLog(value):
    '''Helper function: Log of value if it is positive definite
    0. if value is 0 or less'''
    
    if value > 0.:
        return log(value)
    else:
        return 0.

def cFF(function, *args):
    '''Closure for the fuzzyfication function'''
    the_args = args
    the_f = function
    def in_f(value):
        return the_f(value, *the_args)
        
    # Adding the information
    in_f.args = args
    return in_f

def lff(x,m1,m2):
    '''Left Fuzzyfication function'''
    if x < m1:
        return 1.
    elif x > m2:
        return 0.
    else:
        return (m2 - x)/(m2 - m1)
        
def rff(x,m1,m2):
    '''Right Fuzzyfication function'''
    if x < m1:
        return 0.
    elif x > m2:
        return 1.
    else:
        return (x - m1)/(m2 - m1)
        
def cff(x,m1,m2,m3):
    '''Center Fuzzyfication function'''
    if x < m1:
        return 0.
    elif (x >= m1) & (x < m2):
        return (x - m1)/(m2 - m1)
    elif (x >= m2) & (x < m3):
        return (m3 - x)/(m3 - m2)
    elif (x >= m3):
        return (0.)


class Fuzzification(object):
    '''Class to fuzzyfy to a given Fuzzy Value
    
    Parameters
    ==========
    
    - varName : The name of the Fuzzy variable resulting as output
    - **kargs : Pairs of linguistic labeles and Closures of Fuzzizcation fns
    '''
    
    def __init__(self, varName, **kargs):
        self._values = kargs
        self._varName = varName
        
    def __call__(self, value):
        if iterable(value) & (type(value) != str):
            # Inicialising variables
            output = dict()
            
            temp = dict()
            for k in self._values.keys():
                output[k] = []
                
            for v in value:
                for k in self._values.keys():
                    output[k].append(self._values[k](v))
                    
            return FuzzyVar(self._varName, **output)
            
        else:
            output = dict()
            for k in self._values.keys():
                output[k] = self._values[k](value)
            
            return FuzzyValue(**output)
            
    def do_plot(self, values):
        var = self(values)
        
        for k in var.keys():
            plot(values, var[k])
            
        axis([min(values), max(values), 0, 1.1])
        legend(var.keys(), loc = "lower right")
        print var.keys()
            
        show()

class FuzzyValue(object):
    '''A Fuzzy number consisting of a set of membership values.
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    def __init__(self, **kargs):
        self._values = kargs
        
    def __str__(self):
        return self._values.__str__()
        
    def __repr__(self):
        return self._values.__repr__()
        
    def __getitem__(self, name):
        return self._values[name]
        
    def __setitem__(self, name, value):
        self._values[name] = value
        
    def __and__(self, other):
        output = dict()
        
        for k in self._values.keys():
            output[k] = min(self[k],other[k])
            
        return FuzzyValue(**output)
        
    def __or__(self, other):
        output = dict()
        
        for k in self._values.keys():
            output[k] = max(self[k],other[k])
            
        return FuzzyValue(**output)
        
    def keys(self):
        return self._values.keys()
        
    def values(self):
        return self._values.values()
        

    def ambiguity(self):
        '''Ambiguity:
        :math:'E_a(Y) = g(\pi)=\sum_{i=1}^n {(pi_i^* - pi_{i+1}^*) \cdot ln(i)}' 
        
        Calculation of the ambiguity associated to an attribute
        Ambiguity or nonspecificity measure: Let n = (n(x)ln X) denote a 
        normalized possibility distribution of Y on X = {x 1, x2 ..... x. }
        
        Usage
        ========
        >>> a.ambiguity()
        
        References
        ==========
        
        Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
        Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
        doi:10.1016/0165-0114(94)00229-Z.
        
        
        Author
        =======
        Juanma Belda: jmbeldalois@gmail.com
        
        IBV - Valencia (July 2014)   
        '''

        # Normalize the values of the variable to the maximum
        vals = self.values()
        max_val = max(vals)       
        vals = [float(v)/max_val for v in vals]
        
        # Addding a zero
        vals.append(0.)
        
        # Sorting from upside down
        vals.sort()
        vals.reverse()
        
        # Making the calculations
        t = 0.
        for c in range(0,len(vals)-1):
            #print vals[c]
            t += (vals[c] - vals[c+1]) * log(c + 1)
            
        return t

class FuzzyVar(object):
    '''A Fuzzy Variable consisting on a set of Fuzzy Values
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    def __init__(self, attr, **kargs):
        self._values = kargs
        self._attribute = attr
        
        # This is the counter for the iterator
        self._current = 0
        
    def __getitem__(self, name):
        return FuzzyMembership(self._attribute, name, self._values[name])
        
        
    def __setitem__(self, name, value):
        if len(self._values[name] == len(value)):
            for c in range(len(value)):
                self._values[name][c] = value[c]
        else:
            raise("Sizes not compatible")
            
    def _getname(self):
        return self._attribute
        
    Name = property(_getname)
        
    def append(self, **kargs):
        for k in kargs:
            self._values[k].append(kargs[k])
            
    def __repr__(self):
        cad = self._attribute + "\n"
        val = list()
        
        # Creating the header
        for k in self._values.keys():
            cad  += k + "\t"
            val.append(self._values[k])
            
        cad = cad[0:-1] + "\n"
        
        # Creating the values
        for vs in zip(*val):
            for v in vs:
                cad += str(v) + "\t"
            
            cad = cad[0:-1] + "\n"
            
        return cad
        
    def __eq__(self, member):
        return FuzzyMembership(self._attribute, member, self._values[member])
        
    def value(self,index):
        a = dict()
        for k in self.keys():
            a[k] = self._values[k][index]
            
        return FuzzyValue(**a)
        
    def __iter__(self):
        return self
        
    def __len__(self):
        return len(self._values.values()[0])
        
    def next(self):
        try:
            output = self.value(self._current)
        except:
            self._current = 0
            raise StopIteration
            
        self._current += 1
            
        return output
        
        
    def keys(self):
        return self._values.keys()
        
    def values(self):
        return self._values.values()
        
    def ambiguity(self):
        '''Calculation of the ambiguity associated to an attribute
        Ambiguity or nonspecificity measure: Let n = (n(x)lxeX) de note a 
        normalized possibility distribution of Y on X = {x 1, x2 ..... x. }
        
        Usage
        ========
        >>> a.ambiguity()
        
        References
        ==========
        
        Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
        Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
        doi:10.1016/0165-0114(94)00229-Z.
        
        
        Author
        =======
        Juanma Belda: jmbeldalois@gmail.com
        
        IBV - Valencia (July 2014)   
        '''
        
        ambs = [f.ambiguity() for f in self]
        
        return mean(ambs)
       


class FuzzyMembership(object):
    '''Representation of the values of the members of a Fuzzy set
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    def __init__(self, Attr, Member, Values):
        self._attribute = Attr
        self._mu = Member
        self._value = Values
        
        
    def __and__(self, other):
        
        if other == None:
            return self

        if other._attribute == self._attribute:
            attr = self._attribute
            mu = "%s & %s" % (self._mu, other._mu)
        else:
            attr = "?"
            mu = "%s(%s) & %s(%s)" % (self._attribute, self._mu, other._attribute, other._mu)
        
        vals = [] # Output values
        
        for m,y in zip(self._value, other._value):
            vals.append(min(m,y))
            
        return FuzzyMembership(attr,mu,vals)

    def __or__(self, other):
        if other._attribute == self._attribute:
            attr = self._attribute
            mu = "%s or %s" % (self._mu, other._mu)
        else:
            attr = "?"
            mu = "%s(%s) or %s(%s)" % (self._attribute, self._mu, other._attribute, other._mu)
        
        vals = [] # Output values
        
        for m,y in zip(self._value, other._value):
            vals.append(max(m,y))
            
        return FuzzyMembership(attr,mu,vals)
        
    def fnot(self):
        '''Fuzzy not'''
        attr = self._attribute
        mu = "not(" + self._mu + ")"
        vals = [1. - v for v in self._value]
        
        return FuzzyMembership(attr,mu,list(vals))
        
    def __le__(self, other):
        '''Assessment of subset'''
        return subsethood(self, other)
        
    def __ge__(self, other):
        '''Assessment of superset'''
        return subsethood(other, self)
        
    def __repr__(self):
        cad = "%s:%s\n" % (self._attribute, self._mu)
        cad += self._value.__str__()
        
        return cad
        
    def __len__(self):
        return len(self._value)
        
    def vagueness(self):
        '''Vagueness of a linguistical term.  Definition 4 in 
        Yuan et al. (1995)                
    
        References
        ==========
        
        Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
        Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
        doi:10.1016/0165-0114(94)00229-Z.
        
        
        Author
        =======
        Juanma Belda: jmbeldalois@gmail.com
        
        IBV - Valencia (July 2014)   
        '''
        
        rel_val = [v*pLog(v) + (1- v) * pLog(1 - v) for v in self._value]
                        
        return -mean(rel_val)        
        
    def __getitem__(self, index):
        return self._value[index]
        
    def __setitem__(self, index, value):
        self._value[index] = value
        
        
        
class FuzzySet(object):
    '''Representation of a number of Fuzzy observations with the sames
    attributes
    
    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''

    def __init__(self, *args, **kargs):
        '''Creates a Fuzzy set, and eventually set the attributes'''

        self._vals = dict()
        
        for a in args:
            self._vals[a.Name] = a
        
        for k in kargs:
            member = dict()
            for m in kargs[k]:
                member[m] = []
                
            self._vals[k] = FuzzyVar(k, **member)

        
                
    def __getitem__(self, attribute):
        return self._vals[attribute]
        
    def append(self, **kargs):
        for k in kargs.keys():
            self._vals[k].append(**kargs[k])
            
    def __repr__(self):
        cad = ""
        for k in self._vals.keys():
            cad += self._vals[k].__repr__()
            
        return cad
        
    def __len__(self):
        var = self._vals.keys()[0]
        return len(self._vals[var])
            
    
    def ambiguity(self, Attribute):
        '''Calculation of the ambiguity associated to an attribute
        Ambiguity or nonspecificity measure: Let n = (n(x)lxeX) de note a 
        normalized possibility distribution of Y on X = {x 1, x2 ..... x. }
        
        Usage
        ========
        >>> a.ambiguity("Outlook")
        
        References
        ==========
        
        Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
        Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
        doi:10.1016/0165-0114(94)00229-Z.
        
        
        Author
        =======
        Juanma Belda: jmbeldalois@gmail.com
        
        IBV - Valencia (July 2014)   
        '''
        
        FVars = self._vals[Attribute]
        ambs = [f.ambiguity() for f in FVars]
        
        return mean(ambs)
        
    def mu(self, *args):
        '''Returns a list with the memberships of a given attribute and a
        given member name.
        
        Examples:
        =========
        
        >>> # Example 1        
        >>> a.mu("Outlook","Sunny")        
        >>> # Example 2
        >>> a.mu("Outlook:Sunny")        
        >>> # Example 3
        >>> a["Outlook"] == "Sunny"

        References
        ==========
        
        Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
        Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
        doi:10.1016/0165-0114(94)00229-Z.
        
        
        Author
        =======
        Juanma Belda: jmbeldalois@gmail.com
        
        IBV - Valencia (July 2014)   
        '''
            
        if len(args) == 1:
            Attribute, member = args[0].split(":")
        elif len(args) == 2:
            Attribute = args[0]
            member = args[1]
        else:
            raise Exception("Number of parameters incorrect")       
        
        
        output = self._vals[Attribute][member]
        return output
        
    def keys(self):
        return self._vals.keys()
        
    def attributes(self):
        '''Return the attributes in the Fuzzy set'''
        return self._vals.keys()
        
#membership function        
def subsethood(A, B):
    '''fuzzy subsethood  S(A, B)  measures the degree to which A is a 
    subset of B.
    
    Definition 7 in Yuan et al. (1995)
    
    Parameters
    ===========
    - A: FuzzyMembership
    - B: FuzzyMembership
    
    References
    ==========
    Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
    Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
    doi:10.1016/0165-0114(94)00229-Z.
    

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    if (type(A) != FuzzyMembership) | (type(B) != FuzzyMembership):
        raise Exception("Invalid type")
        
    val = A & B
    
    sval = sum(val._value)
    sA = sum(A._value)
    
    output = sval / sA
    
    return output
    
def FuzzyEvidence(C, mu):
    '''Given fuzzy evidence E, the possibility of classifying an object
    according to a Clasification FuzzyVar.
    
    Definition 9 in Yuan et al.
    
    This is a normalized version according to Yuan et al.
    
    Parameters
    ===========
    
    - C : The FuzzyVar classification variable
    - mu : The Fuzzy membership with the evidence
    
    References
    ==========
    Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
    Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
    doi:10.1016/0165-0114(94)00229-Z.
    

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    out = dict()
    maxim = 0.
    
    for k in C.keys():
        temp = subsethood(mu, C[k])
        out[k] = temp
        if temp > maxim : maxim = temp
            
    for k in C.keys():
        out[k] = out[k] / maxim
        
    #Fout = FuzzyValue(**out)
    
    #return Fout.ambiguity()
    return FuzzyValue(**out)
    
def FuzzyEvidence2(C, mu):
    '''Given fuzzy evidence E, the possibility of classifying an object
    according to a Clasification FuzzyVar.
    
    Definition 9 in Yuan et al.

    This is a non-normalized that seems to be the "true" function used in the
    article.
    
    Parameters
    ===========
    
    - C : The FuzzyVar classification variable
    - mu : The Fuzzy membership with the evidence
    
    References
    ==========
    Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
    Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
    doi:10.1016/0165-0114(94)00229-Z.
    

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    out = dict()
    maxim = 0.
    
    for k in C.keys():
        temp = subsethood(mu, C[k])
        out[k] = temp
#        if temp > maxim : maxim = temp
            
    #Fout = FuzzyValue(**out)
    
    #return Fout.ambiguity()
    return FuzzyValue(**out)
    
def ClassAmbiguityWithP(C, P, mu):
    '''
    The classification ambiguity with fuzzy partitioning
    P = [El . . . . . Ek} on fuzzy evidence F.
    Definition 12 in Yuan et al. (1995)
    
    Parameters
    ==========    

    - C : Clasification FuzzyVar
    - P : Partitioning FuzzyVar
    - mu: Evidence (FuzzyMembership) (F in the original article)
    
    References
    ==========
    Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
    Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
    doi:10.1016/0165-0114(94)00229-Z.
    

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
        
    if type(mu)!=FuzzyMembership:
        raise Exception("Invalid type for the evidence")
        
    if type(P)!=FuzzyVar:
        raise Exception("Invalid type for the partitioning")

    if type(C)!=FuzzyVar:
        raise Exception("Invalid type for the classification")
    
    
    w = dict()
    InSe = dict()
    norm = 0.
    
    for k in P.keys():
        InSe[k] = P[k] & mu # Intersection of evidence and partition
        w[k] = sum(InSe[k])
        norm += w[k]
        
    for k in P.keys():
        w[k] = w[k]/norm
        
    w = FuzzyValue(**w)
    
    #print w
    #print InSe

    result = 0.    
    for k in InSe.keys():
        result += w[k]*FuzzyEvidence(C, InSe[k]).ambiguity()
        
    return result
        
    
def ClassAmbiguity(C,P):
    '''Classification ambiguity given a FuzzyVar'''
    
    w = dict()
    norm = 0.
    for k in P.keys():
        w[k] = sum(P[k])
        norm += w[k]
        
    for k in w.keys():
        w[k] = w[k] / norm
        
    result = 0.
    for k in P.keys():
        result += w[k]*FuzzyEvidence(C, P[k]).ambiguity()
        
    return result
    
    
