###  meqserver.g: MeqTree server
###
###  Copyright (C) 2002-2003
###  ASTRON (Netherlands Foundation for Research in Astronomy)
###  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
###  This program is free software; you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation; either version 2 of the License, or
###  (at your option) any later version.
###
###  This program is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with this program; if not, write to the Free Software
###  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
###  $Id$
pragma include once

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

# These can be uncommented (or set elsewhre prior to include) for debugging.
# app_defaults.g will parse the command line and recognize the following
# options: -suspend, -nostart, -valgrind, -gui, -opt
#
#   use_suspend  := T;
#   use_nostart  := T;
#   use_valgrind := T;
#   use_opt      := T
#   use_valgrind_opts := [ "",
#     "--gdb-attach=yes",          # use either this...
#     "--logfile=meqserver",       # ...or this, not both
#     "--gdb-path=/usr/bin/ddd", 
#   ""];

# these should be declared prior to including app_defaults.g
if( !is_record(default_debuglevels) )
  default_debuglevels := [  MeqNode       =2,
                            MeqForest     =2,
                            MeqSink       =2,
                            MeqSpigot     =2,
                            MeqVisHandler =2,
                            MeqServer     =2,
                            meqserver     =1 ];

include 'appagent/app_defaults.g'
include 'appagent/app_proxy.g'
include 'meq/meqtypes.g'
include 'recutil.g'

# find path to server binary
if( has_field(lofar_software,'meq') && has_field(lofar_software.meq,'servers') )
  for( f in lofar_software.meq.servers ) {
    if( len(stat(f)) )
    {
      print 'Found path to meqserver binary:',f;
      if( use_valgrind )
        _meqserver_binary := f;
      else
        _meqserver_binary := f;
      break;
    }
  }
# not found? try default
if( !is_defined('_meqserver_binary') )
{
  _meqserver_binary := 'meqserver';
  print 'Will use default meqserver binary, hope this works';
}

# define the server binary specification, using possible debug options set above
const _meqserver := 
    define_octoserver(default_octoserver_fifo,_meqserver_binary,
                      valgrind=use_valgrind,valgrind_opts=use_valgrind_opts,
                      nostart=use_nostart,opt=use_opt);
  
const meq.server := function (appid='MeqServer',
    server=_meqserver,options="-nogw -d0 -meq:M:M:MeqServer",
    verbose=default_verbosity,gui=use_gui,
    ref parent_frame=F,ref widgetset=dws,
    ref self=[=],ref public=[=])
{
  # construct base app_proxy object
  if( is_fail( app_proxy(appid,server=server,options=options,
                         verbose=verbose,gui=gui,
                         parent_frame=parent_frame,widgetset=widgetset,
                         self=self,public=public) ))
    fail;
  # init meqserver-specific data members
  self.track_results := F;
  self.results_log := [=];
  
  # define meqserver-specific methods
  # meq() is a general command interface
  const public.meq := function (cmd_name,args=[=],wait_reply=F,silent=F)
  {
    wider self,public;
    if( wait_reply )
    {
      if( silent )
      {
        self.dprint(0,'warning: both wait_reply and silent specified, ignoring silent flag');
      }
      rqid := self.new_requestid();
      reqname := spaste('Command.',cmd_name);
      replyname := to_lower(cmd_name ~ s/\./_/g);
      replyname := paste('app_result',replyname,rqid,sep='_');
      self.dprint(3,'sending command ',cmd_name);
      self.dprint(5,'arguments are ',args);
      has_reply := F;
      whenever self.relay->[replyname] do
      {
        has_reply := T;
        reply := $value;
        deactivate;
      }
      res := public.command(reqname,[request_id=rqid,args=args]);
      if( is_fail(res) )
      {
        self.dprint(3,'command sending failed');
        fail;
      }
      self.dprint(3,'awaiting reply ',replyname,' from relay');
      while( !has_reply )
        await self.relay->[replyname];
      return reply;
    }
    else
    {
      self.dprint(3,'sending command ',cmd_name,' with no wait, silent=',silent);
      self.dprint(5,'arguments are ',args);
      return public.command(spaste('Command.',cmd_name),[args=args,silent=silent]);
    }
  }
  
  # helper function to create a node specification record
  const self.makenodespec := function (node)
  {
    if( is_string(node) )
      return [ name=node ];
    else if( is_integer(node) )
      return [ nodeindex=node ];
    else
      fail 'node must be specified by name or index';
  }

  # define shortcuts for common methods
  # 
  # ------ createnode()
  const public.setaxismap := function (map,wait_reply=F,silent=F)
  {
    wider public;
    global meq;
    rec := [axis_map = meq.set_axes(map)];
    return public.meq('Set.Axis.Map',wait_reply=wait_reply,silent=silent);
  }
  
  # ------ createnode()
  const public.createnode := function (initrec,wait_reply=F,silent=F)
  {
    wider public;
    return public.meq('Create.Node',initrec,wait_reply=wait_reply,silent=silent);
  }

  # ------ resolve()
  const public.resolve := function (node,wait_reply=F,silent=F)
  {
    wider public;
    rec := self.makenodespec(node);
    return public.meq('Resolve',rec,wait_reply=wait_reply,silent=silent);
  }

  # ------ getnodestate()
  const public.getnodestate := function (node)
  {
    wider self,public;
    rec := self.makenodespec(node);
    return public.meq('Node.Get.State',rec,wait_reply=T);
  }
  
  # ------ setnodestate()
  const public.setnodestate := function (node,state)
  {
    wider self,public;
    rec := self.makenodespec(node);
    rec.state := state;
    return public.meq('Node.Set.State',rec,wait_reply=T);
  }
  
  # ------ getnodeindex()
  const public.getnodeindex := function (name)
  {
    wider self,public;
    rec := self.makenodespec(name);
    retval := public.meq('Get.NodeIndex',rec,wait_reply=T);
    if( is_record(retval) && has_field(retval,'nodeindex') )
      return retval.nodeindex;
    else
      fail 'MeqServer did not return a nodeindex field';
  }
  
  
  # ------ getnodelist()
  
  const public.getnodelist := function (name=T,nodeindex=T,class=T,children=F)
  {
    wider self,public;
    rec := [ name=name,nodeindex=nodeindex,class=class,children=children ];
    return public.meq('Get.Node.List',rec,wait_reply=T);
  }
  
  # ------ execute()
  
  const public.execute := function (node,req,wait_reply=T)
  {
    wider self,public;
    rec := self.makenodespec(node);
    rec.request := req;
    return public.meq('Node.Execute',rec,wait_reply=wait_reply);
  }
  
  # ------ track_results()
  # enables or disables automatic printing of node_result events
  # note that if a meqserver is constructed with verbose>0, tracking
  # will be enabled by default
  
  const public.track_results := function (enable=T)
  {
    wider self,public;
    if( enable )
    {
      self.dprint(2,'auto-printing all node_result events');
      # if already executed a whenever, activate it
      if( has_field(self,'weid_print_results') )
        activate self.weid_print_results;
      else
      {
        whenever self.relay->node_result do
        {
          print '============= result for node: ',$value.name;
#          margin_print($value);
          for( s in rec2lines($value,76) )
            print sprintf('  %-76.76s',s);
        }
        # store id of this wheever
        self.weid_print_results := last_whenever_executed();
      }
    }
    else  # disable
    {
      self.dprint(2,'disabling auto-printing of node_result events');
      deactivate self.weid_print_results;
    }
    return T;
  }
  
  if( verbose>0 )
  {
    self.dprint(1,'verbose>0: auto-enabling node_result output');
    public.track_results(T);
    self.dprint(1,'you can disable this by calling .track_results(F)');
  }
  
  
  return ref public;
}

                      
# inits a meqserver
const default_meqserver := function (verbose=3,debug=[=],gui=F)
{
  global _default_mqs;
  if( !is_record(_default_mqs) )
  {
    _default_mqs := meq.server(verbose=verbose,options="-d0 -nogw -meq:M:O:MeqServer",gui=gui);
    if( is_fail(_default_mqs) )
      fail;
    _default_mqs.init([output_col="PREDICT"],wait=T);
    if( !( is_boolean(debug) && !debug ) )
    {
      for( lev in field_names(default_meq_debuglevels) )
        _default_mqs.setdebug(lev,default_meq_debuglevels[lev]);
      if( is_record(debug) )
        for( lev in field_names(debug) )
          _default_mqs.setdebug(lev,debug[lev]);
    }
  }
  return ref _default_mqs;
}


