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

from Timba.TDL import *
from Timba.Grid import DataItem
from Timba.Grid import Services
from Timba.Meq import meq
from Timba.Meq import meqds
from numarray import *
from qt import *


def copy_keys(orig =record(), cp = record()):
    for key in orig.keys():
        
        cp[key]=orig[key];


class Funklet:
    def __init__(self,funklet=record(function="MeqPolc",coeff=array([[0.]]),domain= meq.domain(0,1,0,1),offset=[0,0],scale=[1,1]),name=None):
        self._funklet=funklet;
        self._type = "MeqPolc";
        if funklet.has_field('function'):
            self._type=funklet.function;
        self._coeff = array([[0]]);
        if funklet.has_field('coeff'):
            self._coeff=funklet.coeff;
            if isinstance(self._coeff,list):
                self._coeff = self._funklet.coeff = array(self._coeff);
                
        self._offset=None;
        self._scale=None;
        if funklet.has_field('offset'):
            self._offset = funklet.offset;
        if funklet.has_field('scale'):
            self._scale = funklet.scale;
        self._domain = meq.domain(0,1,0,1);
        if funklet.has_field('domain'):
            self._domain = funklet.domain;
        if funklet.has_field('name') and funklet.name:
            self._name = funklet.name;
        else:
            if name:
                self._name=name;
            else:
                self._name='test';
        if self._name:
            self._udi = "/funklet/"+self._name;
        else:
            self._udi = "/funklet/noname";

        self.init_function();
        

    def getNX(self):
        return self._nx;

    def getNAxis(self):
        #dummy
        return None;

    def getDomain(self):
        return self._domain;

    def setDomain(self,domain = meq.domain(0,1,0,1)):
        self._domain=domain;

    def setCoeff(self,coeff):
        self._coeff=coeff;
        #print self._coeff;
        if isinstance(self._coeff,list):
            self._coeff = array(self._coeff);
        self._meqfunklet.coeff = self._coeff;

    def get_meqfunklet(self):
        if self._meqfunklet == None:
            self.init_function();
        return self._meqfunklet;
            
    def init_function(self):
        self._nx=0;
        self._meqfunklet=None;
        if self._type ==  "MeqPolc":
            self._meqfunklet = meq.polc(self._coeff,subclass=meq._polc_type);
            copy_keys(self._funklet,self._meqfunklet)
            self._meqfunklet.function=None;
            self._create_polc();

        else:
            if self._type ==  "MeqPolcLog" :
                self._meqfunklet = meq.polc(self._coeff,subclass=meq._polclog_type);
                copy_keys(self._funklet,self._meqfunklet)
                self._meqfunklet.function=None;
                self._create_polc(log=True);
            
            else:
                self._meqfunklet = meq.polc(self._coeff,subclass=meq._funklet_type);
                copy_keys(self._funklet,self._meqfunklet)
                self._create_functional();
                #print "created functional",self._meqfunklet;
                
        self.isConstant=False;
        if not self._nx:
            #print "this function is constant"
            self._constant = self.eval();
            self.isConstant=True;
            if not is_scalar(self._constant):
                self._constant = self._constant[0]
    
    def _create_polc(self,log=False,Constants = []):
        self._function="";
        coeff =   self._coeff
        if is_scalar(coeff):
            coeff=[[coeff]];
        if is_scalar(coeff[0]):
            ncoeff=[];
            for i in range(len(coeff)):
                ncoeff.append([coeff[i]]);
            coeff=ncoeff;

        self._coeff=  coeff;
        shapex = len(coeff);
        shapey = len(coeff[0]);
        
        
        axis = [];
        if shapex > 1 :
            axis.append("x0");
            self._nx=1;
        if shapey > 1 :
            axis.append("x1");
            self._nx =2;
        self._axis = axis;
        x0_def="x[0]";
        x1_def="x[1]";
        
        if log:
            if not Constants:
                Constants=[1.,1.]
            if Constants[0]:
                x0_def = "log(x[0]/"+str(Constants[0])+")";
            if Constants[1]:
                x1_def = "log(x[1]/"+str(Constants[1])+")";
            

        function="";
        for xi in range(shapex):
            for yi in range(shapey):
                c_str = "C["+str(xi)+"]["+str(yi)+"]";
                x0_str="";
                for i in range(xi):
                    x0_str += "*"+x0_def;
                x1_str="";
                for i in range(yi):
                    x1_str += "*"+x1_def;
                function += c_str + x0_str + x1_str +"+";

        self._function =function[0:len(function)-1];
        #print "created function",self._function;


    def _create_functional(self):
        for i in range(10,-1,-1):#max number of axis = 10 at the moment
            x_str = "x"+str(i);
            #print "finding:",x_str,"in",self._type;
            if self._type.find(x_str)>=0:
                self._nx=i+1;
                break;
        shape =  self._coeff.shape
        newshape = 1;
        for i in shape:
            newshape *= i;
        self._coeff.setshape((newshape,));
        function = self._type;
        for i in range(len(self._coeff)-1,-1,-1):
            c_str = "C["+str(i)+"]";
            p_str = "p"+str(i);
            function = function.replace(p_str,c_str);
        for i in range(self._nx):
            x_old="x"+str(i);
            x_new= "x["+str(i)+"]";
            function = function.replace(x_old,x_new);
        self._function = function;
        #print "created function",self._function,self._nx;

        
    def eval(self,point={}):
        if self.isConstant:
            #print "returning constant",self._constant;
            return self._constant;
        C=self._coeff;

        if self._nx<=0:
            eval_str = self._function;

            # replace  ^ with **
            eval_str=  eval_str.replace("^","**");
            value = eval(eval_str);
            return value;




        if point is None:
            point = {'x0':0};
        
        x=[];
        if isinstance(point,dict):
            for i in range(0,10):
                x_str = "x"+str(i);
                if point.has_key(x_str):
                    #add zeros for missing x's
                    if len(x) < i-1:
                        for j in range(len(x),i-1):
                            x.append(0.);
                    x.append(point[x_str]);
        else:
            if isinstance(point,list):
                x = point;
        #print "X:",x;


        
        offset  = zeros((self._nx,),Float64);
        scale  = ones((self._nx,),Float64);
        if len(x) > self._nx:
            print "too many coordinates specified, only using first",self._nx;
            del x[self._nx:];

        if not self._offset is None:
            nr=0;
            for i in self._offset:
                #print "offset", offset, self._nx,self._offset,i;
                offset[nr] = i;
                nr+=1;
        if not self._scale is None:
            nr=0;
            for i in self._scale:
                #print "scale", scale,i;
                if i:
                    scale[nr] = 1./i;
                nr+=1;
                
            
        
        for i in range(len(point),self._nx):
            x.append(0);
        nr=0;
        for i in x:
            x[nr]=(i-offset[nr])*scale[nr];
            nr+=1;
            


        eval_str = self._function;

        #replace  ^ with **
        eval_str=  eval_str.replace("^","**");

        #print "evaluating",eval_str;
        #print "x",x
        #print "C",C;
        

        value = eval(eval_str);

        #print "value",value;
        return value;

    

    def get_data(self,cells=None):
        if self.isConstant:
            return array([self._constant]);
        if cells is None :
            return None;
        #print "nx",self._nx;
        grid = cells.grid;
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;

        #print "axis_map",axis_map;
        #print "grid",grid,len(grid),grid[str(axis_map[0]['id']).lower()];
        shape= ();

        nr_defined_axes = 0;
        for i in range(len(axis_map)):
            if axis_map[i].has_key('id') and axis_map[i]['id']:
                nr_defined_axes = nr_defined_axes+1;
            else:
                break;
        if self._nx > nr_defined_axes:
            print "axis missing in axis_map, adding defaults to  forest_state"
            axis_map = self.add_axis_to_forest_state();

            #self._nx = len(axis_map);

        for i in range(self._nx):
            #if not axis_map[i].has_key('id'):
            #    self._nx=i;
            #    break;
            if axis_map[i].has_key('id')  and grid.has_key(str(axis_map[i]['id']).lower()):
           
                shape += (len(grid[str(axis_map[i]['id']).lower()]),);
            else:
                shape +=(1,);
        data = zeros(shape, Float32);
        #print "creating shape",shape,self._nx;

        if len(grid) < self._nx:
            print "axis missing in cells, assuming 0",grid,self._nx #not sure if this is a problem
        k=zeros((self._nx,));
        gridarray=[];
        for i in range(self._nx):
            if axis_map[i].has_key('id') and grid.has_key(str(axis_map[i]['id']).lower()):
                #print "id",str(axis_map[i]['id']).lower(),"found",grid[str(axis_map[i]['id']).lower()],k[i];
                gridarray.append(grid[str(axis_map[i]['id']).lower()]);
            else:
                #print "id",str(axis_map[i]['id']).lower(),"not found";
                gridarray.append([0.]);

        #print "gridarray",gridarray;

        while k[0]<(shape[0]):
            x=[];
            p = ();

            #print "grid",grid,"axis_map",axis_map;
            for i in range(self._nx):

                if len(gridarray[i]) >= k[i]:
                    x.append(  gridarray[i][ k[i] ]);
                else:
                    #print "id",str(axis_map[i]['id']).lower(),"not found";
                    x.append(0.);
                p+=(k[i],);

            #print "writing point",p,x
            data[p] = self.eval(x);
            #print data;
            for i in range(self._nx-1,-1,-1):
                k[i]+=1;
                if k[i]>=shape[i]:
                    #print "next k",k,i
                    if i>0:
                        k[i]=0;
                    else:
                        
                        break;
                else:
                    break;


        #print "data",data
        return data;


    def get_result(self,cells=None):
        data = self.get_data(cells=cells);
        if data is None:
            print "get_result failed, no data"
            return None;
        vellset      = record(shape=data.shape,value=data);
        result = meq.result(cells=cells,vellset=vellset);
        # result assumes axis_map in domain needed for result_plotter
 
        dom  =  result.cells.domain;
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;
        axis_list = [];
 
        for i in range(len(axis_map)):
            if axis_map[i].has_key('id') and axis_map[i]['id']:
                axis_list.append(str(axis_map[i]['id']).lower());
        dom['axis_map'] = axis_list;
 
        result.cells.domain = dom;
        #print result;
        return result;


    def create_default_cells(self):
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;
        dom_ax = {};
        cells_ax = {};
        for i in range(self._nx):
            
            if not axis_map[i].has_key('id'):
                self.add_axis_to_forest_state();
            axis = str(axis_map[i]['id']).lower();

            dom_ax[axis] = (0.,1.);
            num = 'num_'+axis;
            cells_ax[num] = 5;
            
        dom = meq.gen_domain(**dom_ax);
        cells = meq.gen_cells(dom,**cells_ax);
        return cells;

    def plot(self,cells=None,parent=None,newpage=False):
        if cells is None:
            print "no cells specified"

            cells = self.create_default_cells();
            
        if not isinstance(cells,meq._cells_type):
            raise TypeError,'cells argument must be a MeqCells object';
        result = self.get_result(cells=cells);
        
        self.emit_display_signal(result=result,parent=parent,newpage=newpage,newcell=True);
        return result;


    def emit_display_signal (self,result=None,parent=None,newpage=False,newcell=False,**kwargs):
        name=self._name;
        caption=self._name;
        dataitem=DataItem(self._udi,data=result,viewer='Result Plotter',name=name,caption=caption);
        if dataitem:
            if parent:
                parent.emit(PYSIGNAL("displayDataItem()"),(dataitem,kwargs));
            else:
                #print "plotting"
                Services.addDataItem(dataitem,newpage=newpage,newcell=newcell);



    def add_axis_to_forest_state(self,axis=['l','m'],axis_nr=[2,3] ):
        """define extra axes in forest state"""
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;
        if not isinstance(axis,list):
            axis = [axis];
        if is_scalar(axis_nr):
            axis_nr=[axis_nr]
            for i in range(1,len(axis)):
                axis_nr.append(axis_nr[i-1]+1);
        for i in range(len(axis)):
            axis_map[axis_nr[i]].id=hiid(axis[i]);
        Settings.forest_state.axis_map = axis_map;
        return axis_map;
  

class ComposedFunklet(Funklet):
    """ class for a list of funklets...reimplement eval"""
    
    def __init__(self,funklet_list,domain=meq.domain(0,1,0,1)):
        self._Naxis=[];
        self._domain=domain;
        self._funklet_list = funklet_list;
        # initialize domain;
        funk=funklet_list[0];
        self._name = funk._name;
        self._udi = funk._udi;
        self.isConstant = False;
        forest_state=meqds.get_forest_state();
        self._axis_map=forest_state.axis_map;
        if len(self._funklet_list)==1 and funk.isConstant: 
            self.isConstant = True;
            self._constant = funk._constant;
            self._nx = 0;
        else:
            self.getNX();


    def setDomain(self,domain=meq.domain(0,1,0,1)):
        self._domain=domain;
        self.getNX();

    def getNX(self):
        #mkae guess based on regular gridding
        self._nx=0;
        for funk in self._funklet_list:
            if funk.getNX()>self._nx:
                self._nx = funk.getNX();
        funk=self._funklet_list[0];
        tiled = funk.getDomain();


        #print "axis_map",self._axis_map;
        #print "funk",funk;
        #print "domain",self._domain;
        self._Naxis=[];
        for i in self._axis_map:
            if not i.has_key('id'):
                break;
            if not self._domain.has_key(str(i['id']).lower()):
                break;
            if not tiled.has_key(str(i['id']).lower()):
                break;
            dom_size = self._domain[str(i['id']).lower()][1]-self._domain[str(i['id']).lower()][0];
            tile_size = tiled[str(i['id']).lower()][1]-tiled[str(i['id']).lower()][0];
            N = int(dom_size/tile_size+0.5);
            #print "domain for Comp_funklet ",i['id'],N;
            self._Naxis.append(N);
        self._nx=len(self._Naxis);
        
        return self._nx;

    def getNAxis(self):
        return self._Naxis;


    def eval(self,point={}):
        #evaluate for the right  funklet, check on domain;
        pointlist=[];
        #convert to list
        if isinstance(point,dict):
            for i in range(0,10):
                x_str = "x"+str(i);
                if point.has_key(x_str):
                    #add zeros for missing x's
                    if len(pointlist) < i-1:
                        for j in range(len(pointlist),i-1):
                            pointlist.append(0.);
                    pointlist.append(point[x_str]);
        else:
            if isinstance(point,list):
                pointlist = point;
        axis_map=self._axis_map;
        for funklet in self._funklet_list:
            # get first matching funklet:
            domain = funklet.getDomain();
            axisi = 0;
            match=True;
            #print "domain",domain,axis_map,str(axis_map[0]['id']).lower();
            for x in pointlist:
                if not axis_map[axisi].has_key('id'):
                    break;
                if not domain.has_key(str(axis_map[axisi]['id']).lower()):
                    break;
                #print "testing",str(axis_map[axisi]['id']).lower(),domain[str(axis_map[axisi]['id']).lower()][0],x,domain[str(axis_map[axisi]['id']).lower()][1]
                if domain[str(axis_map[axisi]['id']).lower()][0] > x or domain[str(axis_map[axisi]['id']).lower()][1] < x:
                    #print "No MATCH"
                    match=False;
                    break;
                axisi+=1;
            if match:
                return funklet.eval(pointlist);
            
        #if we get here,no match was found...what should we do now???
        return 0;
