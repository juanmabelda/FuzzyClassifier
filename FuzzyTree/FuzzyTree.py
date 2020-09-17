# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 12:37:01 2014

@author: JMBELDA
"""

from .FuzzyVars import *
from numpy import zeros, isnan

class FuzzyTree(object):
    '''Creating a FuzzyTree Object:
    
    Parameters
    ============
    - theFuzzySet : A FuzzySet object containing the data in which building the tree
    - Beta        : Threshold level of truthness to become a Leaf
    - Alfa        : Minimum activation for reliable evidence
    - LHS         : Left Hand Side: The arguments of the rule
    - RHS         : The clasification FuzzyVar
    
    Example
    ============

    >>> #%% Look for the file FuzzyTree.py to watch the example of the article
    >>> FT = FuzzyTree(example,
                               0.7,
                               ["Outlook", "Temperature", "Humidity", "Wind"],
                               "Plan")
    

    References
    ============
    Yuan, Yufei, & Michael J. Shaw. "Induction of fuzzy decision trees". 
    Fuzzy Sets and Systems 69, n.º 2 (27th January 1995): 125-39. 
    doi:10.1016/0165-0114(94)00229-Z.

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''
    
    def __init__(self, theFuzzySet, Beta, Alfa, LHS, RHS):
        
#        if type(theFuzzySet) != FuzzySet:
#            raise Exception("Invalidy type for the Fuzzy Set")
            
        self._Beta = Beta
        self._Alfa = Alfa
        self._NodeParent = FuzzyTreeNode()
        self._FuzzySet = theFuzzySet
        self._Leaves = [] # These are the leaves of the tree
        
        self._LHS = LHS  # Precedentes
        self._RHS = RHS # Consequente
        
        self._createTree()
        
    def GetNodeParent(self):
        return self._NodeParent
        
    NodeParent = property(GetNodeParent,doc="Node parent (main stem) of the tree")
        
    def _createTree(self):
        '''Creation of the FuzzyTree'''
                
        theFuzzySet = self._FuzzySet
        
        C = self._RHS #FuzzyVar classification
        
        fs_C = theFuzzySet[C]
        
        all_vars = set(self._LHS) # All the memberships
        
        #all_vars = all_vars - set([C])
        
        #.....................................................................
        #STEP 1: Measure the classification ambiguity associated
        #        with each attribute
        
        # select the attribute with the smallest classification ambiguity
        # as the root decision node
        
        mFvar = "" # Name of the FuzzyVar with less ambiguity
        
        for P in self._LHS:
            try:
                FSamb = ClassAmbiguity(fs_C, theFuzzySet[P])
            except:
                FSamb = 1.
                
            if not("mini" in locals()):
                mini = FSamb
                mFvar = P
            if FSamb < mini:
                mini = FSamb
                mFvar = P
                
                
        self._NodeParent  = FuzzyTreeNode(FVarName = mFvar)
        self._NodeParent.Truth = mini
        
        NodeList = [self._NodeParent]
        
        # This flag is for checking the creation of a node
        NodeFlag = False
        
        #.....................................................................
        #STEP 3: Repeat step 2 for all newly generated decision nodes until
        # no further growth is possible, the decision tree then is complete.
        for Node in NodeList:
            #print NodeList
        
            # Current classification ambiguity
            #curr_CA = ClassAmbiguity(fs_C, theFuzzySet[Node.Name])
            curr_CA = Node.Truth
            
            #..................................................................
            #STEP 2:
            # Delete all empty branches of the decision node
            kkName = Node.Name
            P = self._FuzzySet[Node.Name]
                    

            #print Node.Name, C
            for mu_k in theFuzzySet[Node.Name].keys():       
                
                # For each nonempty branch of the decision node, calculate the 
                # truth level of classifying all objects within the branch
                # into each class
                
                #tr_lev = dict() # Truth level
                
                # The membership partitition
                try:
                    mu = Node.mu(theFuzzySet)
                except (KeyError):
                    mu = None
                #print Node
                
                # Member function includes the branch
                mu = P[mu_k] & mu
                
                if max(mu) < self._Alfa:
                    continue

                try:
                    Fz_ev = FuzzyEvidence2(fs_C, mu)
                except(ZeroDivisionError):
                    continue
                    
                tr_lev = max(Fz_ev.values())
                
                if tr_lev == 0: continue
                
                if tr_lev > self._Beta:
                    self._SelectNode(Fz_ev,Node,mu_k)
                    continue
                    
                # Otherwise, investigate if an additional attribute will further
                # partition the branch (i.e. generate more than one nonempty 
                # branch) and further reduce the classification ambiguity
                    
#                if NodeFlag:
#                    NodeFlag = False
#                    continue
                    
                v = Node.FVAncestors
                # A flag for recursion on ambiguity
                AmbRed = False
                # These are the FuzzyVars not included in the tree
                new = (all_vars - v)
                # We remove also current node
                new = list(new - set([Node.Name]))
                # If all variables are already included we move to the next
                if len(new) == 0:
                    Fz_ev = FuzzyEvidence2(fs_C, mu)
                    self._SelectNode(Fz_ev,Node,mu_k)
                    continue
                    
                #amb = dict()
                for Pa in new:
                    # The variable under Analysis
                    FV_P = theFuzzySet[Pa]
                    try:
                        amb = ClassAmbiguityWithP(fs_C, FV_P, mu)
                    except(ZeroDivisionError):
                        amb = 1.
                        AmbRed = False
                        continue
                    
                    if amb < curr_CA: 
                        AmbRed = True
                        if not("target") in locals():
                            target = amb
                            ins_node = Pa
                        else:
                            if amb < target:
                                target = amb
                                ins_node = Pa

                # If yes, select the attribute with smallest classification
                # ambiguity as a new decision node from the branch.                            
                if AmbRed:
                    newN = Node.append(ins_node, mu_k)
                    newN.Truth = target
                    NodeList.append(newN)
                    del target
                        
                # If not, terminate this branch as a leaf. At the leaf, all objects
                # will be labelled to one class with the highest truth level.
                if not(AmbRed):
                    if (amb == 1.) | (isnan(amb)): continue
                    Fz_ev = FuzzyEvidence2(fs_C, mu)
                    self._SelectNode(Fz_ev,Node,mu_k)
                    
        #print NodeList
        
    def _SelectNode(self, Fz_ev, Node, mu_k):
        tr_lev = max(Fz_ev.values())
        for mu_c in Fz_ev.keys():
            if Fz_ev[mu_c] == tr_lev:
                newN = Node.append(mu_c, mu_k)
                newN.IsLeaf = True
                newN.Truth = tr_lev
                self._Leaves.append(newN)
                break
            
    def __repr__(self):
        '''Shows the rules underlying the tree'''
        output = ""
        for leaf in self._Leaves:
            cad = "IF "
            for p in leaf.Ancestors:
                rule, condition = p.split(":")
                temp = "(%s==%s)" % (rule, condition)
                cad += temp + " AND "
                
            cad = cad[:-4] + " THEN (" + self._RHS + "==" + leaf.Name + ")"
            cad += ": %f" % leaf.Truth
            output += cad + "\n"
        
        return output
        
    def _output_Node_tree(self, Node):
        '''Iteratively provides the links of the tree'''
        output = '"%s" [label = "%s"]\n' % (Node.ID, Node.Name)
        
        if Node.IsLeaf:
            return output
        
        for child in Node._Sons:
            cad = '"%s"->"%s" [label = "%s"]\n' % (Node.ID, child.ID, child._PMemb)
            output += cad
            output += self._output_Node_tree(child)
            
        return output
    
    def output_to_dot_graphviz(self, filename):
        '''Draws the tree as a dot graphviz digraph'''
        
        tree = self._output_Node_tree(self.NodeParent)
        
        f = open(filename, "w")
        print("digraph G{",file=f)
        print(tree,file=f)
        print("}",file=f)
        
        f.close()
        
    def classify(self, theFuzzySet):
        '''Performs a classification according to the rules of the tree'''
        
        # Creating the output
        kNV = self._FuzzySet[self._RHS].keys() # Output memberships
        dNV = dict()
        length = len(theFuzzySet)
        
        for k in kNV:
            dNV[k] = zeros([length])
        
        # This is the output variable
        fNV = FuzzyVar(self._RHS,**dNV)
        
        #..............................................................
        # Now we go for the classification
        for leaf in self._Leaves:
            evidence = leaf.mu(theFuzzySet)
            fNV[leaf.Name] = fNV[leaf.Name] | evidence
        
        return fNV
        
    def confussion_matrix(self, RealClass, FuzzySet, print_matrix = True):
        '''Calculation of the confussion matrix of the classification'''
        
        Result = self.classify(FuzzySet)
        
        output = dict()
        
        for rc in RealClass.keys():
            output[rc] = dict()
            for ec in Result.keys():
                output[rc][ec] = 0.
        
        for rc, ec in zip(RealClass, Result):
            M_rc = 0.
            M_ec = 0.
            
            for k in rc.keys():
                if (rc[k] >= M_rc):
                    M_rc = rc[k]
                    k_rc = k
                    
                if (ec[k] >= M_ec):
                    M_ec = ec[k]
                    k_ec = k
            
            try:
                output[k_rc][k_ec] += 1.0
            except:
                output[k_rc][k_ec] = 0.
                
                
        # Printing the output
        head = str(RealClass.Name) + "\t"
        for rc in RealClass.keys():
            head += rc + "\t"
        
        if print_matrix: print(head)
        
        for ec in Result.keys():
            row = ec + "\t"
            for rc in RealClass.keys():
                row += str(output[rc][ec]) + "\t"
            
            if print_matrix: print(row)
                    
        return output

    
    
class FuzzyTreeNode(object):
    '''A node of a Fuzzy tree:
    
    Parameters
    ============
    
    - FVarName:  The name of the FuzzyVar that borns on the node.
    - Parent:    The parent node object.
    - PMemb :    The name of the membership function
    - Leaf:     Is this node a Leaf?: True, False, None
    - Truthness: Level of true of the current node

    Author
    =======
    Juanma Belda: jmbeldalois@gmail.com

    IBV - Valencia (July 2014)   
    '''

    def __init__(self,  FVarName = None, Parent = None, PMemb = None,
                 Leaf = None, Truthness = 0. ):
        
        self._FVarName = FVarName
        self._Parent = Parent
        self._PMemb = PMemb
        self.IsLeaf = Leaf
        self._Truthness = Truthness
        self._Sons = []
        
        # Updating ancestors
        try:
            self._Ancestors = [p for p in Parent.Ancestors]
            cad = "%s:%s" % (Parent.Name, PMemb)
            self._Ancestors.append(cad)
        except(AttributeError):
            self._Ancestors = []
            
        # Including me as a son
        if Parent != None:
            Parent._Sons.append(self)
            
        
    def get_Name(self):
        return self._FVarName
        
    Name = property(get_Name, doc = "Name of the FuzzyVar in the Node")
    
    def get_True(self):
        return self._Truthness
    
    def set_True(self, Value):
        self._Truthness = Value
        
    Truth = property(get_True,set_True, doc = "Level of Truthness")

    def get_parent(self):
        return self._Parent
        
    Parent = property(get_parent, doc = "Reference to the Parent Node")
        
        
    def __repr__(self):
        if type(self._FVarName) == str:
            FV = self._FVarName
        else:
            FV = ""
            
        if type(self._Parent) == FuzzyTreeNode:
            Pa = self._Parent._FVarName
        else:
            Pa = "[root]"
            
        if type(self._PMemb) == str:
            mu = self._PMemb
        else:
            mu = ""
            
        cad = "%s: %s(%s) %f" % (FV, Pa, mu, self._Truthness)
        
        return cad
        
    def getAncestors(self):
        '''Return the list of nodes up to the root node'''
        return self._Ancestors
        
    Ancestors = property(getAncestors)
    
    def getFVAncestors(self):
        output = []
        for a in self._Ancestors:
            [P, u] = a.split(":")
            output.append(P)
            
        return set(output)
        
    FVAncestors = property(getFVAncestors,doc="Return the Fuzzyvar ancestors")
    
    def _getId(self):
        output = ""
        
        for node in self.Ancestors:
            output += node + ";"
            
        output += self.Name
            
        return output
        
    ID = property(_getId)
    
    def mu(self, theFuzzyVar):
        '''Returns the Fuzzymembership object including the logic up to
        the current node'''
        
        if len(self._Ancestors) == 0: return None
        
        for node in self._Ancestors:
            try:
                new_mu = theFuzzyVar.mu(node)
            except(TypeError):
                continue
            
            try:
                value = value & new_mu
            except(NameError):
                value = new_mu
                
        return value
                     
    
    def append(self, theFVar, theFmemb):
        '''Appends a new node as son of the current node'''
        
        newNode = FuzzyTreeNode(FVarName=theFVar, Parent=self, PMemb=theFmemb)
        
        #self._Sons.append(newNode)
        
        # If we append sons is no longer a Leaf
        self.IsLeaf = False
        
        return newNode
        
        
       
        