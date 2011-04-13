#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import sys
import atexit
import traceback
from Timba.Meq import meqds

# first things first: setup app defaults from here and from
# command line (this has to go first, as other modules being imported
# may depend on app_defaults settings)
from Timba.Apps import app_defaults
if app_defaults.include_gui:
  try:
    from Timba.GUI.meqserver_gui import *
  except:
    print "*** Error importing GUI modules:";
    traceback.print_exc();
    pass;

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

import traceback
import os
import string
import time
from Timba import octopussy
from Timba import mequtils
from Timba.pretty_print import PrettyPrinter
from Timba.Apps.multiapp_proxy import multiapp_proxy
from Timba.dmi import *
from Timba.utils import *
from Timba.Meq import meq


# default spawn arguments (for spawn=True)
default_spawn = ("meqserver");
default_spawn_opt = ("meqserver-opt");
default_launch = ();

class meqserver (multiapp_proxy):
  """interface to MeqServer app""";
  def __init__(self,appid='meqserver',client_id='meqclient',
               spawn=None,opt=False,**kwargs):
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
    multiapp_proxy.__init__(self,appid,client_id,spawn=spawn,**kwargs);
    # setup own state
    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
    # track axis map changes
    self._we_axis_list = self.whenever('axis.list',self._axis_list_handler);
    # if base/gui init() has explicitly disabled result tracking, _we_track_results
    # will be False rather than None
    if self.get_verbose() > 0 and self._we_track_results is None:
      self.dprint(1,'verbose>0: auto-enabling node_result output');
      self.track_results(True);
      self.dprint(1,'you can disable this by calling .track_results(False)');
  
  # define meqserver-specific methods
  def meq (self,command,args=None,wait=None,silent=False):
    """sends a meq-command and optionally waits for result.
    wait can be specified in seconds, or True to wait indefinitely.""";
    command = make_hiid(command);
    payload = record();
    if args is not None:
      payload.args = args;
    # send command and wait for reply
    if wait:
      if isinstance(wait,bool):
        wait = None;       # timeout=None means block indefinitely
      if silent:
        self.dprint(0,'warning: both wait and silent specified, ignoring silent flag');
      payload.command_index = self.new_command_index();
      replyname = 'result' + command + payload.command_index;
      self.dprintf(3,'sending command %s with wait\n',command);
      self.dprint(5,'arguments are ',args);
      self.pause_events();
      self.send_command('command'+command,payload);
      msg = self.await(replyname,resume=True,timeout=wait);
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
  
  def getnodestate (self,node,wait=True,sync=False):
    spec = self.makenodespec(node);
    spec.sync = sync;
    return self.meq('Node.Get.State',spec,wait=wait);

  def setnodestate (self,node,fields_record,wait=False,sync=True):
    spec = self.makenodespec(node);
    spec.sync = sync;
    spec.state = fields_record;
    return self.meq('Node.Set.State',spec,wait=wait);
  
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
    
  def clearcache (self,node,recursive=True,wait=False,sync=True):
    rec = self.makenodespec(node);
    rec.recursive = recursive;
    rec.sync = sync;
    return self.meq('Node.Clear.Cache',rec,wait=wait);
  
  def change_wd (self,path):
    rec = record(cwd=path);
    return self.meq('Set.Cwd',rec,wait=False);
    
  def publish (self,node,wait=False):
    rec = self.makenodespec(node);
    rec.level = 1;
    return self.meq('Node.Set.Publish.Level',rec,wait=wait);
    
  def _event_handler (self,msg):
    """Auguments app_proxy._event_handler(), to keep track of forest state""";
    multiapp_proxy._event_handler(self,msg);
    payload = msg.payload;
    if self.current_server \
       and getattr(msg,'from') == self.current_server.addr \
       and isinstance(payload,record):
      # check if message includes update of forest state and/or status
      fstatus = getattr(payload,'forest_status',None);
      fstate  = getattr(payload,'forest_state',None);
      # update forest state, if supplied. Merge in the forest status if
      # we also have it
      if fstate is not None:
        if fstatus is not None:
          fstate.update(fstatus);
        meqds.update_forest_state(fstate);
      # no forest state supplied but a status is: merge it in
      elif fstatus is not None:
        meqds.update_forest_state(fstatus,merge=True);
    
  def _result_handler (self,msg):
    try:
      value = msg.payload;
      dprint(0,'============= result for node: ',value.name);
      self._pprint.pprint(value);
    except:
      print 'exception in meqserver._result_handler: ',sys.exc_info();
      traceback.print_exc();
      
  def _axis_list_handler (self,msg):
    try:
      if self.current_server \
            and getattr(msg,'from') == self.current_server.addr: \
        mequtils.set_axis_list(msg.payload);
    except:
      print 'exception in meqserver._axis_list_handler: ',sys.exc_info();
      traceback.print_exc();
  
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
def default_mqs (debug={},nokill=False,extra=None,**kwargs):
  global mqs;
  if not isinstance(mqs,meqserver):
    # create a local tcp port
    gwlocal = "=meqbatch-%d"%os.getpid();
    # start octopussy if needed
    if not octopussy.is_initialized():
      octopussy.init(gwclient=False,gwtcp=0,gwlocal=gwlocal+":1");
    if not octopussy.is_running():
      octopussy.start(wait=True);
    # start meqserver, overriding default args with any kwargs
    args = record(**app_defaults.args);
    args.update(kwargs);
    # add gwpeer= argument
    if isinstance(extra,str):
      extra = args.extra + extra.split(' ');
    extra = (extra or []) + ["-gw",gwlocal];
    spawn = args.get('spawn',None);
    mqs = meqserver(extra=extra,**args);
    mqs.dprint(1,'default meqserver args:',args);
    meqds.set_meqserver(mqs);
    if not nokill:
      atexit.register(stop_default_mqs);
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
    if mqs.current_server:
      mqs.dprint(1,"stopping default meqserver");
      mqs.halt();
      mqs.disconnect();
    # kill process if it is still running after 10 seconds
    if mqs.serv_pid:
      for i in range(10):
        pid,stat = os.waitpid(mqs.serv_pid,os.WNOHANG);
        if pid:
          break;
        time.sleep(1);
      else:
        mqs.dprint(0,"meqserver not exiting cleanly, killing it");
        os.kill(mqs.serv_pid,9);
        pid,stat = os.waitpid(mqs.serv_pid,os.WNOHANG);
    mqs = None;
  if octopussy.is_running():
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

