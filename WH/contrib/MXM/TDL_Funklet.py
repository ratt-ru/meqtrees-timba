from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from numarray import *



class Funklet:
    def __init__(self,funklet=record(function="MeqPolc",coeff=array([[0]]),domain= meq.domain(0,1,0,1),offset=[0,0],scale=[1,1])):
        self._funklet=funklet;
        self._type = "MeqPolc";
        if funklet.has_field('function'):
            self._type=funklet.function;
        self._coeff = array([[0]]);
        if funklet.has_field('coeff'):
            self._coeff=funklet.coeff;
            #print self._coeff;
            if isinstance(self._coeff,list):
                self._coeff = array(self._coeff);

        self._offset=None;
        self._scale=None;
        if funklet.has_field('offset'):
            self._offset = funklet.offset;
        if funklet.has_field('scale'):
            self._scale = funklet.scale;
        self._domain = meq.domain(0,1,0,1);
        if funklet.has_field('domain'):
            self._domain = funklet.domain;
        self.init_function();
        

    def getNX(self):
        return self._nx;

    def getDomain(self):
        return self._domain;

    def setCoeff(self,coeff):
        self._coeff=coeff;
        #print self._coeff;
        if isinstance(self._coeff,list):
            self._coeff = array(self._coeff);
    
    def init_function(self):
        self._nx=0;
        if self._type ==  "MeqPolc":
            self._create_polc();

        else:
            if self._type ==  "MeqPolcLog" :
                self._create_polc(log=True);
            
            else:
                self._create_functional();
                
        self.isConstant=False;
        if not self._nx:
            #print "this function is constant"
            self.isConstant=True;
            self._constant = self._coeff[0]
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
        for i in range(len(self._coeff)):
            c_str = "C["+str(i)+"]";
            p_str = "p"+str(i);
            function = function.replace(p_str,c_str);
        for i in range(self._nx):
            x_old="x"+str(i);
            x_new= "x["+str(i)+"]";
            function = function.replace(x_old,x_new);
        self._function = function;
        #print "created function",self._function;

        
    def eval(self,point={}):
        if self.isConstant:
            return self._constant;
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
        offset  = zeros((self._nx,));
        scale  = ones((self._nx,));
        if len(x) > self._nx:
            print "too many coordinates specified, only using first",self._nx;
            del x[self._nx:];

        if not self._offset is None:
            nr=0;
            for i in self._offset:
                #print offset, self._nx,self._offset,i;
                offset[nr] = i;
                nr+=1;
        if not self._scale is None:
            nr=0;
            for i in self._scale:
                if i:
                    scale[nr] = 1./i;
                nr+=1;
                
            
        
        for i in range(len(point),self._nx):
            x.append(0);
        nr=0;
        for i in x:
            x[nr]=(i-offset[nr])*scale[nr];
            nr+=1;
            
        C=self._coeff;
               
        value = eval(self._function);
        return value;

    

    def get_data(self,cells=None):
        if cells is None :
            return None;
        
        grid = cells.grid;
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;

        #print "axis_map",axis_map;
        #print "grid",grid,len(grid),grid[str(axis_map[0]['id']).lower()];
        shape= ();
        for i in range(self._nx):
            if grid.has_key(str(axis_map[i]['id']).lower()):
           
                shape += (len(grid[str(axis_map[i]['id']).lower()]),);
            else:
                shape +=(1,);
        data = zeros(shape, Float32);

        if not len(grid) == self._nx:
            print "axis missing in cells, assuming 0" #not sure if this is a problem
        k=zeros((self._nx,));
        while k[0]<(shape[0]):
            x=[];
            p = ();
            for i in range(self._nx):
                if grid.has_key(str(axis_map[i]['id']).lower()):
                    x.append(grid[str(axis_map[i]['id']).lower()][k[i]]);
                else:
                    x.append(0.);
                p+=(k[i],);

            #print "writing point",p
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
                
        return data;


    def get_result(self,cells=None):
        data = self.get_data(cells=cells);
        if data is None:
            print "get_result failed, no data"
            return None;
        result = meq.result(cells=cells,data=data);
        #print result;
        return result;

    def plot(self,cells=None):
        if cells is None:
            print "no cells specified"
            return;
        if not isinstance(cells,meq._cells_type):
            raise TypeError,'cells argument must be a MeqCells object';
        return self.get_result(cells=cells);
        

class ComposedFunklet(Funklet):
    """ class for a list of funklets...reimplement eval"""
    
    def __init__(self,funklet_list):
        self._funklet_list = funklet_list;
        # initialize domain;
        self._nx=0;
        for funk in self._funklet_list:
            if funk.getNX()>self._nx:
                self._nx = funk.getNX();
        

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
        #print "pointlist:",pointlist;
        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;
        for funklet in self._funklet_list:
            # get first matching funklet:
            domain = funklet.getDomain();
            axisi = 0;
            match=True;
            #print "domain",domain,axis_map,str(axis_map[0]['id']).lower();
            for x in pointlist:
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
