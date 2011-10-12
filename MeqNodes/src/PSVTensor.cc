//# PSVTensor.cc: The point source DFT component for a station
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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
//# $Id: PSVTensor.cc 8270 2011-07-06 12:17:23Z oms $

#include <MeqNodes/PSVTensor.h>
#include <DMI/AID-DMI.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {

InitDebugContext(PSVTensor,"PSVTensor");
  
  
using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidB,AidUVW,
  AidE|1,AidE|1|AidConj,
};
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const double _2pi_over_c = casa::C::_2pi / casa::C::c;


PSVTensor::PSVTensor()
: TensorFunction(-4,child_labels,3), // first 3 children mandatory, rest are optional
  narrow_band_limit_(.05) 
{
  // dependence on frequency
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

PSVTensor::~PSVTensor()
{}

//##ModelId=400E53550233
void PSVTensor::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);
  rec[AidNarrow|AidBand|AidLimit].get(narrow_band_limit_,initializing);
}

const LoShape shape_3vec(3),shape_2x3(2,3);

// Checks tensor dimensions of a child result to see that they are a per-source tensor
// Valid dimensions are [] (i.e. [1]), [N], [Nx1], [Nx1x1], or [Nx2x2].
void PSVTensor::checkTensorDims (int ichild,const LoShape &shape,int nsrc)
{
  int n = 0;
  FailWhen(shape.size()>3,"child '"+child_labels[ichild].toString()+"': illegal result rank (3 at most expected)");
  if( shape.size() == 0 )
    n = 1;
  else
  {
    n = shape[0];
    if( shape.size() == 2 )
    {
      FailWhen(shape[1]!=1,"child '"+child_labels[ichild].toString()+"': rank-2 result must be of shape Nx1");
    }
    else if( shape.size() == 3 )
    {
      FailWhen(!(shape[1]==1 && shape[2]==1) && !(shape[1]==2 && shape[2]==2),   // Nx1x1 or Nx2x2 result 
          "child '"+child_labels[ichild].toString()+"': rank-3 result must be of shape Nx2x2 or Nx1x1");
    }
  }
  FailWhen(n!=nsrc,"child '"+child_labels[1].toString()+"': first dimension does not match number of sources");
}

// Checks tensor dimensions of children, returns dimensions of our result (2x2)
LoShape PSVTensor::getResultDims (const vector<const LoShape *> &input_dims)
{
  const LoShape &lmn = *input_dims[0], &b = *input_dims[1], &uvw = *input_dims[2];
  // the first child (LMN) is expected to be of shape Nx3, the second (B) of Nx2x2
  FailWhen(lmn.size()!=2 || lmn[1]!=3,"child '"+child_labels[0].toString()+"': an Nx3 result expected");
  // N is num_sources_
  num_sources_ = lmn[0];
  // UVW must be a 3-vector or a 2x3 matrix (in this case smearing is enabled, and the second row contains du,dv,dw).
  FailWhen(uvw!=shape_3vec && uvw!=shape_2x3,"child '"+child_labels[2].toString()+"': an 2x3 matrix or a 3-vector expected");
  // B must be a per-source tensor
  checkTensorDims(1,b,num_sources_);
  // Additional children after the 3rd should come in pairs (Jones term, plus its conjugate), and be per-source tensors
  FailWhen((input_dims.size()-3)%2!=0,"a pair of children must be provided per each Jones term");
  for( uint i=3; i<input_dims.size(); i++ )
    checkTensorDims(i,*input_dims[i],num_sources_);
  
  // our result is a 2x2 matrix 
  return LoShape(2,2);
}

// This gets the time/frequency info from the cells, and puts these into Vells objects:
// freq_vells_ for the frequency axis,
// df_over_2_ and f_dt_over_2_ for delta-freq/2 and freq*delta-time/2 (used in smearing calculations)
void PSVTensor::computeResultCells (Cells::Ref &ref,
        const std::vector<Result::Ref> &childres,const Request &request)
{
  TensorFunction::computeResultCells(ref,childres,request);
  const Cells & cells = *ref;
  Vells freq_approx;
  if( cells.isDefined(Axis::FREQ) )
  {
    int nfreq = cells.ncells(Axis::FREQ);
    // set up frequency vells
    freq_vells_ = Vells(0,Axis::freqVector(nfreq),false);
    memcpy(freq_vells_.realStorage(),cells.center(Axis::FREQ).data(),nfreq*sizeof(double));
    // In the narrow-band case, use a single frequency for smearing calculations
    // (to speed up things)
    const Domain &dom = cells.domain();
    double freq0 = dom.start(Axis::FREQ);
    double freq1 = dom.end(Axis::FREQ);
    double midfreq = (freq0+freq1)/2;
    // narrow-band: use effectively a single frequency
    if( ::abs(freq0-freq1)/midfreq < narrow_band_limit_ )
      freq_approx = midfreq;
    else
      freq_approx = freq_vells_;
    // set up delta-freq/2 vells
    if( cells.numSegments(Axis::FREQ)<2 )
      df_over_2_ = cells.cellSize(Axis::FREQ)(0)/2;
    else
    {
      df_over_2_ = Vells(0,Axis::freqVector(nfreq),false);
      memcpy(df_over_2_.realStorage(),cells.cellSize(Axis::FREQ).data(),nfreq*sizeof(double));
      df_over_2_ /= 2;
    }
  }
  else
    freq_vells_ = freq_approx = df_over_2_ = 0;
  // set up delta-time/2 vells
  if( cells.isDefined(Axis::TIME) )
  {
    int ntime = cells.ncells(Axis::TIME);
    if( cells.numSegments(Axis::TIME)<2 )
      f_dt_over_2_ = cells.cellSize(Axis::TIME)(0)/2;
    else
    {
      f_dt_over_2_ = Vells(0,Axis::timeVector(ntime),false);
      memcpy(f_dt_over_2_.realStorage(),cells.cellSize(Axis::TIME).data(),ntime*sizeof(double));
      f_dt_over_2_ /= 2;
    }
    f_dt_over_2_ *= freq_approx;
  }
  else
    f_dt_over_2_ = 0;
}

// helper function: works out matrix product C=A*B
// A and B are iterators yielding Vells pointers, will be incremented four times
// Note that C may be the same as A or B, in which case the multiplication will overwrite the contents
template<class IA,class IB>
inline void matrixProduct (Vells c[4],IA ia,IB ib)
{
  Vells a0 = **ia++; 
  Vells a1 = **ia++; 
  Vells a2 = **ia++; 
  Vells a3 = **ia++; 
  Vells b0 = **ib++; 
  Vells b1 = **ib++; 
  Vells b2 = **ib++; 
  Vells b3 = **ib++; 
  c[0] = a0*b0 + a1*b2;
  c[1] = a0*b1 + a1*b3;
  c[2] = a2*b0 + a3*b2;
  c[3] = a2*b1 + a3*b3;
}
// helper function: works out scalar product C=a*B
// Note that C may be the same as A or B, the multiply is safe and will overwrite the contents
template<class IB>
inline void scalarProduct (
  Vells c[4],const Vells &a,IB ib)
{
  for( int i=0; i<4; i++ )
    c[i] = a*(**ib++);
}

// This evaluates the result tensors
void PSVTensor::evaluateTensors (std::vector<Vells> & out,
     const std::vector<std::vector<const Vells *> > &args )
{
  // uvw coordinates are the same for all sources, and each had better be a 'timeshape' vector
  const Vells & vu = *(args[2][0]);
  const Vells & vv = *(args[2][1]);
  const Vells & vw = *(args[2][2]);
  // if we have delta-uvws, then enable smearing
  const Vells *pdu=0,*pdv,*pdw;
  if( args[2].size() == 6 )
  {
    pdu = args[2][3];
    pdv = args[2][4];
    pdw = args[2][5];
  }
  // X is an intermediate object used in calculations
  Vells X[4];
  const Vells * pX[4];
  for( int i=0; i<4; i++ )
    pX[i] = &X[i];
  // initialize the output vells where the sum is accumulated
  for( int i=0; i<4; i++ )
    out[i] = Vells::Null();
  
  // compute K=exp{ i*_2pi_over_c*freq*(u*l+v*m+w*n) } for every source, multiply by smearing term,
  // multiply by B matrix and all Jones matrices, then sum over all sources
  for( int isrc=0; isrc<num_sources_; isrc++ )
  {
    // get the LMNs for this source
    const Vells & vl = *(args[0][isrc*3]);
    const Vells & vm = *(args[0][isrc*3+1]);
    const Vells & vn = *(args[0][isrc*3+2]);
    // get the phase argument exp{ i*2*pi/c*(u*l+v*m+w*n) } -- this will be multiplied by frequency in computeExponent()
    Vells p = (vu*vl + vv*vm + vw*vn)*_2pi_over_c;
    Vells K = computeExponent(p,resultCells());
    // if delta-uvw givem, multiply phase by the smearing term (sigma)
    if( pdu )
    {
      Vells dp = ( (*pdu)*vl + (*pdv)*vm + (*pdw)*vn )*_2pi_over_c;
      K *= computeSmearingTerm(p,dp);
    }
    // Now multiply by each successive pair of Jones terms
    // start with X=B
    // if B is scalar -- expand to diagonal matrix
    if( args[1].size() == num_sources_ )
    {
      X[0] = X[3] = *args[1][isrc];
      X[1] = X[2] = Vells::Null();       // null
    }
    // else B is full matrix -- just copy
    else
      for( int i=0; i<4; i++ )
        X[i] = *args[1][isrc*4+i];
    // now loop over Jones terms, computing J*X*Jconj for each pair
    int njones = (args.size()-3)/2;
    int iarg = 3; // first Jones term is argument 3
    for( int i=0; i<njones; i++ )
    {
      // first compute X = J*X
      // if each Jones term is a scalar (i.e. tensor is of size NSRC), then Jones[isrc] is the scalar we need to multiply by
      if( args[iarg].size() == num_sources_ )
        scalarProduct(X,(*args[iarg][isrc]),pX);
      // else each Jones term is a 2x2 matrix (tensor is of size NSRCx2x2), so Jones[isrc*4] is the first matrix element
      else
        matrixProduct(X,args[iarg].begin()+isrc*4,pX);
      iarg++;
      // now X = X*Jconj
      if( args[iarg].size() == num_sources_ )
        scalarProduct(X,*(args[iarg][isrc]),pX);
      else
        matrixProduct(X,pX,args[iarg].begin()+isrc*4);
      iarg++;
    }
    // multiply by K and accumulate in sum
    for( int i=0; i<4; i++ )
      out[i] += X[i]*K;
  }
}

// This computes the phase term, exp(-i*freq*p)
// It is mostly identical to VisPhaseShift::evaluateTensors()
// The p term is expected to be (ul+vm+wn)*2_pi/c, so need only be multiplied by frequency
// to get the actual phase
Vells PSVTensor::computeExponent (const Vells &p,const Cells &cells)
{
  // Now, if r is only variable in time, and we only have one
  // regularly-spaced frequency segment, we can use a quick algorithm
  // to compute only the exponent at freq0 and df, and then multiply
  // the rest.
  // Otherwise we fall back to the (potentially slower) full VellsMath version
  if( p.extent(Axis::TIME) == p.nelements() &&
      cells.ncells(Axis::FREQ) > 1            &&
      cells.numSegments(Axis::FREQ) == 1        )  // fast eval possible
  {
    // need to compute exp(-i*(freq0+n*dfreq)*p) for n=0...Nchan
    // decompose this into exp(-i*freq0*p)*exp(-i*dfreq*p)**n
    const double *fq = freq_vells_.realStorage();
    Vells vf0 = polar(1,p*fq[0]);
    Vells vdf = polar(1,p*(fq[1]-fq[0]));

    int ntime = p.extent(Axis::TIME);
    int nfreq = cells.ncells(Axis::FREQ);
    LoShape result_shape(ntime,nfreq);

    Vells out(numeric_zero<dcomplex>(),result_shape);
    dcomplex* resdata   = out.complexStorage();
    const dcomplex* pf0 = vf0.complexStorage();
    const dcomplex* pdf = vdf.complexStorage();

    int step = (ntime > 1 ? 1 : 0);
    for(int i = 0; i < ntime; i++)
    {
      dcomplex val0 = *pf0;
      *resdata++    = val0;
      dcomplex dval = *pdf;
      for(int j=1; j < nfreq; j++)
      {
        val0      *= dval;
        *resdata++ = val0;
      }// for j (freq)
      pf0 += step;
      pdf += step;
    }// for i (time)
    return out;
  }
  else // slower but much simpler
  {
    // create freq vells from grid
    return polar(1,p*freq_vells_);
  }
}

// This computes the time/freq smearing term, sinc(dt/2)*sinc(df/2), where
// dp is the delta-phase in time, and df is the delta-phase in frequency.
// Input argument is phase and delta-phase (which still needs to be multiplied by frequency),
// i.e. p is expected to be (ul+vm+wn)*2_pi/c, and dp is the same for delta-uvw

Vells PSVTensor::computeSmearingTerm (const Vells &p,const Vells &dp)
{
  Vells dphi = f_dt_over_2_ * dp;
  Vells dpsi = df_over_2_ * p;
  
  Vells prod1 = sin(dphi)/dphi;
  Vells prod2 = sin(dpsi)/dpsi;
  
  prod1.replaceFlaggedValues(dphi.whereEq(0.),1.);
  prod2.replaceFlaggedValues(dpsi.whereEq(0.),1.);
  
  return prod1*prod2;
}


} // namespace Meq
