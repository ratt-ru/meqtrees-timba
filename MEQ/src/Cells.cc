//# Cells.cc: The cells in a given domain.
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


//# Includes
#include "Cells.h"
#include "MeqVocabulary.h"
#include <Common/Lorrays.h>
#include <DMI/DataArray.h>

namespace Meq {

static NestableContainer::Register reg(TpMeqCells,True);

const HIID Cells::axis_id_[] = { FFreq , FTime };

//##ModelId=3F86886E02C1
Cells::Cells ()
: domain_(0),shape_(0,0)
{
}

//##ModelId=3F86886E02D1
Cells::~Cells()
{
}


//##ModelId=3F86886E02C8
Cells::Cells (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth),shape_(0,0)
{
  validateContent();
}

//##ModelId=3F95060B01D3
Cells::Cells (const Domain& domain,int nfreq,int ntime)
  : shape_(nfreq,ntime)
{
  // setup datarecord
  // domain
  (*this)[FDomain] <<= domain_ = (domain.refCount() ? &domain : new Domain(domain));
  // grid subrecord
  DataRecord &grid = (*this)[FGrid] <<= new DataRecord;
  setRecVector(grid_[0],grid[axisId(FREQ)],nfreq);
  setRecVector(grid_[1],grid[axisId(TIME)],ntime);
  // cell size subrecord
  DataRecord &cellsize = (*this)[FCellSize] <<= new DataRecord;
  setRecVector(cell_size_[0],cellsize[axisId(FREQ)],nfreq);
  setRecVector(cell_size_[1],cellsize[axisId(TIME)],ntime);
  // segments subrecord
  DataRecord &segments = (*this)[FSegments] <<= new DataRecord;
  DataRecord &segfreq = segments[axisId(FREQ)] <<= new DataRecord;
  DataRecord &segtime = segments[axisId(TIME)] <<= new DataRecord;
  setRecVector(seg_start_[0],segfreq[FStartIndex],1);
  setRecVector(seg_start_[1],segtime[FStartIndex],1);
  setRecVector(seg_end_[0],segfreq[FEndIndex],1);
  setRecVector(seg_end_[1],segtime[FEndIndex],1);
  
  // setup regular grid
  for( int iaxis=0; iaxis<DOMAIN_NAXES; iaxis++ )
  {
    int nx = ncells(iaxis);
    double x0 = domain.start(iaxis);
    double step = (domain.end(iaxis) - x0) / nx;
    // vectors have been pre-sized by setDataRecord, so the expressions
    // in these assignments will be evaluated in array context
    grid_[iaxis] = x0 + step/2 + step*blitz::tensor::i;
    cell_size_[iaxis] = step;
    // use 1 uniform segment
    seg_start_[iaxis](0) = 0;
    seg_end_[iaxis](0)   = nx-1;
  }
}

// creates a combination of the two grids, depending on resample>0
// (uses higher-sampled grid) or <0 (uses lower-sampled grid)
Cells::Cells (const Cells &a,const Cells &b,int resample)
: shape_(0,0)
{
  // setup datarecord
  // domain
  DbgAssert(*(a.domain_) == *(b.domain_));
  (*this)[FDomain] <<= domain_ = a.domain_;
  // subrecords
  DataRecord &grid = (*this)[FGrid] <<= new DataRecord;
  DataRecord &cellsize = (*this)[FCellSize] <<= new DataRecord;
  DataRecord &segments = (*this)[FSegments] <<= new DataRecord;
  // ***BUG*** here, we simply assume everything (cell positions, sizes)
  // match up, and treat one cells as an integration or upsampling of
  // the other
  for( int i=0; i<DOMAIN_NAXES; i++ )
  {
    const Cells &c = (a.ncells(i) > b.ncells(i)) ^ (resample>0) ? b : a;
    int nc = shape_[i] = c.ncells(i);
    setRecVector(grid_[i],grid[axisId(i)],nc);
    grid_[i] = c.grid_[i];
    // cell size subrecord
    setRecVector(cell_size_[i],cellsize[axisId(i)],nc);
    cell_size_[i] = c.cell_size_[i];
    // segments subrecord
    DataRecord &seg = segments[axisId(i)] <<= new DataRecord;
    int nseg = c.numSegments(i);
    setRecVector(seg_start_[i],seg[FStartIndex],nseg);
    setRecVector(seg_end_[i],seg[FEndIndex],nseg);
    seg_start_[i] = c.seg_start_[i];
    seg_end_[i]  = c.seg_end_[i];
  }
}

Cells::Cells (const Cells &other,const int ops[DOMAIN_NAXES],const int args[DOMAIN_NAXES])
: shape_(0,0)
{
  // setup datarecord
  // domain
  (*this)[FDomain] <<= domain_ = other.domain_;
  // subrecords
  DataRecord &grid = (*this)[FGrid] <<= new DataRecord;
  DataRecord &cellsize = (*this)[FCellSize] <<= new DataRecord;
  DataRecord &segments = (*this)[FSegments] <<= new DataRecord;
  for( int iaxis=0; iaxis<DOMAIN_NAXES; iaxis++ )
  {
    int op=ops[iaxis],arg=args[iaxis];
    int nc0 = other.ncells(iaxis);
    // ***BUG*** we only handle integartion/upsampling by integer factors,
    // SET_NCELLS is thus mapped to one of these operations
    if( op == SET_NCELLS )
    {
      if( arg == nc0 ) // same # of cells: no op
        op = NONE;
      else if( arg>nc0 ) // more cells: assume upsampling
      {
        FailWhen(arg%nc0,"must upsample by an integer factor");
        arg = arg/nc0;
        op  = UPSAMPLE;
      }
      else // less cells: assume integrating
      {
        FailWhen(nc0%arg,"must upsample by an integer factor");
        arg = nc0/arg;
        op  = INTEGRATE;
      }
    }
    // now, do the real operation
    const LoVec_double &grid0 = other.grid_[iaxis],
                       &csz0 = other.cell_size_[iaxis];
    if( op == NONE ) // no op: simply copy the grid
    {
      shape_[iaxis] = nc0;
      setRecVector(grid_[iaxis],grid[axisId(iaxis)],nc0);
      setRecVector(cell_size_[iaxis],cellsize[axisId(iaxis)],nc0);
      grid_[iaxis] = grid0;
      cell_size_[iaxis] = csz0;
      // copy over segments info
      DataRecord &seg = segments[axisId(iaxis)] <<= new DataRecord;
      int nseg = other.numSegments(iaxis);
      setRecVector(seg_start_[iaxis],seg[FStartIndex],nseg);
      setRecVector(seg_end_[iaxis],seg[FEndIndex],nseg);
      seg_start_[iaxis] = other.seg_start_[iaxis];
      seg_end_[iaxis]  = other.seg_end_[iaxis];
    } 
    else if( op == INTEGRATE )
    {
      int nc1 = shape_[iaxis] = nc0/arg;
      setRecVector(grid_[iaxis],grid[axisId(iaxis)],nc1);
      setRecVector(cell_size_[iaxis],cellsize[axisId(iaxis)],nc1);
      int i00=0,i01=arg-1; // original cells [i00:i01] become single cell [iaxis]
      for( int i1=0; i1<nc1; i1++,i00+=arg,i01+=arg )
      {
        double a = grid0(i00)-csz0(i00)/2,
               b = grid0(i01)+csz0(i01)/2;
        grid_[iaxis](i1) = (a+b)/2;
        cell_size_[iaxis](i1) = b-a;
      }
    }
    else if( op == UPSAMPLE )
    {
      int nc1 = shape_[iaxis] = nc0*arg;
      setRecVector(grid_[iaxis],grid[axisId(iaxis)],nc1);
      setRecVector(cell_size_[iaxis],cellsize[axisId(iaxis)],nc1);
      int i1=0;
      for( int i0=0; i0<nc0; i0++ )
      {
        double a = grid0(i0)-csz0(i0)/2,
               b = grid0(i0)+csz0(i0)/2; // original cell is [a,b]
        double sz = (b-a)/arg,           // size of upsampled cell
               x1 = a + sz/2;            // centrel of first subcell
        for( int j=0; j<arg; j++,i1++ )
        {
          grid_[iaxis](i1) = x1;  x1 += sz;
          cell_size_[iaxis](i1) = sz;
        }
      }
    }
    // after all this, recompute segments in the new grid
    recomputeSegments(iaxis);
  }
}

void Cells::setNumCells (int iaxis,int num)
{
  Assert(iaxis>=0 && iaxis<DOMAIN_NAXES);
  shape_[iaxis] = num;
  DataRecord &grid = getSubrecord((*this)[FGrid]);
  setRecVector(grid_[iaxis],grid[axisId(iaxis)],num);
  DataRecord &cellsize = getSubrecord((*this)[FCellSize]);
  setRecVector(cell_size_[iaxis],cellsize[axisId(iaxis)],num);
}   

void Cells::setCells (int iaxis,const LoVec_double &cen,const LoVec_double &size)
{
  int num = cen.size();
  shape_[iaxis] = num;
  Assert(size.size() == num);
  setNumCells(iaxis,num);
  grid_[iaxis] = cen;
  cell_size_[iaxis] = size;
  // recomputes the segments
  recomputeSegments(iaxis);
}
  
void Cells::setCells (int iaxis,const LoVec_double &cen,double size)
{
  int num = cen.size();
  shape_[iaxis] = num;
  setNumCells(iaxis,num);
  grid_[iaxis] = cen;
  cell_size_[iaxis] = size;
  // recomputes the segments
  recomputeSegments(iaxis);
}

void Cells::setCells (int iaxis,double x0,double x1,int num,double size)
{
  setNumCells(iaxis,num);
  // assign uniform spacing
  double step = (x1 - x0) / num;
  grid_[iaxis] = x0 + step/2 + step*blitz::tensor::i;
  cell_size_[iaxis] = size < 0 ? step : size;
  // assign single segment
  setNumSegments(iaxis,1);
  seg_start_[iaxis](0) = 0;
  seg_end_[iaxis]  (0) = num-1;
}

void Cells::setNumSegments (int iaxis,int nseg)
{
  DataRecord &seg = getSubrecord(getSubrecord((*this)[FSegments])[axisId(iaxis)]);
  setRecVector(seg_start_[iaxis],seg[FStartIndex],nseg);
  setRecVector(seg_end_  [iaxis],seg[FEndIndex],nseg);
}

void Cells::recomputeSegments (int iaxis)
{
  using std::fabs;
  Assert(iaxis>=0 && iaxis<DOMAIN_NAXES);
  int num = grid_[iaxis].size();
  // 1 point: always regular, assign single segment
  if( num<2 )
  {
    setNumSegments(iaxis,1);
    seg_start_[iaxis](0) = 0;
    seg_end_[iaxis]  (0) = num-1;
  }
  // 2 points or more: work out segments
  else
  {
    const LoVec_double &x = grid_[iaxis];
    const LoVec_double &h = cell_size_[iaxis];
    // epsilon value used to compare for near-equality
    double epsilon = fabs(x(0) - x(num-1))*1e-10;
    
    LoVec_int start(num),end(num);
    start(0)=0; end(0)=0;
    int iseg = 0;
    double dx0;
    double h0  = h(0);
    bool in_segment = false;
    for( int i=1; i<num; i++ )
    {
      double dx = x(i) - x(i-1);
      double h1 = h(i);
      // if step or size changes, start anew
      if( ( in_segment && fabs(dx-dx0)>epsilon )
          || fabs(h1-h0)>epsilon )
      {
        iseg++;
        start(iseg) = end(iseg) = i;
        in_segment = false;
        h0 = h1;
      }
      else // else extend current segment
      {
        dx0 = dx;
        end(iseg) = i;
        in_segment = true;
      }
    }
    // store the segment indices
    setNumSegments(iaxis,iseg+1);
    seg_start_[iaxis] = start(blitz::Range(0,iseg));
    seg_end_[iaxis]   = end(blitz::Range(0,iseg));
  }
}

// refreshes envelope domain. Should be always be called after setCells
void Cells::recomputeDomain ()
{
  int nx = grid_[0].size();
  int ny = grid_[1].size();
  double x0 = grid_[0](0) - cell_size_[0](0)/2;
  double x1 = grid_[0](nx-1) + cell_size_[0](nx-1)/2;
  double y0 = grid_[1](0) - cell_size_[1](0)/2;
  double y1 = grid_[1](ny-1) + cell_size_[1](ny-1)/2;
  
  (*this)[FDomain].replace() <<= domain_ = new Domain(x0,x1,y0,y1);
}


//##ModelId=400E530403DB
void Cells::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  try
  {
    Hook hdom = (*this)[FDomain],
         hgrid = (*this)[FGrid],
         hcs = (*this)[FCellSize],
         hseg = (*this)[FSegments];
    if( hdom.exists() )
    {
      domain_ = hdom.as_p<Domain>();
      DataRecord &rgrid = hgrid.as_wr<DataRecord>();
      DataRecord &rcs = hcs.as_wr<DataRecord>();
      DataRecord &rseg = hseg.as_wr<DataRecord>();
      DataRecord &rsegf = rseg[axisId(FREQ)].as_wr<DataRecord>();
      DataRecord &rsegt = rseg[axisId(TIME)].as_wr<DataRecord>();
      grid_[0].reference(rgrid[axisId(FREQ)].as<LoVec_double>());
      cell_size_[0].reference(rcs[axisId(FREQ)].as<LoVec_double>());
      Assert(grid_[0].size()==cell_size_[0].size());
      grid_[1].reference(rgrid[axisId(TIME)].as<LoVec_double>());
      cell_size_[1].reference(rcs[axisId(TIME)].as<LoVec_double>());
      Assert(grid_[1].size()==cell_size_[1].size());
      seg_start_[0].reference(rsegf[FStartIndex].as<LoVec_int>());
      seg_end_[0].reference(rsegf[FEndIndex].as<LoVec_int>());
      Assert(seg_start_[0].size()==seg_end_[0].size());
      seg_start_[1].reference(rsegt[FStartIndex].as<LoVec_int>());
      seg_end_[1].reference(rsegt[FEndIndex].as<LoVec_int>());
      Assert(seg_start_[1].size()==seg_end_[1].size());
      shape_[0] = grid_[0].size();
      shape_[1] = grid_[1].size();
    }
    else
    {
      // if domain is missing, everything else must be too
      FailWhen(hgrid.exists() || hcs.exists() || hseg.exists(),
               "domain not defined");
      // make empty cells
      domain_ = 0;
      for( int i=0; i<DOMAIN_NAXES; i++ )
      {
        grid_[i].free();
        cell_size_[i].free();
        seg_start_[i].free();
        seg_end_[i].free();
      }
    }
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Cells record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Cells record failed with unknown exception");
  }  
}
 
void Cells::getCellStartEnd (LoVec_double &start,LoVec_double &end,int iaxis) const
{
  int num = ncells(iaxis);
  LoVec_double hw(num);
  start.resize(num);
  end.resize(num);
  const LoVec_double &cen = center(iaxis);
  hw = cellSize(iaxis)/2;
  start = cen - hw; 
  end   = cen + hw;
}

int Cells::compare (const Cells &that) const
{
  if( domain_ == 0 ) // are we empty?
    return that.domain_ == 0 ? 0 : -1; // equal if that is empty too, else not
  // check for equality of domains & shapes
  if( that.domain_ == 0 || 
      domain() != that.domain() )
    return -1; 
  if( shape() != that.shape() )
    return 1;
  // ***BUG***
  // assume if shapes match, then we have the same grid
  // in the future we must be more intelligent, and compare grids and such
  return 0;
}

//##ModelId=400E530403DE
bool Cells::operator== (const Cells& that) const
{
  if( domain_ == 0 ) // are we empty?
    return that.domain_ == 0; // equal if that is empty too, else not
  // check for equality of domains & shapes
  if( that.domain_ == 0 || 
      domain() != that.domain() || 
      shape() != that.shape() )
    return false;
  // check axes one by one
  for( int i=0; i<DOMAIN_NAXES; i++ )
    if( any( center(i) != that.center(i) ) ||
        any( cellSize(i) != that.cellSize(i) ) )
      return false;
  // everything compared successfully
  return true;
}

//##ModelId=400E5305000E
void Cells::show (std::ostream& os) const
{
  os << "Meq::Cells [" << ncells(FREQ) << ','
     << ncells(TIME) << "]  "
     << domain() << endl;
}

DataRecord & Cells::getSubrecord (const Hook &hook)
{
  if( !hook.exists() )
    return hook <<= new DataRecord;
  else
    return hook.as_wr<DataRecord>();
}

template<class T>
void Cells::setRecVector( blitz::Array<T,1> &vec,const Hook &hook,int n)
{
  DataArray &arr = hook.replace() <<= new DataArray(typeIdOf(T),LoShape(n));
  vec.reference(arr[HIID()].as(Type2Type<blitz::Array<T,1> >()));
}

} // namespace Meq
