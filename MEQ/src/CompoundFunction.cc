//# CompoundFunction.cc: Base class for a compound expression node (i.e. with multiple-planed result)
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#include <MEQ/CompoundFunction.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>

namespace Meq {

CompoundFunction::CompoundFunction (int nchildren,const HIID *labels,int nmandatory)
  : Function(nchildren,labels,nmandatory)
{}

CompoundFunction::~CompoundFunction ()
{
}

int CompoundFunction::checkChildResults (Result::Ref &resref, 
  std::vector<const VellSet *> &child_vs,
  const std::vector<Result::Ref> &childres,
  const int expect_nvs[],
  const int expect_integrated[])
{
  // Check that child results are all OK (no fails, expected # of vellsets per child)
  uint iivs = 0; // this is an index into child_vs
  // Setup pointers to child vellsets. Along the way, check that child 
  // results are all OK (no fails, 3 vellsets per child)
  // NB:****** figure out how to handle the integrated property
  VellSet::Ref vsfail(DMI::ANONWR);
  for( uint ichild=0; ichild<childres.size(); ichild++ )
  {
    const Result &chres = *(childres[ichild]);
    int nvs = chres.numVellSets();
    if( nvs != expect_nvs[ichild] )
    {
      MakeFailVellSet(vsfail(),ssprintf("child %s: expecting %d VellSets, got %d",
          getChildLabel(ichild).toString().c_str(),expect_nvs[ichild],nvs));
    }
    else if( expect_integrated[ichild] >= 0 &&
        chres.isIntegrated() != expect_integrated[ichild] )
    {
      MakeFailVellSet(vsfail(),ssprintf("child %s: integrated: %d, expected %d",
          getChildLabel(ichild).toString().c_str(),
          int(chres.isIntegrated()),expect_integrated[ichild]));
    }
    else
    {
      // accumulate pointers to child vellsets, check for fails
      for( int j=0; j<nvs; j++ )
      {
        const VellSet &chvs = *( child_vs[iivs++] = &( chres.vellSet(j) ) );
        // if it's a fail, propagate fails to output
        if( chvs.isFail() )
        {
          for( int j=0; j<chvs.numFails(); j++ )
            vsfail().addFail(&chvs.getFail(j));
        }
      }
    }
  }
  // any fails come up above? Return complete fail
  if( vsfail->isFail() )
  {
    resref <<= new Result(1);
    resref().setVellSet(0,vsfail.deref_p());
    return RES_FAIL;
  }
  Assert(iivs == child_vs.size());
  return 0;
}
    
void CompoundFunction::computeValues ( Result &result,const std::vector<const VellSet *> &chvs )
{
  // collect vector of pointers to main values
  int num_children = chvs.size();
  vector<const Vells *> mainvals(num_children);
  for( int i=0; i<num_children; i++ )
    mainvals[i] = &( chvs[i]->getValue() );
 
  // determine output spids and # of pert sets
  int npertsets;
  vector<int> spids = findSpids(npertsets,chvs);
  int nspids = spids.size();
  
  // initialize output vellsets with the given # of spids and pert sets
  int nout = result.numVellSets();
  vector<VellSet *> out_vs(nout);
  for( int i=0; i<nout; i++ )
  {
    out_vs[i] = &( result.setNewVellSet(i,nspids,npertsets) );
    out_vs[i]->setSpids(spids);
  }
  const Cells &res_cells = result.cells();
  const LoShape &res_shape = res_cells.shape();
  
  // evaluate main value
  vector<Vells> out_values(nout);
  evalResult(out_values,mainvals,res_cells);
  for( int i=0; i<nout; i++ )
    out_vs[i]->setValue(out_values[i]);
  
  // combine flags from children
  if( combineChildFlags(*(out_vs[0]),chvs) && nout>1 )
  {
    // if more than one output vellset, duplicate flags column (by ref, of course)
    DataArray::Ref flagcol = out_vs[0]->getOptColRef(VellSet::FLAGS);
    for( int i=1; i<nout; i++ )
      out_vs[i]->setOptCol(VellSet::FLAGS,flagcol.deref_p());
  }
  
  // Evaluate all perturbed values.
  vector<vector<const Vells*> > pert_values(npertsets);
  vector<double> pert(npertsets);
  vector<int> indices(num_children,0);  // holds index of current spid for each child
  vector<int> found(npertsets);
  for( uint ispid=0; ispid<spids.size(); ispid++) 
  {
    found.assign(npertsets,-1);
    // pert_values start with pointers to each child's main value
    pert_values.assign(npertsets,mainvals);
    // loop over children. For every child that contains a perturbed
    // value for spid[ispid], put a pointer to the perturbed value into 
    // pert_values[ipert][ichild]. For children that do not contain a 
    // perturbed value, it will retain a pointer to the main value.
    // The values of the pertubations themselves are collected into pert[]; 
    // these must match across all children
    for( int ich=0; ich<num_children; ich++ )
    {
      const VellSet &vs = *(chvs[ich]);
      int inx = vs.isDefined(spids[ispid],indices[ich]);
      if( inx >= 0 )
      {
        for( int ipert=0; ipert<std::max(vs.numPertSets(),npertsets); ipert++ )
        {
          const Vells &pvv = vs.getPerturbedValue(inx,ipert);
          FailWhen(pvv.isArray() && pvv.shape() != res_shape,"mismatch in child result shapes");
          pert_values[ipert][ich] = &pvv;
          if( found[ipert] >=0 )
          {
            FailWhen(pert[ipert]!=vs.getPerturbation(inx,ipert),
                ssprintf("perturbation %d for spid %d does not match between child results %d and %d",
                  ipert,spids[ispid],found[ipert],ich));
          }
          else
          {
            pert[ipert] = vs.getPerturbation(inx,ipert);
            found[ipert] = ich;
          }
        }
      }
    }
    // now, call evaluate() on the pert_values vectors to obtain the
    // perturbed values of the function
    for( int ipert=0; ipert<npertsets; ipert++ )
    {
      FailWhen(found[ipert]<0,
               ssprintf("missing perturbation set %d for spid %d",
                        ipert,spids[ispid]));
      evalResult(out_values,pert_values[ipert],res_cells);
      for( int i=0; i<nout; i++ )
      {
        out_vs[i]->setPerturbation(ispid,pert[ipert],ipert);
        out_vs[i]->setPerturbedValue(ispid,out_values[i],ipert);
      }
    }
  } // end for(ispid) over spids
  
}
    
};
