//# Domain.cc: The domain for an expression
//#
//# Copyright (C) 2002
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

#include <Common/Debug.h>
#include <DMI/DataField.h>
#include "Domain.h"
#include "MeqVocabulary.h"

namespace Meq {

// pull in registry definitions
static int _dum = aidRegistry_Meq();
static NestableContainer::Register reg(TpMeqDomain,True);

//##ModelId=3F86886E030D
Domain::Domain()
{
  memset(range_,0,sizeof(range_));
  memset(defined_,0,sizeof(defined_));
}

//##ModelId=3F86886E030E
Domain::Domain (const DataRecord & rec,int flags)
: DataRecord(rec,(flags&~DMI::WRITE)|DMI::DEEP|DMI::READONLY)
{
  validateContent();
}

//##ModelId=3F95060C00A7
Domain::Domain (double x1,double x2,double y1,double y2)
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
  FailWhen(a1>=a2,"segment start must be < end");
  range_[iaxis][0] = a1;
  range_[iaxis][1] = a2;
  defined_[iaxis]  = true;
  // add to record
  (*this)[Axis::name(iaxis)] <<= new DataField(Tpdouble,2,range_[iaxis]);
}


void Domain::revalidateContent ()
{
  protectAllFields();
}  

//##ModelId=400E5305010B
void Domain::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  memset(range_,0,sizeof(range_));
  memset(defined_,0,sizeof(defined_));
  try
  {
    HIID id;
    NCRef ncref;
    Iterator iter = initFieldIter();
    while( getFieldIter(iter,id,ncref) )
    { 
      FailWhen(id.size()!=1,"illegal axis ID "+id.toString());
      int iaxis = id[0].index();
      if( iaxis<0 )
      {
        iaxis = Axis::number(id[0]);
        FailWhen(iaxis<0,"unknown axis ID "+id.toString());
      }
      int size;
      const double *a = (*ncref)[HIID()].as_p<double>(size);
      FailWhen(size!=2,"bad axis specification for "+id.toString());
      FailWhen(a[0]>=a[1],"segment start must be < end");
      range_[iaxis][0] = a[0];
      range_[iaxis][1] = a[1];
      defined_[iaxis]  = true;
    }
    protectAllFields();
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Domain field failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Domain field failed with unknown exception");
  }  
}

bool Domain::supersetOfProj (const Domain &other) const
{
  Thread::Mutex::Lock lock(mutex());
  Thread::Mutex::Lock lock2(other.mutex());
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( isDefined(i) &&
        ( !other.isDefined(i) || start(i) > other.start(i) || end(i) < other.end(i) ) )
      return false;
  return true;
}

Domain Domain::envelope (const Domain &a,const Domain &b)
{
  Thread::Mutex::Lock lock(a.mutex());
  Thread::Mutex::Lock lock2(b.mutex());
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

//##ModelId=400E53050125
void Domain::show (std::ostream& os) const
{
  os << "Meq::Domain [";
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( defined_[i] )
       os << Axis::name(i) << " " << start(i) << ":" << end(i) << ',';
  os << "]\n";
}


} // namespace Meq
