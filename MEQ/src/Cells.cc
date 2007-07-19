//# Cells.cc: The cells in a given domain.
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
//# $Id$


//# Includes
#include "Cells.h"
#include "MeqVocabulary.h"
#include <TimBase/Lorrays.h>
#include <DMI/NumArray.h>

namespace Meq {

static DMI::Container::Register reg(TpMeqCells,true);

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
Cells::Cells (const DMI::Record &other,int flags,int depth)
: DMI::Record()
{
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  Record::cloneOther(other,flags,depth,true);
}

    //##ModelId=3F95060B01D3
Cells::Cells (const Domain &domain,int nx,int ny,int domflags)
{
  init(&domain,domflags);
  if( nx >= 0 )
  {
    FailWhen(!domain.isDefined(0),"axis 0 not defined in Cells domain");
    FailWhen(!domain.isDefined(1),"axis 1 not defined in Cells domain");
    setCells(0,domain.start(0),domain.end(0),nx);
    setCells(1,domain.start(1),domain.end(1),ny);
  }
}

Cells::Cells (const Domain *pdom,int nx,int ny,int domflags)
{
  init(pdom,domflags);
  if( nx >= 0 )
  {
    FailWhen(!pdom->isDefined(0),"axis 0 not defined in Cells domain");
    FailWhen(!pdom->isDefined(1),"axis 1 not defined in Cells domain");
    setCells(0,pdom->start(0),pdom->end(0),nx);
    setCells(1,pdom->start(1),pdom->end(1),ny);
  }
}

void Cells::setDomain (const Domain *pdom,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  shape_.clear();
  defined_.clear();
  domain_.attach(pdom,flags);
  Record::addField(FDomain,domain_.ref_cast<BObj>(),DMI::REPLACE|Record::PROTECT);
}

void Cells::init (const Domain *pdom,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  setDomain(pdom,flags);
  // init new subrecords
  Record::addField(FGrid,new Record,DMI::REPLACE|Record::PROTECT);
  Record::addField(FCellSize,new Record,DMI::REPLACE|Record::PROTECT);
  Record::addField(FSegments,new Record,DMI::REPLACE|Record::PROTECT);
}


// creates a combination of the two grids, depending on resample>0
// (uses higher-sampled grid) or <0 (uses lower-sampled grid)
Cells::Cells (const Cells &a,const Cells &b,int resample)
{
  // setup datarecord
  Assert(a.domain() == b.domain());
  init(&a.domain(),0);
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
  init(&other.domain(),0);
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
    DMI::Record &grid = getSubrecord(FGrid);
    setRecVector(grid_[iaxis],grid[Axis::axisId(iaxis)],num);
    DMI::Record &cellsize = getSubrecord(FCellSize);
    setRecVector(cell_size_[iaxis],cellsize[Axis::axisId(iaxis)],num);
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
  Record &segments = getSubrecord(FSegments);
  Record::Hook seghook(segments,Axis::axisId(iaxis));
  Record *pseg;
  if( seghook.exists() )
    pseg = seghook.as_wp<Record>();
  else
    seghook <<= pseg = new Record;
  setRecVector(seg_start_[iaxis],(*pseg)[FStartIndex],nseg);
  setRecVector(seg_end_  [iaxis],(*pseg)[FEndIndex],nseg);
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
    double dx0 = 0;
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
  Record::addField(FDomain,domain_.deref_p(),DMI::REPLACE|Record::PROTECT);
}

//##ModelId=400E530403DB
void Cells::validateContent (bool)
{
  Thread::Mutex::Lock lock(mutex());
  shape_.reserve(Axis::MaxAxis);
  defined_.reserve(Axis::MaxAxis);
  shape_.clear();
  defined_.clear();
  try
  {
    Hook hdom   = (*this)[FDomain],
         hgrid  = (*this)[FGrid],
         hcs    = (*this)[FCellSize],
         hseg   = (*this)[FSegments];
    if( hdom.exists() )
    {
      domain_.attach(hdom.as_p<Domain>());
      const DMI::Record &rgrid = hgrid.as<DMI::Record>();
      const DMI::Record &rcs   = hcs.as<DMI::Record>();
      const DMI::Record &rseg  = hseg.as<DMI::Record>();
      // now iterate over the grid record to determine which axes are
      // defined
      for( ConstIterator iter = rgrid.begin(); iter != rgrid.end(); iter++ )
      { 
        const HIID &id = iter.id();
        FailWhen(id.size()!=1,"illegal axis ID "+id.toString());
        int iaxis = id[0].index();
        if( iaxis<0 || id.size()>1 )
          iaxis = Axis::axis(id);
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
      protectField(FDomain);
      protectField(FGrid);
      protectField(FCellSize);
      protectField(FSegments);
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
    ThrowMore(err,"validate of Cells record failed");
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

void Cells::superset (Cells::Ref &ref,const Cells &a,const Cells &b) 
{
  if( !a.domain_.valid() )
  {
    ref.attach(b);
    return;
  }
  if( !b.domain_.valid() ) 
  {
    ref.attach(a);
    return;
  }
  bool asup=true,bsup=true;
  // loop over axes to check compatibility first, and to see if one is a superset
  int iaxis;
  for( iaxis=0; iaxis<std::min(a.rank(),b.rank()); iaxis++ )
  {
    int na = a.ncells(iaxis);
    int nb = b.ncells(iaxis);
    if( na )
    {
      if( nb )
      {
        if( na != nb ||
            a.domain().start(iaxis) != b.domain().start(iaxis) ||
            a.domain().end(iaxis)   != b.domain().end(iaxis)   )
        {
          ref.detach();
          return;
        }
      }
      else // axis not b
        bsup = false;
    }
    else if( nb ) // axis not in a
      asup = false;
  }
  // check for supersets again
  if( asup && a.rank() >= b.rank() )
  {
    ref.attach(a);
    return;
  }
  if( bsup && b.rank() >= a.rank() )
  {
    ref.attach(b);
    return;
  }
  // ok, get on with the merge
  Cells & cells = ref <<= new Cells;
  for( iaxis=0; iaxis<std::max(a.rank(),b.rank()); iaxis++ )
  {
    if( a.isDefined(iaxis) )
      cells.setCells(iaxis,a.center(iaxis),a.cellSize(iaxis));
    else if( b.isDefined(iaxis) )
      cells.setCells(iaxis,b.center(iaxis),b.cellSize(iaxis));
  }
  cells.recomputeDomain();
}


int Cells::compare (const Cells &that) const
{
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

DMI::Record & Cells::getSubrecord (const HIID &id)
{
  Record *psr;
  Field * fld = Record::findField(id);
  if( fld )
  {
    return fld->ref().ref_cast<Record>().dewr();
  }
  else
  {
    Record *psr = new Record;
    Record::addField(id,psr,Record::PROTECT);
    return *psr;
  }
}

template<class T>
void Cells::setRecVector( blitz::Array<T,1> &vec,const Hook &hook,int n)
{
  DMI::NumArray &arr = hook.replace() <<= new DMI::NumArray(typeIdOf(T),LoShape(n));
  vec.reference(arr[HIID()].as(Type2Type<blitz::Array<T,1> >()));
}

} // namespace Meq
