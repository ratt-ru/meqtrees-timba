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

//##ModelId=3F86886E02C1
Cells::Cells ()
{
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
}

//##ModelId=3F86886E02D1
Cells::~Cells()
{
}


//##ModelId=3F86886E02C8
Cells::Cells (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth)
{
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  validateContent();
}

Cells::Cells (const Domain& domain)
{
  init(domain);
}

    //##ModelId=3F95060B01D3
Cells::Cells (const Domain& domain,int nx,int ny)
{
  init(domain);
  FailWhen(!domain.isDefined(0),"axis 0 not defined in Cells domain");
  FailWhen(!domain.isDefined(1),"axis 1 not defined in Cells domain");
  setCells(0,domain.start(0),domain.end(0),nx);
  setCells(1,domain.start(1),domain.end(1),ny);
}

void Cells::setDomain (const Domain &domain)
{
  Thread::Mutex::Lock lock(mutex());
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  shape_.clear();
  defined_.clear();
  if( domain.refCount() )
    domain_.attach(domain,DMI::READONLY);
  else
    domain_.attach(new Domain(domain),DMI::ANON|DMI::READONLY);
  (*this)[FDomain] <<= domain_.copy();
}

void Cells::init (const Domain& domain)
{
  Thread::Mutex::Lock lock(mutex());
  setDomain(domain);
  // grid subrecord
  (*this)[FGrid] <<= new DataRecord;
  (*this)[FCellSize] <<= new DataRecord;
  (*this)[FSegments] <<= new DataRecord;
}


// creates a combination of the two grids, depending on resample>0
// (uses higher-sampled grid) or <0 (uses lower-sampled grid)
Cells::Cells (const Cells &a,const Cells &b,int resample)
{
  // setup datarecord
  Assert(a.domain() == b.domain());
  init(a.domain());
  shape_.resize(std::max(a.shape_.size(),b.shape_.size()));
  defined_.resize(shape_.size());
  // ***BUG*** here, we simply assume everything (cell positions, sizes)
  // match up, and treat one cells as an integration or upsampling of
  // the other
  for( int iaxis=0; iaxis<Axis::MaxAxis; iaxis++ )
  {
    const Cells &c = (a.ncells(iaxis) > b.ncells(iaxis)) ^ (resample>0) ? b : a;
    int np = c.ncells(iaxis);
    setNumCells(iaxis,np);
    if( np )
    {
      grid_[iaxis] = c.grid_[iaxis];
      cell_size_[iaxis] = c.cell_size_[iaxis];
      // segments subrecord
      setNumSegments(iaxis,c.numSegments(iaxis));
      seg_start_[iaxis] = c.seg_start_[iaxis];
      seg_end_[iaxis]   = c.seg_end_[iaxis];
    }
  }
}

Cells::Cells (const Cells &other,const int ops[Axis::MaxAxis],const int args[Axis::MaxAxis])
{
  // setup datarecord
  init(other.domain());
  shape_.resize(other.shape_.size());
  defined_ = other.defined_;
  for( int iaxis=0; iaxis<Axis::MaxAxis; iaxis++ )
  {
    int op=ops[iaxis],arg=args[iaxis];
    int np = other.ncells(iaxis);
    if( np )
    {
      // ***BUG*** we only handle integartion/upsampling by integer factors,
      // SET_NCELLS is thus mapped to one of these operations
      if( op == SET_NCELLS )
      {
        if( arg == np ) // same # of cells: no op
          op = NONE;
        else if( arg>np ) // more cells: assume upsampling
        {
          FailWhen(arg%np,"must upsample by an integer factor");
          arg = arg/np;
          op  = UPSAMPLE;
        }
        else // less cells: assume integrating
        {
          FailWhen(np%arg,"must upsample by an integer factor");
          arg = np/arg;
          op  = INTEGRATE;
        }
      }
      // now, do the real operation
      const LoVec_double &grid0 = other.grid_[iaxis],
                         &csz0 = other.cell_size_[iaxis];
      if( op == NONE ) // no op: simply copy the grid
      {
        setNumCells(iaxis,np);
        grid_[iaxis] = grid0;
        cell_size_[iaxis] = csz0;
        // copy over segments info
        setNumSegments(iaxis,other.numSegments(iaxis));
        seg_start_[iaxis] = other.seg_start_[iaxis];
        seg_end_[iaxis]   = other.seg_end_[iaxis];
      } 
      else if( op == INTEGRATE )
      {
        int np1 = np/arg;
        setNumCells(iaxis,np1);
        int i00=0,i01=arg-1; // original cells [i00:i01] become single cell [iaxis]
        for( int i1=0; i1<np1; i1++,i00+=arg,i01+=arg )
        {
          double a = grid0(i00)-csz0(i00)/2,
                 b = grid0(i01)+csz0(i01)/2;
          grid_[iaxis](i1) = (a+b)/2;
          cell_size_[iaxis](i1) = b-a;
        }
        recomputeSegments(iaxis);
      }
      else if( op == UPSAMPLE )
      {
        int np1 = np*arg;
        setNumCells(iaxis,np1);
        int i1=0;
        for( int i0=0; i0<np; i0++ )
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
        recomputeSegments(iaxis);
      }
    } // endif( np )
    else // else no cells along this axis 
      setNumCells(iaxis,0);
  }
}

void Cells::setAxisShape (int iaxis,int num)
{
  Thread::Mutex::Lock lock(mutex());
  int sz = shape_.size();
  if( iaxis >= sz )
  {
    shape_.resize(iaxis+1);
    defined_.resize(iaxis+1);
    for( ; sz<iaxis; sz++ )
    {
      shape_[sz]   = 1;
      defined_[sz] = false;
    }
  }
  // assign num -- 0 is assigned as '1' in shape, and defined is set to false
  shape_[iaxis]  = num ? num : 1;
  defined_[iaxis]   = num;
}

void Cells::setNumCells (int iaxis,int num)
{
  Thread::Mutex::Lock lock(mutex());
  Assert(iaxis>=0 && iaxis<Axis::MaxAxis);
  setAxisShape(iaxis,num);
  if( num )
  {
    DataRecord &grid = getSubrecord((*this)[FGrid]);
    setRecVector(grid_[iaxis],grid[Axis::name(iaxis)],num);
    DataRecord &cellsize = getSubrecord((*this)[FCellSize]);
    setRecVector(cell_size_[iaxis],cellsize[Axis::name(iaxis)],num);
  }
  else
  {
    grid_[iaxis].free();
    cell_size_[iaxis].free();
    seg_start_[iaxis].free();
    seg_end_[iaxis].free();
  }
}

void Cells::setCells (int iaxis,const LoVec_double &cen,const LoVec_double &size)
{
  Thread::Mutex::Lock lock(mutex());
  int num = cen.size();
  Assert(size.size() == num);
  setNumCells(iaxis,num);
  grid_[iaxis] = cen;
  cell_size_[iaxis] = size;
  // recomputes the segments
  recomputeSegments(iaxis);
}
  
void Cells::setCells (int iaxis,const LoVec_double &cen,double size)
{
  Thread::Mutex::Lock lock(mutex());
  int num = cen.size();
  setNumCells(iaxis,num);
  grid_[iaxis] = cen;
  cell_size_[iaxis] = size;
  // recomputes the segments
  recomputeSegments(iaxis);
}

void Cells::setCells (int iaxis,double x0,double x1,int num,double size)
{
  Thread::Mutex::Lock lock(mutex());
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

void Cells::setEnumCells (int iaxis,int num)
{
  Thread::Mutex::Lock lock(mutex());
  setNumCells(iaxis,num);
  grid_[iaxis] = blitz::tensor::i;
  cell_size_[iaxis] = 0;
  // assign single segment
  setNumSegments(iaxis,1);
  seg_start_[iaxis](0) = 0;
  seg_end_[iaxis]  (0) = num-1;
}

void Cells::setNumSegments (int iaxis,int nseg)
{
  Thread::Mutex::Lock lock(mutex());
  DataRecord &seg = getSubrecord(getSubrecord((*this)[FSegments])[Axis::name(iaxis)]);
  setRecVector(seg_start_[iaxis],seg[FStartIndex],nseg);
  setRecVector(seg_end_  [iaxis],seg[FEndIndex],nseg);
}

void Cells::recomputeSegments (int iaxis)
{
  Thread::Mutex::Lock lock(mutex());
  using std::fabs;
  Assert(iaxis>=0 && iaxis<Axis::MaxAxis);
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
  Thread::Mutex::Lock lock(mutex());
  Domain *newdom = new Domain;
  domain_ <<= newdom;
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    int np = ncells(i);
    if( np )
    {
      double a0 = grid_[i](0)    - cell_size_[i](0)/2;
      double a1 = grid_[i](np-1) + cell_size_[i](np-1)/2;
      newdom->defineAxis(i,a0,a1);
    }
  }
  domain_.change(DMI::READONLY);
  (*this)[FDomain].replace() <<= domain_.copy();
}

void Cells::privatize (int flags,int depth)
{
  // if deep-privatizing, then detach shortcuts -- they will be reattached 
  // by validateContent()
//  if( flags&DMI::DEEP || depth>0 )
//  {
//    domain_.detach();
  DataRecord::privatize(flags,depth);
//  }
}


void Cells::revalidateContent ()
{
  protectAllFields();
}

//##ModelId=400E530403DB
void Cells::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  shape_.clear();
  defined_.clear();
  try
  {
    protectAllFields();
    Hook hdom   = (*this)[FDomain],
         hgrid  = (*this)[FGrid],
         hcs    = (*this)[FCellSize],
         hseg   = (*this)[FSegments];
    if( hdom.exists() )
    {
      domain_.attach(hdom.as_p<Domain>());
      const DataRecord &rgrid = hgrid.as<DataRecord>();
      const DataRecord &rcs   = hcs.as<DataRecord>();
      const DataRecord &rseg  = hseg.as<DataRecord>();
      // now loop over the grid record to determine which axes are
      // defined
      HIID id;
      NCRef ncref;
      Iterator iter = rgrid.initFieldIter();
      while( rgrid.getFieldIter(iter,id,ncref) )
      { 
        FailWhen(id.size()!=1,"illegal axis ID "+id.toString());
        int iaxis = id[0].index();
        if( iaxis<0 )
        {
          iaxis = Axis::number(id[0]);
          FailWhen(iaxis<0,"unknown axis ID "+id.toString());
        }
        // check that this axis is defined in the domain
        FailWhen(!domain_->isDefined(iaxis),"axis "+id.toString()+" not defined in domain");
        // set grid centers and axis shape
        grid_[iaxis].reference(rgrid[id].as<LoVec_double>());
        int np = grid_[iaxis].size();
        setAxisShape(iaxis,np);
        // now, the axis must be present in all other records, and shapes must match
        cell_size_[iaxis].reference(rcs[id].as<LoVec_double>());
        Assert(cell_size_[iaxis].size() == np);
        seg_start_[iaxis].reference(rseg[id][FStartIndex].as<LoVec_int>());
        seg_end_[iaxis].reference(rseg[id][FEndIndex].as<LoVec_int>());
        Assert(seg_start_[iaxis].size()==seg_end_[iaxis].size());
      }
    }
    else
    {
      // if domain is missing, everything else must be too
      FailWhen(hgrid.exists() || hcs.exists() || hseg.exists(),
               "domain not defined");
      // make empty cells
      domain_.detach();
      for( int i=0; i<Axis::MaxAxis; i++ )
        setNumCells(i,0);
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
  Thread::Mutex::Lock lock(mutex());
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
  Thread::Mutex::Lock lock(mutex());
  Thread::Mutex::Lock lock2(that.mutex());
  if( !domain_.valid() ) // are we empty?
    return !that.domain_.valid(); // equal if that is empty too, else not
  // check for equality of domains & shapes
  if( !that.domain_.valid() || 
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
  Thread::Mutex::Lock lock(mutex());
  Thread::Mutex::Lock lock2(that.mutex());
  if( compare(that) )
    return false;
  // check axes one by one
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( any( center(i) != that.center(i) ) ||
        any( cellSize(i) != that.cellSize(i) ) )
      return false;
  // everything compared successfully
  return true;
}

//##ModelId=400E5305000E
void Cells::show (std::ostream& os) const
{
  Thread::Mutex::Lock lock(mutex());
  os << "Meq::Cells [" << shape_ << "]\n";
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
