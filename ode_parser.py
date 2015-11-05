# py/pyext - python script objects for PD and MaxMSP
#
# Copyright (c) 2002-2007 Thomas Grill (gr@grrrr.org)
# For information on usage and redistribution, and for a DISCLAIMER OF ALL
# WARRANTIES, see the file, "license.txt," in this distribution.  
#

"""        
        name = "Lorenz"
        variables = "x y z"
        parameters = "r b tau"
        inputs = "I1"
        eq = "dx = (11.0*(y - x)+I1)/tau;dy = (x*(r - z) - y)/tau;dz = (x*y - b*z)/tau;"

"""

try:
    import pyext
except:
    print "ERROR: This script must be loaded by the PD/Max pyext external"

import pypdode

import os
    
#################################################################

class generate(pyext._class):
    """Example of a simple class which receives messages and prints to the console"""

    # number of inlets and outlets
    _inlets=1
    _outlets=0
    VARIABLES = ""
    PARAMETROS = ""
    INPUTS = ""
    FORMULA = ""
    NAME = ""

    # methods for first inlet

    def build_1(self):
        
        print os.getcwd(), os.path.dirname(os.path.abspath(__file__))

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        pypdode.parse(self.NAME,self.VARIABLES,self.PARAMETROS,self.FORMULA,self.INPUTS)
        pypdode.build(self.NAME)
        pypdode.patch(self.NAME,self.PARAMETROS,self.INPUTS,self.VARIABLES)

    def print_1(self):

        print os.getcwd()
        print "Name ",self.NAME
        print "Eq ",self.FORMULA
        print "Variables ",self.VARIABLES
        print "Parameters ",self.PARAMETROS
        print "Inputs ",self.INPUTS
   
    def variables_1(self,*argv):
        s = ""        
        for arg in argv:
            s = s +" " + str(arg)
                  
        self.VARIABLES = s.lstrip().rstrip()
    
    def parameters_1(self,*argv):
        s = ""        
        for arg in argv:
            s = s +" " + str(arg)
                  
        self.PARAMETROS = s.lstrip().rstrip()
        
    def eq_1(self,*argv):
        s = ""        
        for arg in argv:
            print arg
            s = s +" " + str(arg)
                  
        self.FORMULA = s.lstrip().rstrip()
    
    def symbol_1(self,sym):
        self.FORMULA = self.FORMULA + str(sym) + "; " 

    def inputs_1(self,*argv):
        s = ""        
        for arg in argv:
            s = s +" " + str(arg)
                  
        self.INPUTS = s.lstrip().rstrip()
        
    def name_1(self,*argv):
        s = ""        
        for arg in argv:
            s = s +" " + str(arg)
                  
        self.NAME = s.lstrip().rstrip()
        
    def clear_1(self):
        
        self.NAME = ""
        self.PARAMETROS = ""
        self.INPUTS = ""
        self.VARIABLES = ""
        self.FORMULA = ""