### meqtypes.g: defines Glish counterpats to various MEQ classes
###
### Copyright (C) 2002
### ASTRON (Netherlands Foundation for Research in Astronomy)
### P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; either version 2 of the License, or
### (at your option) any later version.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
### $Id$

pragma include once

include 'dmitypes.g'

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

# init global namespaces meq and meq_test
if( !is_record(meq) )
  meq := [=];
if( !is_record(meq_test) )
  meq_test := [=];


# Creates a request ID

const meq.requestid := function(domain_id,config_id=0,iter_id=0)
{ 
  return hiid(domain_id,config_id,iter_id);
}


# Creates a basic defrec for a node

const meq.node := function (class,name,children=F,default=[=],groups="")
{
  defrec := [ class=class,name=name ];
  if( !is_boolean(children) )
    defrec.children := children;
  if( len(groups) )
    defrec.node_groups := hiid(groups);
  return defrec;
}


# Creates a Polc

const meq.polc := function (coeff,freq0=0,freqsc=1,time0=0,timesc=1,pert=1e-6,
                           scale=F,weight=1,domain=F,dbid=-1)
{
  if( is_boolean(scale) )
    scale := [freq0,freqsc,time0,timesc];
  rec := [ freq_0=scale[1],freq_scale=scale[2],
           time_0=scale[3],time_scale=scale[4],
           pert=pert,weight=weight,dbid_index=dbid ];
  # set coeff  
  if( len(coeff) == 1 )
    rec.coeff := array(as_double(coeff),1,1);
  else if( !has_field(coeff::,'shape') || len(coeff::shape) != 2 )
    fail 'meq.polc: coeff must be either scalar or a 2D array';
  else
    rec.coeff := as_double(coeff);
  # set domain if specified
  if( !is_boolean(domain) )
  {
    if( !is_dmi_type(domain,'MeqDomain') )
      fail 'meq.polc: domain argument must be a meq.domain';
    rec.domain := domain;
  }
  rec::dmi_actual_type := 'MeqPolc';
  return rec;
}


# Creates a Parm defrec

const meq.parm := function (name,default=F,polc=F,groups="")
{
  rec := meq.node('MeqParm',name,groups=groups);
  # set default if specified
  if( !is_boolean(default) )
  {
    if( !is_dmi_type(default,'MeqPolc') )
      default := meq.polc(default);
    rec.default := default;
  }
  # set polcs if specified
  if( is_record(polc) )
  {
    if( is_dmi_type(polc,'MeqPolc') ) # single polc
      rec.polcs := polc;
    else
    {
      for( i in 1:len(polc) )  # else must be a vector of polcs
      {
        if( !is_dmi_type(polc[i],'MeqPolc') )
          fail 'meq.parm: polc argument must be a meq.polc or a vector of meqpolcs';
      }
      rec.polcs := polc;
      rec.polcs::dmi_datafield_content_type := 'MeqPolc';
    }
  }
  return rec;
}


# Creates a Meq::Domain

const meq.domain := function (startfreq,endfreq,starttime,endtime)
{
  domain := as_double([startfreq,endfreq,starttime,endtime]);
  domain::dmi_datafield_content_type := 'double';
  domain::dmi_actual_type  := 'MeqDomain';
  return domain;
}


# Creates a Meq::Cells
# Two options are available:
#   meq.cells(domain,nf,nt) creates regularly-spaced cells
#   meq.cells(domain,nf,times=[...],time_steps=[...]) creates cells with
#               explicit time sampling

const meq.cells := function (domain,num_freq,num_time=F,times=F,time_steps=F)
{
  if( !is_dmi_type(domain,'MeqDomain') )
    fail 'domain argument must be a meq.domain object';
  if( is_integer(num_time) )
  {
    dt := (domain[4]-domain[3])/num_time;
    times := domain[3] + ((1:num_time)-0.5)*dt;
    time_steps := array(dt,num_time);
  }
  rec := [ domain=domain,num_freq=as_integer(num_freq),
           times=as_double(times),
           time_steps=as_double(time_steps) ];
  rec::dmi_actual_type := 'MeqCells';
  return rec;
}



# Creates a record list from its arguments.
# A record list is turned into a DataField of DataRecords on the C++ side.
# Arguments may be records or record lists; all arguments are concatenated 
# into a single list.
# If called with no arguments, returns an empty list.

const meq.reclist := function (...)
{
  list := [=];
  list::dmi_datafield_content_type := 'DataRecord';
  list::dmi_is_reclist := T;
  for( i in 1:num_args(...) )
  {
    arg := nth_arg(i,...);
    if( !is_record(arg) )
      fail 'meq.reclist(): arguments must be records';
    # if argument is a reclist, merge wtih list
    if( arg::dmi_is_reclist )
    {
      for( j in 1:len(arg) )
        list[spaste('#',len(list)+1)] := arg[j];
    }
    else # else add to list
    {
      list[spaste('#',len(list)+1)] := arg;
    }
  }
  return list;
}


# creates a command list for inclusion in a request

const meq.initcmdlist := function ()
{
  return meq.reclist();
}



# adds to a command list 

const meq.addcmdlist := function (ref cmdlist,node,command,value=F)
{
  if( !is_record(cmdlist) || !cmdlist::dmi_is_reclist )
    cmdlist := meq.reclist();
  cmd := [=];
  cmd[command] := value;
  # zero-length node is wildcard
  if( len(node) )
  {
    if( is_integer(node) )
      cmd.nodeindex := node;
    else if( is_string(node) )
      cmd.name := node;
    else 
      fail 'node must be specified by index or name';
  }
  cmdlist[spaste('#',len(cmdlist)+1)] := cmd;
  return ref cmdlist;
}

# creates a request
const meq.request := function (cells=F,request_id=F,calc_deriv=0)
{
  global _meqdomain_id;
  # if no request ID supplied, generate one by incrementing the
  # global domain ID. 
  if( is_boolean(request_id) )
    request_id := meq.requestid(_meqdomain_id+:=1);
  else  # else, setup global domain ID from the one given in the request ID
    _meqdomain_id := as_integer(as_string(request_id) ~ s/\..*$//);
  rec := [ request_id=hiid(request_id),
           calc_deriv=as_integer(calc_deriv) ];
  if( !is_boolean(cells) )
    rec.cells := cells;
  rec::dmi_actual_type := 'MeqRequest';

  # adds a command to the request
  const rec.add_command := function (group,node,command,value=F)
  {
    wider rec;
    # add node_state and group subrecord
    if( !has_field(rec,'rider') )
      rec.rider := [=];
    if( !has_field(rec.rider,group) )
      rec.rider[group] := [=];
    ns := ref rec.rider[group];
    if( !is_integer(node) && !is_string(node) )
      fail 'meq.request.add_command(): node must be specified by index or name(s)';
    # single nodeindex: add to command_by_nodeindex map
    if( is_integer(node) && len(node)==1 ) 
    {
      if( !has_field(ns,'command_by_nodeindex') )
        ns.command_by_nodeindex := [=];
      key := spaste('#',as_string(node));
      if( !has_field(ns.command_by_nodeindex,key) )
        ns.command_by_nodeindex[key] := [=];
      ns.command_by_nodeindex[key][command] := value;
    }
    else # multiple indices or names: add to command_by_list map
    {
      if( !has_field(ns,'command_by_list') )
        ns.command_by_list := meq.initcmdlist();
      meq.addcmdlist(ns.command_by_list,node,command,value);
    }
    return T;
  }
  # shortcut for adding state changes
  const rec.add_state := function (group,node,state)
  {
    wider rec;
    return rec.add_command(group,node,'state',state);
  }
  
  rec.add_command::dmi_ignore := T;
  rec.add_state::dmi_ignore := T;
  
  return ref rec;
}


# creates a command list to set the names parms solvable

const meq.solvable_list := function (names)
{
  return [ command_by_list=
            meq.reclist([name=names,state=[solvable=T]],
                        [state=[solvable=F]]) ];
}
