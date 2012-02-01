//# Domain.cc: The domain for an expression
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

#include <TimBase/Debug.h>
#include <DMI/Vec.h>
#include "Domain.h"
#include "MeqVocabulary.h"

namespace Meq {

// pull in registry definitions
static int _dum = aidRegistry_Meq();
static DMI::Container::Register reg(TpMeqDomain,true);

const HIID FAxisMap = AidAxis|AidMap;

//##ModelId=3F86886E030D
Domain::Domain()
: map_attached_(false)
{
  memset(range_,0,sizeof(range_));
  memset(defined_,0,sizeof(defined_));
}

//##ModelId=3F86886E030E
Domain::Domain (const DMI::Record & rec,int flags,int depth)
: Record(rec,flags,depth),
  map_attached_(false)
{
  validateContent(false); // not recursive
}

//##ModelId=3F95060C00A7
Domain::Domain (double x1,double x2,double y1,double y2)
: map_attached_(false)
{
  memset(range_,0,sizeof(range_));
  memset(defined_,0,sizeof(defined_));
  defineAxis(0,x1,x2);
  defineAxis(1,y1,y2);
}

void Domain::defineAxis (int iaxis,double a1,double a2)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(iaxis<0 || iaxis>=Axis::MaxAxis,"illegal axis argument");
  //// FailWhen(a1>=a2,"segment start must be < end");
  // swap a1/a2 around if a2>=a1
  if( a1==a2 )
    a1 -= 1e-6;
  else if( a1>a2 )
  { double tmp=a1; a1=a2;  a2 = tmp; }
  range_[iaxis][0] = a1;
  range_[iaxis][1] = a2;
  defined_[iaxis]  = true;
  // add to record
  Record::addField(Axis::axisId(iaxis),new DMI::Vec(Tpdouble,2,range_[iaxis]),DMI::REPLACE|Record::PROTECT);
  // add axis map if not default
  if( !Axis::isDefaultMap() && !map_attached_ )
  {
    map_attached_ = true;
    ObjRef ref;  Axis::getAxisIds(ref);
    Record::addField(FAxisMap,ref,Record::PROTECT);
  }
}

void Domain::setDomainId (int t0,int t1,int dt,int nt,int f0,int f1,int df,int nf)
{
  domain_id_.resize(8);
  domain_id_[0] = t0;
  domain_id_[1] = t1;
  domain_id_[2] = dt;
  domain_id_[3] = nt;
  domain_id_[4] = f0;
  domain_id_[5] = f1;
  domain_id_[6] = df;
  domain_id_[7] = nf;
  (*this)[FDomainId] = domain_id_;
}

bool Domain::getDomainId (int &t0,int &t1,int &dt,int &nt,int &f0,int &f1,int &df,int &nf)
{
  if( domain_id_.empty() )
    return false;
  t0 = domain_id_[0];
  t1 = domain_id_[1];
  dt = domain_id_[2];
  nt = domain_id_[3];
  f0 = domain_id_[4];
  f1 = domain_id_[5];
  df = domain_id_[6];
  nf = domain_id_[7];
  return true;
}


//##ModelId=400E5305010B
void Domain::validateContent (bool)
{
  Thread::Mutex::Lock lock(mutex());
  memset(range_,0,sizeof(range_));
  memset(defined_,0,sizeof(defined_));
  try
  {
    if( (*this)[FDomainId].get_vector<int>(domain_id_) )
    {
      FailWhen(!domain_id_.empty() && domain_id_.size() != 8,"domain ID must be a vector of 8 integers");
    }
    else
      domain_id_.resize(0);
    Record::Field * paxismap = findField(FAxisMap);
    map_attached_ = (paxismap != 0);
    // change map using domain record, if needed
    if( map_attached_ )
    {
      Axis::setAxisMap(paxismap->ref().as<DMI::Vec>());
      paxismap->protect(true);
    }
    // now iterate over all domain elements
    for( Iterator iter = Record::begin(); iter != Record::end(); iter++ )
    { 
      const HIID &id = iter.id();
      if( id == FAxisMap || id == FDomainId ) // skip this one
        continue;
// NB: not sure what I was thinking of here, why can't we have longer axis IDs?
//      FailWhen(id.size()!=1,"illegal axis ID "+id.toString());
      const BObj *pobj = iter.ref().deref_p();
      const Container *pcont = dynamic_cast<const Container*>(pobj);
      FailWhen(!pcont,"illegal content of type "+pobj->objectType().toString()+" for axis "+id.toString());
      int iaxis = id[0].index();
      if( iaxis<0 || id.size()>1 )
        iaxis = Axis::axis(id);
      int size;
      const double *a = (*pcont)[HIID()].as_p<double>(size);
      FailWhen(size!=2,"bad axis specification for "+id.toString());
      FailWhen(a[0]>=a[1],"segment start must be < end");
      range_[iaxis][0] = a[0];
      range_[iaxis][1] = a[1];
      defined_[iaxis]  = true;
      iter.protect(); 
    }
    // add axis map if not default
    if( !Axis::isDefaultMap() && !map_attached_ )
    {
      map_attached_ = true;
      ObjRef ref;  Axis::getAxisIds(ref);
      Record::addField(FAxisMap,ref,Record::PROTECT);
    }
  }
  catch( std::exception &err )
  {
    std::cout<<"failed Domain record: "<<sdebug(10)<<endl;
    cdebug(1)<<"failed Domain record: "<<sdebug(10)<<endl;
    ThrowMore(err,"validate of Domain record failed");
  }
  catch( ... )
  {
    std::cout<<"failed Domain record: "<<sdebug(10)<<endl;
    cdebug(1)<<"failed Domain record: "<<sdebug(10)<<endl;
    Throw("validate of Domain record failed with unknown exception");
  }  
}

bool Domain::supersetOfProj (const Domain &other) const
{
// OMS 28/10/2009: commented out mutexes, not needed for const objects, surely
//  Thread::Mutex::Lock lock(mutex());
//  Thread::Mutex::Lock lock2(other.mutex());
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( isDefined(i) &&
        ( !other.isDefined(i) || start(i) > other.start(i) || end(i) < other.end(i) ) )
      return false;
  return true;
}

Domain Domain::envelope (const Domain &a,const Domain &b)
{
// OMS 28/10/2009: commented out mutexes, not needed for const objects, surely
//  Thread::Mutex::Lock lock(a.mutex());
//  Thread::Mutex::Lock lock2(b.mutex());
  Domain out;
  using std::min;
  using std::max;
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    if( a.isDefined(i) )
    {
      if( b.isDefined(i) )
        out.defineAxis(i,min(a.start(i),b.start(i)),max(a.end(i),b.end(i)));
      else
        out.defineAxis(i,a.start(i),a.end(i));
    }
    else if( b.isDefined(i) )
      out.defineAxis(i,b.start(i),b.end(i));
  }
  return out;
}

void Domain::expandToEnvelope (const Domain &other)
{
  Thread::Mutex::Lock lock(mutex());
  using std::min;
  using std::max;
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    // do nothing if axis not defined in other
    if( other.isDefined(i) )
    {
       // if we do define it, check if it needs to be expanded
      if( isDefined(i) )
      {
        double x1 = min(start(i),other.start(i));
        double x2 = max(end(i),other.end(i));
        if( x1 != start(i) || x2 != end(i) )
          defineAxis(i,x1,x2);
      } 
      // we do not define it -- simply copy it over then
      else 
        defineAxis(i,other.start(i),other.end(i));
    }
  }
}



//##ModelId=400E53050125
void Domain::show (std::ostream& os) const
{
  os << "Meq::Domain [";
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( defined_[i] )
       os << Axis::axisId(i) << " " << start(i) << ":" << end(i) << ',';
  os << "]\n";
}


} // namespace Meq
