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
  
#-- setup shortcuts to dmi methods

const meq.list  := dmi.list;
const meq.add_list := dmi.add_list;
const meq.merge_list := dmi.merge_list;
const meq.field := dmi.field;
  
#-- meq.domain_ndim(), domain_axes()---------------------------------------------
# Basic constants specifying layout of domain and cells

const meq._axis_ids  := [ hiid('freq'),hiid('time') ];
const meq._axis_nums := [ freq=0,time=1 ];

#-- meq.set_axes() -------------------------------------------------------------
# Sets list of active axes
const meq.set_axes := function (axes="freq time")
{
  meq._axis_ids   := "";
  meq._axis_nums  := [=];
  for( a in axes ) 
  {
    meq._axis_ids := [ meq._axis_ids,hiid(a) ];
    meq._axis_nums[a] := len(meq._axis_ids);
  }
  return meq._axis_ids;
}

#-- meq.axis_num() -------------------------------------------------------------
# Resolves its arguments (axis id or numbers) to axis numbers
const meq.axis_num := function (ids)
{
  out := [];
  for( id in ids )
  {
    if( is_string(id) )
      out[len(out)] := meq._axis_nums[id];
    else if( is_integer(id) )
      out[len(out)] := id;
    else
      fail 'unknown type for axis id';
  }
  return out;
}

#-- meq.axis_id() -------------------------------------------------------------
# Resolves its arguments (axis id or numbers) to axis id
const meq.axis_id := function (ids)
{
  out := [];
  for( id in ids )
  {
    if( is_string(id) )
      out[len(out)] := id;
    else if( is_integer(id) )
      out[len(out)] := meq._axis_ids[id];
    else
      fail 'unknown type for axis id';
  }
  return out;
}

#-- meq.node() -------------------------------------------------------------
# Creates a basic defrec for a node

const meq.node := function (class,name,extra=[=],children=F,default=[=],groups="")
{
  defrec := [ class=class,name=name ];
  if( !is_boolean(children) )
    defrec.children := children;
  # group field: convert to hiid implicitly
  if( len(groups) )
    defrec.node_groups := dmi.hiid_list(groups);
  if( len(extra) )
    for( f in field_names(extra) )
      defrec[f] := extra[f];
  return defrec;
}


#-- meq.polc() -------------------------------------------------------------
# Creates a Polc object
# Axes may be specified by name or index

const meq.polc := function (coeff,axis=[],offset=[],scale=[],
                            domain=F,pert=F,weight=F,dbid=F)
{
  rank := len(shape(coeff));
  if( rank>2 )
    fail 'polc rank too high';
  # single coeff is rank 0
  if( rank == 1 && len(coeff) == 1 )
    rank := 0;
  # setup basic record 
  rec := [ coeff=as_double(coeff) ];
  # optional attributes
  if( !is_boolean(pert) )
    rec.pert := pert;
  if( !is_boolean(weight) )
    rec.weight := weight;
  if( !is_boolean(dbid) )
    rec.dbid := dbid;
  # add optional fields for rank>0
  if( rank>0 )
  {
    if( len(axis) )
      rec.axis_index := meq.axis_num(axis[1:rank]);
    if( len(offset) )
      rec.offset := offset[1:rank];
    if( len(scale) )
      rec.scale := scale[1:rank];
  }    
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
# creates a Meq::Domain 
# Two ways of calling it are:
# 1. (Backwards compatible with old freq/time domains);
#    supply four arguments: freq1 freq2 time1 time2 for a freq/time domain
# 2. Supply arrays axis,start,end (all of same size) to create a general
#    domain. Axes may be specified by name or index.

const meq.domain := function (startfreq=[],endfreq=[],starttime=[],endtime=[],
            axis=[],start=[],end=[])
{
  # old calling convention:
  if( !len(axis) )
  {
    rec := [ freq=as_double([startfreq,endfreq]),
             time=as_double([starttime,endtime]) ];
  }
  # new style
  else
  {
    rec := [=];
    for( i in 1:len(axis) )
      rec[meq.axis_id(axis[i])] := as_double([start[i],end[i]]);
  }
  # setup various attributes
  const rec::dmi_actual_type := 'MeqDomain';
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
# As in the case of domain, there's two styles of calling it: the old style
# for freq/time cells, and the new style for generalized cells/domains:
# I. Old style calls take two forms:
#     meq.cells(domain,num_freq,num_time) 
#           creates regularly-spaced cells over
#           the given domain (domain must define freq/time)
#     meq.cells(freq_grid=[...],time_grid=[...]) 
#           creates cells with an explicitly specified grid
#   The two forms may be combined, e.g.:
#     meq.cells(domain,num_freq,time_grid=[...]) creates cells with regular freq
#           sampling, and an explicitly specified time grid
#   The optional freq_cell_size and time_cell_size arguments may be given to 
#   specify cell sizes (default is full tiling). Use either a scalar for 
#   uniform cell size, or a vector of the same length as the grid.
# II. New-style calls for generalized cells/domains:
#   meq.cells(domain,num=[...])
#           creates regularly-spaced cells over the given domain. Domain
#           must have the sume number of axes as there are elements in num.
#   meq.cells(axis=[...],grid=[...])
#           explicitly specified axes (as numbers or ids) and grid points.
#           grid is a record of vectors, must have the same number of vectors
#           in it as there are elements in axis. Domain is computed 
#           automatically as the envelope domain.
#   For both forms, an optional cellsize argument may specify cell size
#   (default is full tiling). Use either a vector of scalars (for uniform size),
#   or a record of vectors to specify the size at each grid point.
# Note that the old style may also be called directly as meq.cells_ft(),
# and the new style as meq.cellsx(). In fact, this function simply calls
# one or the other depending on which arguments are specified.
const meq.cells := function (domain=F,
                                # arguments for old-style calls
                             num_freq=F,num_time=F,
                             freq_grid=[],time_grid=[],
                             freq_cell_size=[],time_cell_size=[],
                                # arguments for new-style calls
                             axis=[],num=[],grid=[=],cell_size=[])
{
  if( !len(axis) && !len(num) )
    return meq.cells_ft(domain,num_freq,num_time,freq_grid,time_grid,
                        freq_cell_size,time_cell_size);
  else  
    return meq.cellsx(domain,axis,ncells,grid,cellsize);
}

const meq.cells_ft := function (domain=F,
                                num_freq=F,num_time=F,
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
  return rec;
}

const meq.cellsx := function (domain=F,axis=[],num=[],grid=[=],cell_size=[])
{  
  # build up list of ranges, and vector of axes
  rng := [=];
  axis_id := [];
  # either from domain...
  if( is_dmi_type(domain,'MeqDomain') )
  {
    if( len(axis) )
      fail 'meq.cells() must specify either domain or axis array, not both';
    # build up list of ranges, and vector of axes
    for( a in field_names(domain) )
    {
      rng[len(rng)] := domain[a];
      axis_id[len(axis_id)] := meq.axis_id(a);
    }
  } # or from axis argument...
  else
  {
    if( !len(axis) )
      fail 'meq.cells() must specify either domain or axis array';
    # build up empty list of ranges
    for( i in 1:len(axis) )
    {
      axis_id[i] := meq.axis_id(axis[i]);
      rng[i] := F;
    }
  }
  rec := [ grid=[=],cell_size=[=],segments=[=] ];
  domstart := [];
  domend := [];
  # now, figure out each grid/range based on other arguments
  for( i in 1:len(axis_id) )
  {
    a := axis_id[i];
    # convert everything to double
    if( i <= len(num) )
      np := num[i];
    else
      np := F;
    if( i <= len(grid) )
      gr := as_double(grid[i]);
    else
      gr := [];
    if( i <= len(cell_size) )
      csz := as_double(csz[i]);
    else
      csz := [];
    # resolve grids
    np := meq_private.resolve_grid(a,rng[i],np,gr,csz,segs);
    if( is_fail(np) )
      fail;
    # create record
    rec.grid[a] := gr;
    rec.cell_size[a] := csz;
    rec.segments[a] := segs;
    # remember domain start/end
    domstart[i] := rng[i][1];
    domend[i] := rng[i][2];
  }
  rec.domain := meq.domain(axis=axis_id,start=domstart,end=domend);
  const rec::dmi_actual_type := 'MeqCells';
  return rec;
}

#-- meq_private.merge_records()  ------------------------------------------------
# private helper function to merge command records
const meq_private.merge_records := function (ref rec,command,value)
{
  if( is_string(command) )
    rec[command] := value;
  else if( is_record(command) )
    for( f in field_names(command) )
      rec[f] := command[f];
  else
    fail 'command argument must be string or record';
}

#-- meq_private.makecmdrec() -------------------------------------------------------------
# forms a command record from a node spec and a command 
const meq_private.make_cmd_rec := function (node,command,value=T)
{
  local cmd;
  # resolve command argument - can be string or record
  if( is_string(command) )
  {
    cmd := [=];
    cmd[command] := value;
  }
  else if( is_record(command) )
    cmd := command;
  else
    fail 'command argument must be string or record';
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
  return cmd;
}

# This maps request ID components onto positions in the request ID and bits
# in the depmask (starting from ID end = bit 0).
# The default settings here should correspond to MEQ/RequestId.h.
# Note that some applications may redefine the mappings (see symdeps),
# in which case they just have to provide their own.
const meq._rqid_mapping := [ value=1,resolution=2,domain=5,dataset=6 ];
const meq._rqid_maxlen := 16;

#-- meq.rqid() -------------------------------------------------------------
# Creates a request ID
# With no arguments, creates a null ID
const meq.rqid := function(domain=-1,dataset=0,resolution=0,value=0,
                           mapping=meq._rqid_mapping)
{ 
  if( domain<0 )
    return hiid('');
  # create array of indices and insert arguments at appropriate positions
  rqid := array(0,meq._rqid_maxlen);
  n := len(rqid)+1;
  rqid[n-mapping.domain] := domain;
  rqid[n-mapping.dataset] := dataset;
  rqid[n-mapping.resolution] := resolution;
  rqid[n-mapping.value] := value;
  # find first non-zero element
  i0 := 1;
  while( !rqid[i0] && i0<len(rqid) )
    i0+:=1;
  s := as_string(rqid[i0]);
  while( i0<len(rqid) )
    s := spaste(s,'.',rqid[i0+:=1]);
  # create hiid
  return hiid(s);
}

#-- meq.request() -------------------------------------------------------------
# creates a request
const meq.request := function (cells=F,rqid=F,calc_deriv=0)
{
  global _meqdomain_id;
  # if no request ID supplied, generate one by incrementing the
  # global domain ID. 
  if( is_boolean(rqid) )
    rqid := meq.rqid(_meqdomain_id+:=1);
  req := [ request_id=hiid(rqid),
           calc_deriv=as_integer(calc_deriv) ];
  if( !is_boolean(cells) )
    req.cells := cells;
  req::dmi_actual_type := 'MeqRequest';
  
  return ref req;
}

#-- meq.node_spec() -------------------------------------------------------------
# given a 'node' argument, adds it to spec record as 'name' or 'nodeindex',
# depending on type. This is a common paradigm for specifying nodes.
# Optional spec argument may be used to update an existing record; if not
# given, a new record is returned.
const meq.node_spec := function (node,ref spec=[=])
{
  if( is_integer(node) )
    spec.nodeindex := node;
  else if( is_string(node) )
    spec.name := node;
  else 
    fail 'node must be specified by index or name';
  return ref spec;
}

#-- meq.add_command() -------------------------------------------------------------
# adds a command to a request rider
# req:    request to add command to (passed in by ref)
# group:  this is the node group that the command is targeted at. Only
#         nodes belonging to this group will be checked. Use 'all' for
#         all nodes (NB: the 'all' group may be phased out in the future)
# node:   specifies the target node. Four options are available:
#         (a) empty scalar array (i.e. '[]'): targets command at all nodes   
#             (adds it to the command_all list of the rider)
#         (b) single integer: assumes this is a node index
#             (adds command to the command_by_nodeindex map)
#         (c) vector of integers: assumes these are node indices
#             (adds command to command_by_list, with a nodeindex key)
#         (d) one or more strings: assumes node names
#             (adds command to command_by_list, with a name key)
#         (e) empty string array (""): adds a wildcard entry to 
#             command_by_list, which will match all nodes not matched
#             by a previous entry.
# command: string command (used as field name in the maps), or a command 
#         record. If a string is used, then the record is extended with 
#         field command=value. If a record is used, then value is ignored.
const meq.add_command := function (ref req,group,node,command,value=T)
{
  # add node_state and group subrecord
  if( !has_field(req,'rider') )
    req.rider := [=];
  if( !has_field(req.rider,group) )
    req.rider[group] := [=];
  ns := ref req.rider[group];
  if( !is_integer(node) && !is_string(node) )
    fail 'node must be specified by index or name(s)';
  # empty node argument: add to command_all list
  if( len(node) == 0 )
  {
    if( !has_field(ns,'command_all') )
      ns.command_all := [=];
    mqs_private.merge_records(ns.command_all,command,value);
  }
  # single nodeindex: add to command_by_nodeindex map
  else if( is_integer(node) && len(node)==1 ) 
  {
    if( !has_field(ns,'command_by_nodeindex') )
      ns.command_by_nodeindex := [=];
    key := spaste('#',as_string(node));
    if( !has_field(ns.command_by_nodeindex,key) )
      ns.command_by_nodeindex[key] := [=];
    mqs_private.merge_records(ns.command_by_nodeindex[key],command,value);
  }
  else # multiple indices or names: add to command_by_list map
  {
    local cmdrec;
    # resolve command argument - can be string or record
    if( is_string(command) )
    {
      cmdrec := [=];
      cmdrec[command] := value;
    }
    else if( is_record(command) )
      cmdrec := command;
    else
      fail 'command argument must be string or record';
    # zero-length node is wildcard; otherwise add node spec to record
    if( len(node) )
      cmdrec := meq.node_spec(node,cmdrec);
    # create new list or add to end of existing list
    if( !has_field(ns,'command_by_list') )
      ns.command_by_list := dmi.list(cmdrec);
    else
      dmi.add_list(ns.command_by_list,cmd);
  }
  return T;
}

#-- meq.add_state() -------------------------------------------------------------
# shortcut for adding state change command to a request rider

const meq.add_state := function (ref req,group,node,state)
{
  return add_command(req,group,node,'state',state);
}


#-- meq.solvable_list() -------------------------------------------------------------
# creates a command list to set the named parms solvable

const meq.solvable_list := function (names)
{
  return [ command_by_list = dmi.list([name=names,state=[solvable=T]],
                      [state=[solvable=F]]) ];
}
