#!/usr/bin/python

import octopussy
import sys
import string
import time
from pprint import PrettyPrinter
from app_proxy import app_proxy
from dmitypes import *

class meqserver (app_proxy):
  "interface to MeqServer app";
  def __init__(self,appid='meqserver',launch=None,verbose=0,**kwargs):
    if launch:
      if isinstance(launch,bool):
        launch = ('meqserver','M','M');
      elif len(launch) == 2:
        launch = ('meqserver',) + launch;
    app_proxy.__init__(self,appid,launch=launch,verbose=verbose,**kwargs);
    
    self._we_track_results = None;
    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
    if kwargs.get('verbose',0) > 0:
      self.dprint(1,'verbose>0: auto-enabling node_result output');
      public.track_results(True);
      self.dprint(1,'you can disable this by calling .track_results(False)');
  
  # define meqserver-specific methods
  def meq (self,command,args=None,wait=False,silent=False):
    "sends a meq-command and optionally waits for result";
    command = make_hiid(command);
    payload = srecord();
    if not args is None:
      payload.args = args;
    # send command and wait for reply
    if wait:
      if silent:
        self.dprint(0,'warning: both wait and silent specified, ignoring silent flag');
      payload.request_id = self.new_rqid();
      replyname = 'app.result' + command + payload.request_id;
      self.dprintf(3,'sending command %s with wait',command);
      self.dprint(5,'arguments are ',args);
      self.pause_events();
      self.send_command('command'+command,payload);
      msg = self.await(replyname);
      return msg.payload;
    # else simply send command
    else: 
      self.dprintf(3,'sending command %s with no wait, silent=%d\n',command,silent);
      self.dprint(5,'arguments are ',args);
      payload.silent = silent;
      self.send_command('command'+command,payload);
  
  # helper function to create a node specification record
  def makenodespec (self,node):
    "makes an srecord containing a node specification";
    if isinstance(node,str):
      return srecord({'name':node});
    elif isinstance(node,int):
      return srecord({'nodeindex':node});
    else:
      raise TypeError,'node must be specified by name or index, have '+str(type(node));

  def createnode (self,initrec,wait=False,silent=False):
    initrec = make_srecord(initrec);
    return self.meq('Create.Node',initrec,wait=wait,silent=silent);
  
  def getnodestate (self,node):
    return self.meq('Node.Get.State',self.makenodespec(node),wait=True);
  
  def getnodeindex (self,name):
    retval = self.meq('Get.NodeIndex',self.makenodespec(name),wait=True);
    try: return retval.nodeindex;
    except:
      raise ValueError,'MeqServer did not return a nodeindex field';

  def getnodelist (self,name=True,nodeindex=True,classname=True,children=False):
    rec = srecord({'name':name,'nodeindex':nodeindex,'class':classname,'children':children});
    return self.meq('Get.Node.List',rec,wait=True);
  
  def execute (self,node,req):
    rec = self.makenodespec(node);
    rec.request = req;
    return self.meq('Node.Execute',rec,wait=True);
  
  def _result_handler (self,msg):
    try:
      value = msg.payload;
      print '============= result for node: ',value.name;
      self._pprint.pprint(value);
    except:
      print 'exception in meqserver._resulthandler: ',sys.exc_info();
  
  def track_results (self,enable=True):
    if enable:
      self.dprint(2,'auto-printing all node_result events');
      if self._we_track_results:
        self._we_track_results.activate();
      else:
        self._we_track_results = self.whenever('node.result',self._result_handler);
    else:  # disable
      self.dprint(2,'disabling auto-printing of node_result events');
      if self._we_track_results:
        self._we_track_results.deactivate();

default_debuglevels = {
  'MeqNode'      :2,
  'MeqForest'    :2,
  'MeqSink'      :2,
  'MeqSpigot'    :2,
  'MeqVisHandler':2,
  'MeqServer'    :2,
  'meqserver'    :1  
};
  
mqs = None;


# inits a meqserver
def default_mqs (verbose=3,debug={},gui=False):
  global mqs;
  if not octopussy.is_running():
    octopussy.start();
  if not isinstance(mqs,meqserver):
    mqs = meqserver(launch=True,verbose=verbose);
    mqs.init(srecord(output_col='PREDICT'),wait=True);
    if debug is None:
      pass;
    else:
      octopussy.set_debug(default_debuglevels);
      if isinstance(debug,dict):
        octopussy.set_debug(debug);
  return mqs;
  
#
# self-test block
#
if __name__ == '__main__':
  default_mqs();
  rec = srecord({'class':'MeqConstant'},name='x',value=0);
  print 'rec: ',rec;
  print 'createnode:',mqs.createnode(rec,wait=True);
  octopussy.stop();

