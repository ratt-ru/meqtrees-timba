#!/usr/bin/python

import sys

# first things first: setup app defaults from here and from
# command line (this has to go first, as other modules being imported
# may depend on app_defaults settings)
import app_defaults

#-------- update default debuglevels
app_defaults.debuglevels.update({
  'MeqNode'      :2,
  'MeqForest'    :2,
  'MeqSink'      :2,
  'MeqSpigot'    :2,
  'MeqVisHandler':2,
  'MeqServer'    :2,
  'meqserver'    :1  
});

#-------- update default arguments
app_defaults.args.update({'launch':True,'spawn':None,
                         'verbose':2,'wp_verbose':0 });
                         
#-------- parse command line
if __name__ == '__main__':
  app_defaults.parse_argv(sys.argv[1:]);

import os
import string
import time
import octopussy
from pretty_print import PrettyPrinter
from app_proxy import app_proxy
from dmitypes import *
import meq


# default launch arguments (for launch=True)
default_launch = ('meqserver','M','M');
# default spawn arguments (for spawn=True)
default_spawn = ( os.environ['HOME']+'/LOFAR/installed/current/bin/meqserver',
                  '-noglish','-meq:M:O:MeqServer' );

class meqserver (app_proxy):
  "interface to MeqServer app";
  def __init__(self,appid='meqserver',launch=None,spawn=None,**kwargs):
    # if launch or spawn is just True, substitute default values
    if launch:
      if isinstance(launch,bool) and launch:
        launch = default_launch;
      elif len(launch) == 2:
        launch = ('meqserver',) + launch;
    if spawn and isinstance(spawn,bool):
      spawn = default_spawn;
    # init base class  
    app_proxy.__init__(self,appid,launch=launch,spawn=spawn,**kwargs);
    
    # setup own state
    self._we_track_results = None;
    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
    if self.get_verbose() > 0:
      self.dprint(1,'verbose>0: auto-enabling node_result output');
      self.track_results(True);
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
      self.dprintf(3,'sending command %s with wait\n',command);
      self.dprint(5,'arguments are ',args);
      self.pause_events();
      self.send_command('command'+command,payload);
      msg = self.await(replyname,resume=True);
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

mqs = None;


# inits a meqserver
def default_mqs (debug={},**kwargs):
  global mqs;
  if not isinstance(mqs,meqserver):
    # start octopussy if needed
    if not octopussy.is_initialized():
      octopussy.init(gw=True);
    if not octopussy.is_running():
      octopussy.start(wait=True);
    # start meqserver, overriding default args with any kwargs
    args = app_defaults.args;
    args.update(kwargs);
    print 'starting a meqserver with args:',args;
    mqs = meqserver(**args);
    mqs.init(srecord(output_col='PREDICT'),wait=False);
    if debug is None:
      pass;
    else:
      octopussy.set_debug(app_defaults.debuglevels);
      if isinstance(debug,dict):
        octopussy.set_debug(debug);
  return mqs;
  
#
# self-test block
#
if __name__ == '__main__':
  app_defaults.parse_argv(sys.argv[1:]);
  gui = app_defaults.args['gui'];
  
  default_mqs(verbose=2,wp_verbose=2);
  for i in range(1,10):
    print 'createnode:',mqs.createnode(meq.node('MeqConstant','x'+str(i),value=0),wait=False);

  if gui:
    mqs.run_gui(); 
  else:
    time.sleep(2);

  print '================= stopping mqs';
  mqs.halt();
  mqs.disconnect();
    
  print "===== calling octopussy.stop() =====";
  octopussy.stop();

