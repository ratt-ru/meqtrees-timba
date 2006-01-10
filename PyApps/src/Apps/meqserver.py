#!/usr/bin/python

import sys

# first things first: setup app defaults from here and from
# command line (this has to go first, as other modules being imported
# may depend on app_defaults settings)
from Timba.Apps import app_defaults
if app_defaults.include_gui:
  from Timba.GUI.meqserver_gui import *

# #-------- update default debuglevels
# app_defaults.debuglevels.update({
#   'MeqNode'      :2,
#   'MeqForest'    :2,
#   'MeqSink'      :2,
#   'MeqSpigot'    :2,
#   'MeqVisHandler':2,
#   'MeqServer'    :2,
#   'meqserver'    :1  
# });
# 

#-------- parse command line
if __name__ == '__main__':
  app_defaults.parse_argv(sys.argv[1:]);

import os
import string
import time
from Timba import octopussy
from Timba.pretty_print import PrettyPrinter
from Timba.Apps.app_proxy import app_proxy
from Timba.dmi import *
from Timba.utils import *
from Timba.Meq import meq


# default spawn arguments (for spawn=True)
default_spawn = ("meqserver");
default_spawn_opt = ("meqserver-opt");
default_launch = ();

class meqserver (app_proxy):
  "interface to MeqServer app";
  def __init__(self,appid='meqserver',client_id='meqclient',launch=None,spawn=None,opt=False,**kwargs):
    # if launch or spawn is just True, substitute default values
    if launch:
      if isinstance(launch,bool) and launch:
        launch = default_launch;
      elif len(launch) == 2:
        launch = ('meqserver',) + launch;
    if spawn and isinstance(spawn,bool):
      if opt:
        spawn = default_spawn_opt;
      else:
        spawn = default_spawn;
    # set gui arg
    if 'gui' in kwargs and kwargs['gui'] and not callable(kwargs['gui']):
      kwargs['gui'] = meqserver_gui;
    self._we_track_results = None;
    # init base class  
    app_proxy.__init__(self,appid,client_id,launch=launch,spawn=spawn,**kwargs);
    # setup own state
    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
    # if base/gui init() has explicitly disabled result tracking, _we_track_results
    # will be False rather than None
    if self.get_verbose() > 0 and self._we_track_results is None:
      self.dprint(1,'verbose>0: auto-enabling node_result output');
      self.track_results(True);
      self.dprint(1,'you can disable this by calling .track_results(False)');
  
  # define meqserver-specific methods
  def meq (self,command,args=None,wait=False,silent=False):
    "sends a meq-command and optionally waits for result";
    command = make_hiid(command);
    payload = record();
    if not args is None:
      payload.args = args;
    # send command and wait for reply
    if wait:
      if silent:
        self.dprint(0,'warning: both wait and silent specified, ignoring silent flag');
      payload.request_id = self.new_rqid();
      replyname = 'result' + command + payload.request_id;
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
    "makes an record( containing a node specification";
    if isinstance(node,str):
      return record(name=node);
    elif isinstance(node,int):
      return record(nodeindex=node);
    else:
      raise TypeError,'node must be specified by name or index, have '+str(type(node));

  def createnode (self,initrec,wait=False,silent=False):
    initrec = make_record(initrec);
    return self.meq('Create.Node',initrec,wait=wait,silent=silent);
  
  def getnodestate (self,node):
    return self.meq('Node.Get.State',self.makenodespec(node),wait=True);
  
  def getnodeindex (self,name):
    retval = self.meq('Get.NodeIndex',self.makenodespec(name),wait=True);
    try: return retval.nodeindex;
    except:
      raise ValueError,'MeqServer did not return a nodeindex field';

  def getnodelist (self,name=True,nodeindex=True,classname=True,children=False):
    rec = record({'name':name,'nodeindex':nodeindex,'class':classname,'children':children});
    return self.meq('Get.Node.List',rec,wait=True);
  
  def execute (self,node,req,wait=False):
    rec = self.makenodespec(node);
    rec.request = req;
    return self.meq('Node.Execute',rec,wait=wait);
    
  def publish (self,node,wait=False):
    rec = self.makenodespec(node);
    rec.enable = True;
    return self.meq('Node.Publish.Results',rec,wait=wait);
  
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
      self._we_track_results = False;

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
    # print 'meqserver args:',args;
    mqs = meqserver(**args);
    if debug is None:
      pass;
    else:
      octopussy.set_debug(app_defaults.debuglevels);
      if isinstance(debug,dict):
        octopussy.set_debug(debug);
  return mqs;
  
def stop_default_mqs ():
  global mqs;
  if mqs: 
    mqs.halt();
    mqs.disconnect();
  octopussy.stop();
  
  
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

