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
if( !is_record(meq_private) )
  meq_private := [=];

#-- meq.requestid() -------------------------------------------------------------
# Creates a request ID

const meq.requestid := function(domain_id,config_id=0,iter_id=0)
{ 
  return hiid(domain_id,config_id,iter_id);
}


#-- meq.node() -------------------------------------------------------------
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


#-- meq.polc() -------------------------------------------------------------
# Creates a Polc object

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
  const rec::dmi_actual_type := 'MeqPolc';
  return rec;
}


#-- meq.parm() -------------------------------------------------------------
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
    {
      rec.polcs := [=];
      rec.polcs['#1'] := polc;
    }
    else
    {
      for( i in 1:len(polc) )  # else must be a vector of polcs
      {
        if( !is_dmi_type(polc[i],'MeqPolc') )
          fail 'meq.parm: polc argument must be a meq.polc or a vector of meqpolcs';
      }
      rec.polcs := polc;
    }
    const rec.polcs::dmi_datafield_content_type := 'MeqPolc';
  }
  return rec;
}


#-- meq.domain() -------------------------------------------------------------
# creates a Meq::Domain from starting/ending freq and time

const meq.domain := function (startfreq,endfreq,starttime,endtime)
{
  rec := [ freq=as_double([startfreq,endfreq]),
           time=as_double([starttime,endtime]) ];
  # setup various attributes
  const rec::dmi_actual_type := 'MeqDomain';
  const rec::meq_axes := "freq time";
  const rec.ndim := function () 
  { return 2; }
  const rec.axes := function () 
  { return "freq time"; }
  return rec;
}


#-- meq_private.resolve_grid() -----------------------------------------------
# helper function to resolve a meq.cells grid for one axis

const meq_private.resolve_grid := function (type,dom,num,
                                    ref grid,ref cellsize,ref segs) 
{
  if( len(grid) )
  {
    if( is_integer(num) && num != len(grid) )
      fail spaste('both num_',type,' and ',type,'_grid specified and are inconsistent');
    num := len(grid);
    # figure out segments
    if( num<3 ) # 1 or 2 grid points: always regular
      val segs := [ start_index=1,end_index=num ];
    else # >2 grid points: check for regularity
    {
      val segs := [ start_index=1,end_index=2 ];
      cur_step := grid[2]-grid[1];
      for( i in 3:num )
      {
        dx := grid[i] - grid[i-1];
        if( !is_boolean(cur_step) && dx != cur_step )  # start new segment if new step
        {
          cur_step := F;
          segs.start_index := [segs.start_index,i];
          segs.end_index   := [segs.end_index,i];
        }
        else # else extend current segment
        {
          cur_step := dx;
          segs.end_index[len(segs.end_index)] := i;
        }
      }
    }
  }
  else if( is_integer(num) )
  {
    if( num <= 0 )
      fail spaste('illegal num_',type,' argument');
    if( is_boolean(dom) )
      fail spaste('domain must be specified if ',type,'_grid is not');
    step := (dom[2]-dom[1])/num;
    val grid := dom[1] + ((1:num)-0.5)*step;
    # set cell size if not specified
    if( !len(cellsize) )
      val cellsize := array(step,num);
    # just 1 regular segment
    val segs := [ start_index=1,end_index=num ];
  }
  else
    fail spaste('either num_',type,' or ',type,'_grid must be specified');
  # resolve cell size if not specified
  # use distance to nearest grid point as the cell size
  if( !len(cellsize) )
  {
    val cellsize := array(0.,num);
    if( num > 1 )
    {
      x := [ 2*grid[1]-grid[2],grid,2*grid[num]-grid[num-1] ];
      d1 := grid - x[1:num];
      d2 := x[3:(num+2)] - grid;
      for( i in 1:num )
        cellsize[i] := min(d1[i],d2[i])
    }
  }
  # scalar specified: use uniform cell size
  else if( len(cellsize) == 1 )
    val cellsize := array(cellsize,num);
  # vector specified: check length
  else if( len(cellsize) != num )
    fail spaste('length of ',type,'_cell_size does not conform to grid');
  return num;
}

#-- meq.cells() -------------------------------------------------------------
# Creates a Meq::Cells
# Two forms of constructor are available:
#   meq.cells(domain,num_freq,num_time) creates regularly-spaced cells over
#         the given domain
#   meq.cells(freq_grid=[...],time_grid=[...]) creates cells with an explicitly
#         specified grid
# The forms may be combined, e.g.:
#   meq.cells(domain,num_freq,time_grid=[...]) creates cells with regular freq
#         sampling, and an explicitly specified time grid
# The optional freq_cell_size and time_cell_size arguments may be given to 
# specify cell sizes (default is full tiling). Use either a scalar for 
# uniform cell size, or a vector of the same length as the grid.

const meq.cells := function (domain=F,num_freq=F,num_time=F,
                             freq_grid=[],time_grid=[],
                             freq_cell_size=[],time_cell_size=[])
{
  if( is_dmi_type(domain,'MeqDomain') )
  {
    df := domain.freq;
    dt := domain.time;
  }
  else
    df := dt := F;
  # convert everything to double
  freq_grid := as_double(freq_grid);
  time_grid := as_double(time_grid);
  freq_cell_size := as_double(freq_cell_size);
  time_cell_size := as_double(time_cell_size);
  # resolve grids
  nf := meq_private.resolve_grid('freq',df,num_freq,freq_grid,freq_cell_size,fs);
  if( is_fail(nf) )
    fail;
  nt := meq_private.resolve_grid('time',dt,num_time,time_grid,time_cell_size,ts);
  if( is_fail(nt) )
    fail;
  # create record
  rec := [ domain     = meq.domain(df[1],df[2],dt[1],dt[2]),
           grid       = [ freq=freq_grid,     time=time_grid],
           cell_size  = [ freq=freq_cell_size,time=time_cell_size],
           segments   = [ freq=fs,            time=ts] ];
  # setup various attributes
  const rec::dmi_actual_type := 'MeqCells';
  const rec::meq_axes := "freq time";
  const rec.ndim := function () 
  { return 2; }
  const rec.axes := function () 
  { return "freq time"; }
  return rec;
}

#-- meq.reclist() -------------------------------------------------------------
# Creates a record list from its arguments.
# A record list is turned into a DataField of DataRecords on the C++ side.
# Arguments may be records or record lists; all arguments are concatenated 
# into a single list.
# If called with no arguments, returns an empty list.

const meq.reclist := function (...)
{
  list := [=];
  const list::dmi_datafield_content_type := 'DataRecord';
  const list::dmi_is_reclist := T;
  if( num_args(...) )
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


#-- meq.initcmdlist() -------------------------------------------------------------
# creates a command list for inclusion in a request

const meq.initcmdlist := function ()
{
  return meq.reclist();
}



#-- meq.addcmdlist() -------------------------------------------------------------
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

#-- meq.request() -------------------------------------------------------------
# creates a request

const meq.request := function (cells=F,request_id=F,calc_deriv=0,clear_solver=T)
{
  global _meqdomain_id;
  # if no request ID supplied, generate one by incrementing the
  # global domain ID. 
  if( is_boolean(request_id) )
    request_id := meq.requestid(_meqdomain_id+:=1);
  else  # else, setup global domain ID from the one given in the request ID
    _meqdomain_id := as_integer(as_string(request_id) ~ s/\..*$//);
  rec := [ request_id=hiid(request_id),
           calc_deriv=as_integer(calc_deriv),
           clear_solver=as_boolean(clear_solver) ];
  if( !is_boolean(cells) )
    rec.cells := cells;
  rec::dmi_actual_type := 'MeqRequest';

  #-- meq.request.add_command() -------------------------------------------------------------
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
  
  #-- meq.request.add_state() -------------------------------------------------------------
  # shortcut for adding state change commands
  
  const rec.add_state := function (group,node,state)
  {
    wider rec;
    return rec.add_command(group,node,'state',state);
  }
  
  rec.add_command::dmi_ignore := T;
  rec.add_state::dmi_ignore := T;
  
  return ref rec;
}


#-- meq.solvable_list() -------------------------------------------------------------
# creates a command list to set the names parms solvable

const meq.solvable_list := function (names)
{
  return [ command_by_list=
            meq.reclist([name=names,state=[solvable=T]],
                        [state=[solvable=F]]) ];
}
