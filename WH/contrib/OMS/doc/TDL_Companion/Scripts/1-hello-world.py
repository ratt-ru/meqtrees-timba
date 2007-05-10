from Timba.TDL import *

def _define_forest (ns,**kwargs):
  ns.hello_world << Meq.Constant(value=0,message="Hello world!");
  
print "Hello world!"
