//# ResampleMachine.cc: resamples result resolutions
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

#include "ResampleMachine.h"
#include "MeqVocabulary.h"
#include "Request.h"
#include "Result.h"
#include "Cells.h"


namespace Meq {

ResampleMachine::ResampleMachine ()
: flag_mask(-1),flag_bit(0),flag_density(0.5)
{}

ResampleMachine::ResampleMachine (const Cells &output)
: flag_mask(-1),flag_bit(0),flag_density(0.5)
{ 
  setOutputRes(output); 
}

ResampleMachine::ResampleMachine (const Cells &output,const Cells &input)
: flag_mask(-1),flag_bit(0),flag_density(0.5)
{ 
  setOutputRes(output); setInputRes(input); 
}


template<class T>
void ResampleMachine::doResample (Vells::Ref &voutref,const blitz::Array<T,2> &in)
{
  int nx = outshape[0];
  int ny = outshape[1];
  
  Vells &vout = voutref <<= new Vells(T(),nx,ny,false);
  blitz::Array<T,2> &out = vout.as(Type2Type<blitz::Array<T,2> >());
  
  // i1,j1: current output cell/block of cells of input array
  // i0,j0: top left of integrated cell in 
  int i0,j0=0; 
  // loop over output
  for( int j1=0; j1<ny; j1+=nexpand[1],j0+=nsum[1] )
  {
    i0=0;
    for( int i1=0; i1<nx; i1+=nexpand[0],i0+=nsum[0] )
    {
      T ss = 0;
      // if output value not fully flagged, do the sum
      if( !outflags || !(*outflags)(i1,j1) )
      {
        // sum up block of input cells at (i0,j0)
        int isum, jsum = j0;
        for( int j=0; j<nsum[1]; j++,jsum++ )
        {
          isum = i0;
          for( int i=0; i<nsum[0]; i++,isum++ )
            if( !inflags || !((*inflags)(isum,jsum)&flag_mask) )
              ss += in(isum,jsum);
        }
        // renormalize
        ss *= renorm(i1,j1);
      }
      // assign value to block of output cells
      int iexp, jexp = j1;
      for( int j=0; j<nexpand[1]; j++,jexp++ )
      {
        iexp = i1;
        for( int i=0; i<nexpand[0]; i++,iexp++ )
          out(iexp,jexp) = ss;
      }
    }
  }
}

// resamples Vells to a new grid and returns the result 
Vells::Ref ResampleMachine::resampleVells (const Vells &in)
{
  Vells::Ref out;
  // array vells -- do integrate/expand
  if( in.isArray() )
  {
    // init pv to complex or double Vells of the right shape
    if( in.isComplex() )
      doResample(out,in.getComplexArray());
    else
      doResample(out,in.getRealArray());
  }
  // scalar vells -- do trivial rescaling
  else
  {
    if( renorm_factor == 1 )
      out.attach(in,DMI::READONLY);
    else
      out <<= new Vells( in * renorm_factor );
  }
  return out;
}

void ResampleMachine::setOutputRes (const Cells &out)
{
  inres.detach();
  // if already referenced, attach to ref, else attach copy
  if( out.refCount() )
    outres.attach(out);
  else
    outres <<= new Cells(out);
}

void ResampleMachine::setInputRes (const Cells &incells)
{
  FailWhen(!outres.valid(),"output resolution must be set first");
  const Cells &outcells = *outres;
  outshape = outcells.shape();
  identical = true;
  // figure out how to convert between cells
  for( int i=0; i<DOMAIN_NAXES; i++ )
  {  
    nsum[i] = nexpand[i] = 1;
    int nin = incells.ncells(i),
        nout = outshape[i];
    if( nin > nout ) // decreasing resolution in this dimension
    {
      int n = nin/nout;
      FailWhen(nin%nout,
          ssprintf("incompatible number of cells in dimension %d: %d child, %d parent",
            i,nin,nout));
      nsum[i] = n;
      identical = false;
    }
    else if( nin < nout )
    {
      int n = nout/nin;
      FailWhen(nout%nin,
          ssprintf("incompatible number of cells in dimension %d: %d child, %d parent",
            i,nin,nout));
      nexpand[i] = n;
      identical = false;
    }
  }
  // resize normalization matrix
  renorm.resize(outshape);
  // if we successfully reached this point, attach Cells to inres to indicate
  // that everything's been set up successfully
  // if already referenced, attach to ref, else attach copy
  if( incells.refCount() )
    inres.attach(incells);
  else
    inres <<= new Cells(incells);
}

void ResampleMachine::apply (VellSet::Ref &outref,const VellSet::Ref &inref,bool integrated)
{
  FailWhen(!outres.valid(),"output resolution not set");
  FailWhen(!inres.valid(),"input resolution not set");
  const VellSet &invs = *inref;
  // if resampling is 1-1, or input is a fail, just pass to output 
  if( identical || invs.isFail() )
  {
    outref.copy(inref);
    return;
  }
  
  // else create new output VS
  VellSet &vs = outref <<= new VellSet(invs.numSpids(),invs.numPertSets());
  vs.setShape(outshape);
  vs.copySpids(vs);
  vs.copyPerturbations(vs);
  
  renorm.resize(outshape);
  renorm_factor = 1;
  // figure out how to convert between cells
  for( int i=0; i<DOMAIN_NAXES; i++ )
  {  
    // if integrating, then we just sum up the cells and leave it at that.
    // else if averaging, we must divide by N to get the average value.
    if( nsum[i] && !integrated ) // decreasing resolution in this dimension
      renorm_factor /= nsum[i];
    // if integrating, then we have to renormalize individual cells
    // else if averaging, then just leave the value as is
    if( nexpand[i] && integrated )
      renorm_factor /= nexpand[i];
  }
  renorm = renorm_factor;
  
  // handle flags if supplied (and configured)
  if( flag_mask && invs.hasOptCol<VellSet::FLAGS>() )
  {
    inflags  = &( invs.getOptCol<VellSet::FLAGS>() );
    outflags = &( vs.initOptCol<VellSet::FLAGS>() );

    // # of pixels in integarted cell
    int cellsize = nsum[0]*nsum[1];
    // threshold for number of flagged pixels in integrated cell which
    // will cause us to flag the output
    int nfl_threshold = std::max( cellsize,
                              int(floor(cellsize*flag_density+.5)) );

    int nx = outshape[0];
    int ny = outshape[1];
    // i1,j1: current output cell/block of cells of input array
    // i0,j0: top left of integrated cell in 
    int i0,j0=0; 
    // loop over output
    for( int j1=0; j1<ny; j1+=nexpand[1],j0+=nsum[1] )
    {
      i0=0;
      for( int i1=0; i1<nx; i1+=nexpand[0],i0+=nsum[0] )
      {
        VellSet::FlagType sumfl = 0; // OR of flags within integration cell
        int nfl = 0;                 // number of flagged pixels in cell
        // sum up block of input cells at (i0,j0)
        int isum, jsum = j0;
        for( int j=0; j<nsum[1]; j++,jsum++ ) {
          isum = i0;
          for( int i=0; i<nsum[0]; i++,isum++ ) {
            int fl = (*inflags)(isum,jsum)&flag_mask;
            if( fl ) {
              sumfl |= fl;
              nfl++;
            }
          }
        }
        // have we found any flags within the integrated cell?
        if( nfl )
        {
          // critical number of flags => flag entire output cell
          if( nfl >= nfl_threshold )
          {
            // if flag_bit is specified, use that instead of the summary flags
            if( flag_bit )
              sumfl = flag_bit;
            // assign flag value to block of output flags 
            int iexp, jexp = j1;
            for( int j=0; j<nexpand[1]; j++,jexp++ ) {
              iexp = i1;
              for( int i=0; i<nexpand[0]; i++,iexp++ )
                (*outflags)(iexp,jexp) = sumfl;
            }
          }
          // partially flagged cell has to be renormalized since fewer 
          // points will be used in integration
          else
            renorm(i1,j1) *= double(cellsize)/(cellsize-nfl);
        }
      }
    }
  }
  else // no flags to handle
  {
    inflags = outflags = 0;
  }

  // resample main value
  vs.setValue(resampleVells(invs.getValue()));
  // resample perturbed values
  for( int iset=0; iset<vs.numPertSets(); iset++ )
    for( int ipert=0; ipert<vs.numSpids(); ipert++ )
      vs.setPerturbedValue(ipert,
          resampleVells(invs.getPerturbedValue(ipert,iset)),iset);
}

} // namespace Meq
