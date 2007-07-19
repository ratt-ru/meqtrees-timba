# Helper class to compose the the function string for functionals

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.Meq import meq
from numarray import *
from Timba.Contrib.MXM.TDL_Funklet import *

class Functional:
    def __init__(self,function="",pp={},test=None,var_def={'x0':"time",'x1':"freq"},Npar=0):
        """create the function_string, function is a string with parameters p0,...,pN, parlist is list of parramters.
        This can be either another functional or a number initializing the parameter.
        For simplicity one could  specify the number of parameters
        in this functional (so WITHOUT counting the nr. of pars in other subfunctionals), if specified, any missing paramters will
        be initialised with 0.For safety reasons NO other keywords than p0..pN are allowed..."""

        if Npar<=0:
            #print "Number of parameters not specified, assuming",len(pp);
            Npar=self._npar=len(pp);
        self._function=function;
        self._start_par=0;
        self._npar=Npar;
        self._last_par=Npar;
        self._coeff=[];
        self._test=test;
        self._funklet=None;
        self._var_def=var_def;
        if isinstance(pp,list):
            """if pp is list assume these are all numbers, initializing the parameters"""
            #print "pp is a list, assuming these are just numerical coefficients",pp;
            self._coeff=pp;
            if Npar>len(pp):
                for i in range(len(coeff),Npar):
                    self._coeff.append(0);
        else:    
            tmp_start_par=0;
            for par in range(Npar):
                this_par=0.;

                par_str = "p"+str(par);

                if pp.has_key(par_str):
                    this_par=pp[par_str];
                if isinstance(this_par,Functional):
                    par_str = "p"+str(tmp_start_par);
                    this_par.setStartPar(tmp_start_par);
                    fstr="("+this_par.getFunction()+")";
                    n=this_par.getNpar();
                    if n>1:
                        self._shift(tmp_start_par+1,n-1);#shifts all later par with step n
                    self._coeff[len(self._coeff):]=this_par.getCoeff();
                    self._replace_str(par_str,fstr);
                    tmp_start_par+=n;
                else:
                    tmp_start_par+=1;
                    self._coeff.append(this_par);

        self._funklet = Funklet(funklet = record(function = self._function,coeff=self._coeff));

    def eval(self,test=None):
        """evaluate functional at point test"""


        if(test):
            self._test=test;
        if not self._test:
            print "Please specify variables,assuming (x0=0,x1=0,x2=0,x3=0)"
            self._test=dict(x0=0,x1=0,x2=0,x3=0);


        if self._funklet:
            return self._funklet.eval(self._test);
        self._eval_string = self._function;
        for i in range(len(self._coeff)-1,-1,-1):#reverse iteration to get rid of problems with p-numbers >= 10  
            par_str="p"+str(i);
            par=self._coeff[i];
            self._eval_string = self._eval_string.replace(par_str,str(par));
        for xkey in self._test:
            self._eval_string = self._eval_string.replace(xkey,str(self._test[xkey]));
            




        #replace  ^ with **
        self._eval_string=  self._eval_string.replace("^","**");
        
        #print "evaluating",self._eval_string;
        return eval(self._eval_string);


    def plot(self,cells=None,newpage=False):
        #print self._funklet;
        if self._funklet is None:
            return;
        else:
            
            return self._funklet.plot(cells=cells,newpage=newpage);
        
    
    def _shift(self,start,shift):
        for n in range(self._last_par-1,start-1,-1):
            old_par_str="p"+str(n);
            new_par_str="p"+str(n+shift);
            self._replace_str(old_par_str,new_par_str);
        self._last_par+=shift;

    def _reverse_shift(self,start,shift):
        for n in range(start,self._last_par):
            old_par_str="p"+str(n);
            new_par_str="p"+str(n-shift);
            self._replace_str(old_par_str,new_par_str);
        self._last_par-=shift;
    

    def _replace_str(self,old,new):
        #print "replacing",old,"with",new,"in",self._function;
        self._function = self._function.replace(old,new);
        #print "new string",self._function;

    def getFunction(self):
        return self._function;

    def getNpar(self):
        return self._npar;

    def getCoeff(self):
        return self._coeff;

    def setStartPar(self,start):
        #print "setting start_par",start,self._start_par;
        if start >  self._start_par:
            self._shift(self._start_par,start-self._start_par);
        if start< self._start_par:
            self._reverse_shift(self._start_par,self._start_par-start);
            

        self._start_par=start;


    def setCoeff(self,i,cf):
        if i<self._npar:
            self._coeff[i]=cf;
            self._funklet.setCoeff(self._coeff);

    def getFunklet(self):
        funklet=meq.polc(coeff=self._coeff,subclass=meq._funklet_type);
        funklet.function=self._function;
        return funklet;

    def display(self,var_def=None):
        """returns a more readable string,any keys in axis_def are replaced"""
        if var_def is not None:
            self._var_def=var_def;
        print_str = self._function;
        if self._var_def is not None:
            for key in self._var_def:
                print_str=print_str.replace(key,self._var_def[key]);
        print print_str;
        return print_str;

def create_polc(shape=[1,1],coeff=None):
    """helper function,creates functional for polc with shape shape,
    you can initialize any parameters by specifying coeff, coeff will be assumed 0 for all missing """
    func=""
    if coeff is None:
        coeff=[];
    if len(shape)==1: 
        shape.append(1);
    if shape[0]==0:
        shape[0]=1;
    if shape[1]==0:
        shape[1]=1;
    nr_par=0;
    startp=0;
    for i in range(shape[1]):
        for j in range(shape[0]):
            nr_par=nr_par+1;
            if(len(coeff)<nr_par):
                coeff.append(0.);
            func=func+'p'+str(startp);
            for i2 in range(j):
                func = func + '*'+ "x0";
            for i1 in range(i):
                func = func + '*'+ "x1";
            func = func + "+"
            startp=startp+1;
            #print "createing polc",nr_par,coeff,i,j;
    #remove last +
  
    fstr= func[0:len(func)-1];  
    return Functional(fstr,pp=coeff,Npar=nr_par);

    
