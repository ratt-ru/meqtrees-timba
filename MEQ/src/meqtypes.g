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

# Creates a request ID
const meqrequestid := function(domain_id,config_id=0,iter_id=0)
{ 
  return hiid(domain_id,config_id,iter_id);
}

# Creates a defrec for a node
const meqnode := function (class,name,children=F,default=[=],config_groups="")
{
  defrec := [ class=class,name=name ];
  if( !is_boolean(children) )
    defrec.children := children;
  if( len(config_groups) )
    defrec.config_groups := hiid(config_groups);
  return defrec;
}

# Creates a Polc
const meqpolc := function (coeff,freq0=0,freqsc=1,time0=0,timesc=1,pert=F,
                           domain=F)
{
  rec := [ freq_0=freq0,time_0=time0,freq_scale=freqsc,time_scale=timesc ];
  # set coeff  
  if( len(coeff) == 1 )
    rec.coeff := array(as_double(coeff),1,1);
  else if( !has_field(coeff::,'shape') || len(coeff::shape) != 2 )
    fail 'meqpolc: coeff must be either scalar or a 2D array';
  else
    rec.coeff := as_double(coeff);
  # set perturbation if specified
  if( !is_boolean(pert) )
    rec.pert := pert;
  # set domain if specified
  if( !is_boolean(domain) )
  {
    if( !is_dmi_type(domain,'MeqDomain') )
      fail 'meqpolc: domain argument must be a meqdomain';
    rec.domain := domain;
  }
  rec::dmi_actual_type := 'MeqPolc';
  return rec;
}

# Creates a Parm defrec
const meqparm := function (name,default=F,polc=F,config_groups="")
{
  rec := meqnode('MeqParm',name,config_groups=config_groups);
  # set default if specified
  if( !is_boolean(default) )
  {
    if( !is_dmi_type(default,'MeqPolc') )
      default := meqpolc(default);
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
          fail 'meqparm: polc argument must be a meqpolc or a vector of meqpolcs';
      }
      rec.polcs := polc;
      rec.polcs::dmi_datafield_content_type := 'MeqPolc';
    }
  }
  return rec;
}

# Creates a Meq::Domain
const meqdomain := function (startfreq,endfreq,starttime,endtime)
{
  domain := as_double([startfreq,endfreq,starttime,endtime]);
  domain::dmi_datafield_content_type := 'double';
  domain::dmi_actual_type  := 'MeqDomain';
  return domain;
}

# Creates a Meq::Cells
const meqcells := function (domain,num_freq,times,time_steps )
{
  rec := [ domain=domain,num_freq=as_integer(num_freq),
           times=as_double(times),
           time_steps=as_double(time_steps) ];
  rec::dmi_actual_type := 'MeqCells';
  return rec;
}

# creates a state list for inclusion in a request
const meqinitstatelist := function ()
{
  rec := [=];
  rec::dmi_datafield_content_type := 'DataRecord';
  return rec;
}

# adds to a state list 
const meqaddstatelist := function (ref rec,node,state)
{
  if( is_integer(node) )
    rec[spaste('#',len(rec)+1)] := [ nodeindex=node,state=state ];
  else if( is_string(node) )
    rec[spaste('#',len(rec)+1)] := [ name=node,state=state ];
  else 
    fail 'node must be specified by index or name';
  return ref rec;
}

# creates a request
const meqrequest := function (cells=F,request_id=F,calc_deriv=0)
{
  global _meqdomain_id;
  # if no request ID supplied, generate one by incrementing the
  # global domain ID. 
  if( is_boolean(request_id) )
    request_id := meqrequestid(_meqdomain_id+:=1);
  else  # else, setup global domain ID from the one given in the request ID
    _meqdomain_id := as_integer(as_string(request_id) ~ s/\..*$//);
  rec := [ request_id=hiid(request_id),
           calc_deriv=as_integer(calc_deriv) ];
  if( !is_boolean(cells) )
    rec.cells := cells;
  rec::dmi_actual_type := 'MeqRequest';
  
  const rec.addstate := function (group,node,state)
  {
    wider rec;
    # add node_state and group subrecord
    if( !has_field(rec,'node_state') )
      rec.node_state := [=];
    if( !has_field(rec.node_state,group) )
      rec.node_state[group] := [=];
    ns := ref rec.node_state[group];
    # node specified by index
    if( is_integer(node) )
    {
      if( len(node) == 1 )  # single index: add to by_nodeindex map
      {
        if( !has_field(ns,'by_nodeindex') )
          ns.by_nodeindex := [=];
        ns.by_nodeindex[spaste('#',as_string(node))] := state;
      }
      else # multiple indices: add to by_list map
      {
        if( !has_field(ns,'by_list') )
          ns.by_list := meqinitstatelist();
        meqaddstatelist(ns.by_list,node,state);
      }
    }
    else if( is_string(node) ) # string nodes: add to by_list map
    {
      if( !has_field(ns,'by_list') )
        ns.by_list := meqinitstatelist();
      meqaddstatelist(ns.by_list,node,state);
    }
    else
      fail 'meqrequest.addstate(): node must be specified by index or name(s)';
    return T;
  }
  
  return ref rec;
}
