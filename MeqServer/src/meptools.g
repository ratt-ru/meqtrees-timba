### meptools.g: tools for manipulating MEPs
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

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

include 'meq/meqtypes.g'

#------ meq.get_domain()
# Helper function: returns the domain of its argument.
# If argument is a meq.domain, simply returns it. If argument is 
# a polc, returns domain of polc, or a default ([0:1,0:1]) if polc 
# does not have a domain defined.
const meq.get_domain := function (x)
{
  if( is_dmi_type(x,'MeqDomain') )
    return x;
  else if( is_dmi_type(x,'MeqPolc') )
  {
    if( has_field(x,'domain') )
      return x.domain;
    else
      return meq.domain(0,1,0,1);
  }
  else
    fail 'meq.get_domain(): argument is not a meq.domain or a meq.polc';
}

#------ meq.get_full_grid(x,y,cells)
# Given a cells, fills in two vectors with the coordinates of every grid
# point defined by that cells, as follows (assuming N frequencies and M
# times):
#     [x1,...,xN,x1,...,xN,x1,...,xN, ... ,x1,...,xN ]
#     [y1 ... y1,y2 ... y2,y3 ... y3, ... ,yM,...,yM ]
const meq.get_full_grid := function (ref x,ref y,cells)
{
  xp := cells.grid[1];
  yp := cells.grid[2];
  # create composite arrays where every combination is present
  val x := rep(xp,len(yp));           # [x1,...,xn,x1,...,xn,x1,...,xn,x1 ...
  val y := array(0.,len(xp)*len(yp)); # [y1 ... y1,y2 ... y2,y3 ... y3,y4 ...
  for( i in 1:len(yp) )
    y[(i-1)*len(xp)+(1:len(xp))] := yp[i];
  return len(x);
}

#------ meq.eval_polc()
# Evaluates a polc over either (a) a set of points, or (b) a cells object.
# (a): cells not supplied; x and y must be vectors of coordinates
# (b): cells supplied and must be valid meq.cells object.
#      In this case it calls meq.get_full_grid(), above, to obtain x and y.
const meq.eval_polc := function (polc,x=F,y=F,cells=F)
{
  if( is_dmi_type(cells,'MeqCells') )
  {
    meq.get_full_grid(x,y,cells);
    # print 'x: ',x; print 'y: ',y;
  }
  else
  {
    if( is_boolean(x) || is_boolean(y) )
      fail 'numeric x and y vectors must be supplied'
    if( len(x) != len(y) )
      fail 'lengths of x and y vectors must match';
  }
  # evaluate
  x := (x-polc.freq_0)/polc.freq_scale;
  y := (y-polc.time_0)/polc.time_scale;
  res := array(0.,len(x));
  powx := 1;
  nx := shape(polc.coeff)[1];
  ny := shape(polc.coeff)[2];
  for( i in 1:nx )
  {
    powy := powx;
    for( j in 1:ny )
    {
      res +:= polc.coeff[i,j]*powy;
      powy *:= y;
    }
    powx *:= x;
  }
  # if input was a cells, reform the result into a matrix
  if( is_dmi_type(cells,'MeqCells') )
    res := array(res,len(cells.grid[1]),len(cells.grid[2]));
  return res;
}

#------ meq.envelope_2domains()
# Helper function for meq.envelope_domain()
# Computes the envelope of two meqdomains. If the first domain is
# undefined, simply returns the second domain.
const meq.envelope_2domains := function (d1,d2)
{
  if( !is_dmi_type(d1,'MeqDomain') )
    return d2;
  for( a in field_names(d1) )
    if( has_field(d2,'a') && is_numeric(d1[a]) && is_numeric(d2[a])
        && len(d1[a]) == 2 && len(d2[a]) == 2 )
      d1[a] := range(d1[a],d2[a]);
  return d1;
}

#------ meq.envelope_domain()
# Given any number of meqdomains or meqpolcs, returns a meq.domain that is 
# an envelope of all the supplied domains. The following arguments can be used:
#   * meqpolcs or meqdomains
#   * records (i.e. vectors) of meqpolcs or meqdomains
const meq.envelope_domain := function (...)
{
  dom := F;
  for( i in 1:num_args(...) )
  {
    x := nth_arg(i,...);
    if( is_record(x) && !has_field(x::,'dmi_actual_type') )
    {
      for( i in 1:len(x) )
        dom := meq.envelope_2domains(dom,meq.get_domain(x[i]));
    }
    else
      dom := meq.envelope_2domains(dom,meq.get_domain(x));
  }
  return dom;
}





