from Timba.TDL import *
from Timba import pynode
from Timba.Meq import meq
from Timba import mequtils

Settings.forest_state.cache_policy = 100;

class LMInjector (pynode.PyNode):
  def update_state (self,mystate):
    # mystate does some magic to map fields from the node constructor into
    # fields in 'self'
    mystate('domain_l',[0,1]);
    mystate('domain_m',[0,1]);
    mystate('num_l',5);
    mystate('num_m',5);
    mequtils.add_axis('l');
    mequtils.add_axis('m');
    
  def modify_child_request (self,request):
    try:
      print '***** original: ',request.cells;
      # these things modify the cells object in-place
      meq.add_cells_axis(request.cells,'l',self.domain_l,self.num_l);
      meq.add_cells_axis(request.cells,'m',self.domain_m,self.num_m);
      print '***** modified: ',request.cells;
      # return the modified request object
      return request;
    except:
      print "Error forming up modified request:";
      traceback.print_exc();
      print "Using original request";
      return None;
  
  def get_result (self,request,*children):
    # pass through result of first child
    return children[0];


def _define_forest (ns,**kwargs):
  ns.x << Meq.Grid(axis='l')+Meq.Grid(axis='m');
  ns.inj << Meq.PyNode(ns.x,
                       class_name="LMInjector",module_name=__file__,
                       num_l=10,num_m=20);

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('inj',request);

  