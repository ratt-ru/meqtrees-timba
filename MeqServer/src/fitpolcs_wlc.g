### fitpolcs_wlc.g: fitter for polcs using a weighted linear combination
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

include 'debug_methods.g'
include 'meq/meptable.g'
include 'meq/meptools.g'
include 'functionals.g'
include 'fitting.g'

#------ functional_poly2()
# Creates a functional representing a 2D polynomial of the specified x,y order

const meq.functional_poly2 := function (degx,degy)
{
  # create a functional for the target polc
  terms := array('',(degx+1)*(degy+1));
  np := 0;
  for( j in 0:degy )
    for( i in 0:degx )
    {
      # create "pk*x0*..*x0*x1*...*x1" string for term (i,j)
      s := spaste('p',np);
      if( i>0 )
        s := paste(s,spaste('x0**',i),sep='*');
      if( j>0 )
        s := paste(s,spaste('x1**',j),sep='*');
      np +:= 1;
      terms[np] := s;
    }
  funcdesc := paste(terms,sep='+');
  # print funcdesc;
  return dfs.compiled(funcdesc);
}


#------ polc2functional()
# Creates a functional from a polc object

const meq.polc2functional := function (polc)
{
  sh := shape(polc.coeff);
  if( len(sh) == 1 )
    return dfs.poly(0,polc.coeff);
  else
  {
    ff := functional_poly2(sh[1]-1,sh[2]-1);
    ff.setparameters(polc.coeff);
    return ff;
  }
}


#------ fitpolc()
# Fits a set of predicted values with a 2D polc of order degx,degy.
# This is a helper function meant to be used by various fitpolcs_xxx schemes.
#   x,y       : vectors of coordinates (length N)
#   values    : is a vector of predicted values (length N)
#   weights   : is a vector of weights (length N), or 1 for no weighting
#   degx,degy : required order of polc in X and Y
#   scale     : scale of polc, as a [x0,xscale,y0,yscale] vector

const meq.fitpolc := function (x,y,values,weights,degx,degy,scale=[0,1,0,1])
{
  if( degx>0 || degy>0 )
  {
    # make a functional object to represent the new polc
    ff := meq.functional_poly2(degx,degy);
    # Note the following possible scenarios:
    # degx>0,degy>0: ff will have two dimensions. Both x and y will
    #                be expected by the fitter.
    # degx>0,degy=0: ff will have one dimension. Only x coordinate will
    #                be expected by the fitter.
    # degx=0,degy>0: ff will have two dimensions (with no dependence on the
    #                first argument). Both x and y expected by the fitter.
    # degx=0,degy=0: constant; processed separately 
    if( ff.ndim()>1 )
      xx := array(rbind((x-scale[1])/scale[2],(y-scale[3])/scale[4]),len(x)*2);
    else 
      xx := (x-scale[1])/scale[2];
    if( !dfit.linear(ff,xx,values,wt=weights) )
      fail 'fitting failed';
    sol := dfit.solution();
  }
  else # c00 only: just use a weighted mean
  {
    sol := sum(values*weights)/sum(weights);
  }
  return meq.polc(array(sol,degx+1,degy+1),scale=scale,domain=domain);
}


#------ fitpolcs_wlc()
# Fits the given polcs with a new degx x degy polc, computed over the specified 
# domain. Uses a weighted-linear combination scheme.
# If no domain is specified, then the envelope of the polcs' domains is 
# used. A scale may be specified as [f0,fscale,t0,tscale]. If it is not 
# specified, then a scale corresponding to [0:1] over the domain is used.

const meq.fitpolcs_wlc := function (polcs,degx=0,degy=0,domain=F,scale=F,verbose=0)
{
  # define a sink for debug output
  sink := debug_sink('fitpolcs_wlc',verbose); 
  
  # figure out domain of target polc
  if( is_boolean(domain) )
    domain := meq.envelope_domain(polcs);
  # figure out scale of target polc
  if( is_boolean(scale) )
    scale := [ domain[1],domain[2]-domain[1],domain[3],domain[4]-domain[3] ];
    
  npolcs := len(polcs);
  sink.dprintf(1,'%d input polcs; output order is %dx%d',npolcs,degx,degy);
  sink.dprintf(2,'output domain: %f:%f,%f:%f',domain[1],domain[2],domain[3],domain[4]);
  sink.dprintf(2,'output scale: %f:%f,%f:%f',scale[1],scale[2],scale[3],scale[4]);
  
  # polcs will be evaluated over a regular grid
  nx := max(degx*2,3);
  ny := max(degy*2,3);
  cells := meq.cells(domain,nx,ny);
  ngrid := meq.get_full_grid(x,y,cells);
  sink.dprint(2,'grid x: ',x);
  sink.dprint(2,'grid y: ',y);
  
  # compute cubes: pval(i,k)   is value of polc k at grid point #i
  #                weight(i,k) is weight
  pval   := array(0.,ngrid,npolcs);
  weight := pval;
  for( k in 1:npolcs )
  {
    p := polcs[k];
    polcname := paste('polc',k);
    sink.dprint(3,polcname,':',p);
    pval[,k] := meq.eval_polc(p,x,y);
    sink.dprint(3,'  polcval: ',pval[,k]);
    # compute weight -- different depending on whether it's in/out of domain
    x0 := (p.domain[1]+p.domain[2])/2;  # domain center
    y0 := (p.domain[3]+p.domain[4])/2;
    rx := (p.domain[2]-p.domain[1])/2;  # domain half-width
    ry := (p.domain[4]-p.domain[3])/2;
    # total weight is wx*wy -- product of independent X, Y weights.
    # Wx,wy: within a domain is linear from 1 at domain center, to 0.5 at edge.
    # Outside a domain, it decreases quadratically, starting from 0.5 at edge.
    ndx := abs(x-x0)/rx;  # ndx: normalized (x-x0)/rx. 1 at domain's edge
    ndy := abs(y-y0)/ry;
    xdom := ndx<=1;       # mask: inside domain x,y
    ydom := ndy<=1;
    wx := wy := array(0.,ngrid);
    sink.dprint(3,'  x domain mask: ',xdom);
    sink.dprint(3,'  y domain mask: ',ydom);
    # print xdom,ydom;
    wx[xdom] := 1-0.5*ndx[xdom];
    wy[ydom] := 1-0.5*ndy[ydom];
    wx[!xdom] := 0.5/(ndx[!xdom]*ndx[!xdom]);
    wy[!ydom] := 0.5/(ndy[!ydom]*ndy[!ydom]);
    sink.dprint(3,'  x weights: ',wx);
    sink.dprint(3,'  y weights: ',wy);
    weight[,k] := wx*wy*p.weight;
    sink.dprint(3,'  total weights: ',weight[,k]);
  }
  # compute the weighted average (wa_val) and per-point summary weight (wa_sw)
  # at every grid point
  pvalw := pval*weight;
  wa_sw := wa_val := array(0.,ngrid);
  for( i in 1:ngrid )
  {
    wa_sw[i]  := sum(weight[i,]);
    wa_val[i] := sum(pvalw[i,])/wa_sw[i];
  }
  sink.dprint(2,'weighted mean: ',wa_val);
  sink.dprint(2,'sum weights: ',wa_sw);
  
  # call fitpolc() above to do the actual fit
  polc := meq.fitpolc(x,y,wa_val,wa_sw,degx,degy,scale=scale);
  if( is_fail(polc) )
    fail;
  sink.dprint(2,'solution coeffs: ',polc.coeff);
  
  # in high-verbosity mode, evaluate the new polc over the grid 
  # and print the differences
  if( verbose>2 )
  {
    diff := wa_val - meq.eval_polc(polc,x,y);
    sink.dprint(2,'weighted mean: ',array(wa_val,nx,ny));
    sink.dprint(2,'weights: ',array(wa_sw,nx,ny));
    sink.dprint(2,'difference with weighted mean: ',array(diff,nx,ny));
  }
  return polc;
}


# test function for fitpolcs_wlc

meq_test.fitpolcs_wlc := function (degx=F,degy=F,tests=[],verbose=3)
{
  global mt,polcs,p;
  if( !is_record(mt) )
    mt:=meq.meptable('test/test.mep')
    
  polcs := mt.getpolcs('x');
  
  # poly degrees for each test
  if( is_boolean(degx) || is_boolean(degy) )
  {
    degx := [3,3,3,0,1,0];
    degy := [0,1,2,1,2,0];
  }
  
  # output polcs placed in p record. Init empty record first
  p := [=];
  for( i in 1:len(degx) )
    p[i] := F;

  # if tests not specified, run all 
  if( !len(tests) )
    tests := 1:len(degx);
   
  for( t in tests )
  {
    printf('\n\n-------- running fitpolcs_wlc(%d,%d) --------\n',degx[t],degy[t]);
    p[t] := meq.fitpolcs_wlc(polcs,degx[t],degy[t],verbose=verbose);
    print '\nresult: ',p[t];
  }
}







