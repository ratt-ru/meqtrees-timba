#!/usr/bin/python

from dmitypes import *

domain_ndim = 2;
domain_axes = ( "freq","time" );

def node (classname,name,children=None,groups=None,**kwargs):
  "creates a node record";
  rec = srecord({'class':classname},name=name,**kwargs);
  if children:
    if not isinstance(children,(list,tuple)):
      children = (children,);
    self.children = children;
  if groups:
    self.node_groups = make_hiid_list(groups);
  return rec;
  
def polc (coeff,freq0=0,freqsc=1,time0=0,timesc=1,pert=1e-6,
          scale=None,weight=1,domain=None,dbid=-1):
  "creates a polc record";
  if scale is None:  # scale supplied as seq of four numbers, or explicitly
    scale = ( freq0,freqsc,time0,timesc );
  rec = srecord(freq_0=scale[0],freq_scale=scale[1],
                time_0=scale[2],time_scale=scale[3],
                pert=pert,weight=weight,dbid_index=dbid);
  # process coeff argument -- force into a 2D array
  if is_scalar(coeff):
    if not isinstance(coeff,complex):  # force float or complex
      coeff = float(coeff);
    rec.coeff = array(coeff,shape=(1,1));
  elif is_array(coeff) and len(coeff.getshape()) == 2:
    if coeff.type() in (arr_double,arr_dcomplex):
      rec.coeff = coeff;
    else:
      raise TypeError,'coeff array must be float (Float64) or dcomplex (Complex64)';
  else:
    raise TypeError,'coeff argument must be a scalar or a rank-2 array';
  # process domain argument
  if domain is not None:
    if dmi_type(domain) == 'MeqDomain':
      rec.domain = domain;
    else:
      raise TypeError,'domain argument must be a meq.domain() object';
  # set attr
  rec.__dmi_type = 'MeqPolc';
  return rec;
  
def make_polc (p):
  if dmi_type(p) == 'MeqPolc':
    return p;
  elif is_scalar(p) or is_array(p):
    return polc(p);
  else:
    raise TypeError,'cannot convert %s to a meq.polc'%type(p);

def parm (name,default=None,polcs=None,*args,**kwargs):
  rec = node('MeqParm',name,*args,**kwargs);
  # default must be a polc
  if default is not None:
    rec.default = make_polc(default);
  # polcs must be a list of polcs, or a single polc
  if polcs is not None:
    if isinstance(polcs,(list,tuple)):
      rec.polcs = map(make_polc,polcs);
    else:
      rec.polcs = ( make_polc(polcs), );
  return rec;
    
def domain (startfreq,endfreq,starttime,endtime):
  rec = srecord(freq=map(float,(startfreq,endfreq)),
                time=map(float,(starttime,endtime)));
  rec.__dmi_type = 'MeqDomain';
  return rec;
  
# helper function to resolve a meq.cells grid for one axis
# returns (grid,cellsize,segs) tuple
def _resolve_grid (axisname,dom,num,grid,cellsize):
  # first, figure out grid
  # (a) grid specified explicitly
  if grid is not None and len(grid):
    if grid.rank != 1:
      raise TypeError,'%s_grid must be a vector'%axisname;
    if num is not None and num != len(grid):
      raise ValueError,'both num_%s and %s_grid specified but do not match'%(axisname,axisname);
    num = len(grid);
    # figure out segments
    if num<3:  # <=2 points: always regular
      segs = srecord(start_index=0,end_index=num-1);
    else:      # >2 grid points: check for regularity
      segs = srecord(start_index=[0],end_index=[1]);
      cur_step = grid[1]-grid[0];
      for i in range(2,num-1):
        dx = grid[i] - grid[i-1];
        if cur_step is not None and dx != cur_step: # start new segment if new step
          cur_step = None;
          segs.start_index.append(i);
          segs.end_index.append(i);
        else: # else extend current segment
          cur_step = dx;
          segs.end_index[-1] = i;  # update end of current segment
  # (b) num is specified
  elif num is not None:
    if num <= 0:
      raise ValueError,'illegal num_%s value'%axisname;
    if dom is None:
      raise ValueError,'domain must be specified to use num_%s'%axisname;
    step = (dom[1]-dom[0])/num;
    grid = dom[1] + (numarray.arange(num)+0.5)*step;
    # set cell size if not specified
    if cellsize is None or not len(cellsize):
      cellsize = numarray.zeros([num],arr_double) + step;
    segs = srecord(start_index=0,end_index=num-1);
  else:
    raise ValueError,'either num_%s or %s_grid must be specified'%(axisname,axisname);
  # resolve cell size if not specified
  # use distance to nearest grid point as the cell size
  if cellsize is None or not len(cellsize):
    cellsize = numarray.zeros([num],arr_double);
    x = array([ 2*grid[0]-grid[1]] + grid.getflat() + [2*grid[-1]-grid[-2]]);
    d1 = grid - x[:-2];
    d2 = x[2:] - grid;
    for i in range(num):
      cellsize[i] = min(d1[i],d2[i]);
  elif len(cellsize) == 1:
    cellsize = numarray.zeros([num],arr_double) + cellsize[0];
  elif len(cellsize) != num:
    raise ValueError,'length of %s_cell_size does not conform to grid shape'%axisname;
  return (grid,cellsize,segs);
  
  
# #-- meq.cells() -------------------------------------------------------------
# # Creates a Meq::Cells
# # Two forms of constructor are available:
# #   meq.cells(domain,num_freq,num_time) creates regularly-spaced cells over
# #         the given domain
# #   meq.cells(freq_grid=[...],time_grid=[...]) creates cells with an explicitly
# #         specified grid
# # The forms may be combined, e.g.:
# #   meq.cells(domain,num_freq,time_grid=[...]) creates cells with regular freq
# #         sampling, and an explicitly specified time grid
# # The optional freq_cell_size and time_cell_size arguments may be given to 
# # specify cell sizes (default is full tiling). Use either a scalar for 
# # uniform cell size, or a vector of the same length as the grid.
#
def cells(domain=None,num_freq=None,num_time=None,
          freq_grid=[],time_grid=[],
          freq_cell_size=[],time_cell_size=[]):
  # decompose domain into axis ranges
  if domain is not None:
    if dmi_type(domain) != 'MeqDomain':
      raise TypeError,'domain argument must be a meq.domain() object';
    df = domain.freq;
    dt = domain.time;
  else:
    df = None;
    dt = None;
  # convert everything to double arrays (possibly empty)
  freq_grid = asarray(freq_grid,arr_double);
  time_grid = asarray(time_grid,arr_double);
  freq_cell_size = asarray(freq_cell_size,arr_double);
  time_cell_size = asarray(time_cell_size,arr_double);
  # resolve grids
  (freq_grid,freq_cell_size,fs) = _resolve_grid(
        'freq',df,num_freq,freq_grid,freq_cell_size);
  (time_grid,time_cell_size,ts) = _resolve_grid(
        'time',dt,num_time,time_grid,time_cell_size);
  # create record
  rec = srecord( domain    = domain(df[1],df[2],dt[1],dt[2]),
                 grid      = srecord(freq=freq_grid,time=time_grid),
                 cell_size = srecord(freq=freq_cell_size,time=time_cell_size),
                 segments  = srecord(freq=fs,time=ts) )
  rec.__dmi_type = 'MeqCells';
  return rec;
  
  
# }
# 
# #-- meq.reclist() -------------------------------------------------------------
# # Creates a record list from its arguments.
# # A record list is turned into a DataField of DataRecords on the C++ side.
# # Arguments may be records or record lists; all arguments are concatenated 
# # into a single list.
# # If called with no arguments, returns an empty list.
# 
# const meq.reclist := function (...)
# {
#   list := [=];
#   const list::dmi_datafield_content_type := 'DataRecord';
#   const list::dmi_is_reclist := T;
#   if( num_args(...) )
#     for( i in 1:num_args(...) )
#     {
#       arg := nth_arg(i,...);
#       if( !is_record(arg) )
#         fail 'meq.reclist(): arguments must be records';
#       # if argument is a reclist, merge wtih list
#       if( arg::dmi_is_reclist )
#       {
#         for( j in 1:len(arg) )
#           list[spaste('#',len(list)+1)] := arg[j];
#       }
#       else # else add to list
#       {
#         list[spaste('#',len(list)+1)] := arg;
#       }
#     }
#   return list;
# }
# 
# 
# #-- meq_private.merge_records()  ------------------------------------------------
# # private helper function to merge command records
# 
# const meq_private.merge_records := function (ref rec,command,value)
# {
#   if( is_string(command) )
#     rec[command] := value;
#   else if( is_record(command) )
#     for( f in field_names(command) )
#       rec[f] := command[f];
#   else
#     fail 'command argument must be string or record';
# }
# 
# #-- meq_private.initcmdlist() -------------------------------------------------------------
# # creates a command list for inclusion in a request
# 
# const meq_private.initcmdlist := function ()
# {
#   return meq.reclist();
# }
# 
# #-- meq_private.addcmdlist() -------------------------------------------------------------
# # adds to a command list 
# 
# const meq_private.addcmdlist := function (ref cmdlist,node,command,value=F)
# {
#   if( !is_record(cmdlist) || !cmdlist::dmi_is_reclist )
#     cmdlist := meq.reclist();
#   local cmd;
#   # resolve command argument
#   if( is_string(command) )
#   {
#     cmd := [=];
#     cmd[command] := value;
#   }
#   else if( is_record(command) )
#     cmd := command;
#   else
#     fail 'command argument must be string or record';
#   # zero-length node is wildcard
#   if( len(node) )
#   {
#     if( is_integer(node) )
#       cmd.nodeindex := node;
#     else if( is_string(node) )
#       cmd.name := node;
#     else 
#       fail 'node must be specified by index or name';
#   }
#   cmdlist[spaste('#',len(cmdlist)+1)] := cmd;
#   return ref cmdlist;
# }
# 
# #-- meq.request() -------------------------------------------------------------
# # creates a request
# 
# const meq.request := function (cells=F,request_id=F,calc_deriv=0)
# {
#   global _meqdomain_id;
#   # if no request ID supplied, generate one by incrementing the
#   # global domain ID. 
#   if( is_boolean(request_id) )
#     request_id := meq.requestid(_meqdomain_id+:=1);
#   else  # else, setup global domain ID from the one given in the request ID
#     _meqdomain_id := as_integer(as_string(request_id) ~ s/\..*$//);
#   req := [ request_id=hiid(request_id),
#            calc_deriv=as_integer(calc_deriv) ];
#   if( !is_boolean(cells) )
#     req.cells := cells;
#   req::dmi_actual_type := 'MeqRequest';
#   
#   return ref req;
# }
# 
# #-- meq.add_command() -------------------------------------------------------------
# # adds a command to a request rider
# # req:    request to add command to (passed in by ref)
# # group:  this is the node group that the command is targeted at. Only
# #         nodes belonging to this group will be checked. Use 'all' for
# #         all nodes (NB: the 'all' group may be phased out in the future)
# # node:   specifies the target node. Four options are available:
# #         (a) empty scalar array (i.e. '[]'): targets command at all nodes   
# #             (adds it to the command_all list of the rider)
# #         (b) single integer: assumes this is a node index
# #             (adds command to the command_by_nodeindex map)
# #         (c) vector of integers: assumes these are node indices
# #             (adds command to command_by_list, with a nodeindex key)
# #         (d) one or more strings: assumes node names
# #             (adds command to command_by_list, with a name key)
# #         (e) empty string array (""): adds a wildcard entry to 
# #             command_by_list, which will match all nodes not matched
# #             by a previous entry.
# # command: string command (used as field name in the maps), or a command 
# #         record. If a string is used, then the record is extended with 
# #         field command=value. If a record is used, then value is ignored.
# const meq.add_command := function (ref req,group,node,command,value=F)
# {
#   # add node_state and group subrecord
#   if( !has_field(req,'rider') )
#     req.rider := [=];
#   if( !has_field(req.rider,group) )
#     req.rider[group] := [=];
#   ns := ref req.rider[group];
#   if( !is_integer(node) && !is_string(node) )
#     fail 'node must be specified by index or name(s)';
#   # empty node argument: add to command_all list
#   if( len(node) == 0 )
#   {
#     if( !has_field(ns,'command_all') )
#       ns.command_all := [=];
#     mqs_private.merge_records(ns.command_all,command,value);
#   }
#   # single nodeindex: add to command_by_nodeindex map
#   else if( is_integer(node) && len(node)==1 ) 
#   {
#     if( !has_field(ns,'command_by_nodeindex') )
#       ns.command_by_nodeindex := [=];
#     key := spaste('#',as_string(node));
#     if( !has_field(ns.command_by_nodeindex,key) )
#       ns.command_by_nodeindex[key] := [=];
#     mqs_private.merge_records(ns.command_by_nodeindex[key],command,value);
#   }
#   else # multiple indices or names: add to command_by_list map
#   {
#     if( !has_field(ns,'command_by_list') )
#       ns.command_by_list := meq_private.initcmdlist();
#     meq_private.addcmdlist(ns.command_by_list,node,command,value);
#   }
#   return T;
# }
# 
# #-- meq.add_state() -------------------------------------------------------------
# # shortcut for adding state change command to a request rider
# 
# const meq.add_state := function (ref req,group,node,state)
# {
#   return add_command(req,group,node,'state',state);
# }
# 
# 
# #-- meq.solvable_list() -------------------------------------------------------------
# # creates a command list to set the names parms solvable
# 
# const meq.solvable_list := function (names)
# {
#   return [ command_by_list=
#             meq.reclist([name=names,state=[solvable=T]],
#                         [state=[solvable=F]]) ];
# }
