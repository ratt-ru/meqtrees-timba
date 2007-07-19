//# Domain.h: The domain for an expression
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

#ifndef MEQ_DOMAIN_H
#define MEQ_DOMAIN_H

#include <DMI/Record.h>
#include <MEQ/TID-Meq.h>
#include <MEQ/Axis.h>

#pragma types #Meq::Domain

#pragma aid ndim axes Axis Map

namespace Meq 
{ 

//##ModelId=3F86886E0183
class Domain : public DMI::Record
{
public:
  typedef DMI::CountedRef<Domain> Ref;

  // Create a time,frequency default domain of -1:1,-1:1..
    //##ModelId=3F86886E030D
  Domain();

  // Create from an existing data record (also serves as copy constructor)
    //##ModelId=3F86886E030E
  Domain (const DMI::Record &,int flags=0,int depth=0);

  // Shortcut to create a 2D domain (along axis 0 and 1)
    //##ModelId=3F95060C00A7
  Domain (double x1,double x2,double y1,double y2);
  
  // adds an axis to the Domain definition
  void defineAxis (int iaxis,double a1,double a2);

    //##ModelId=400E530500F5
  virtual DMI::TypeId objectType () const
  { return TpMeqDomain; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E530500F9
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new Domain(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Domain is made from a DMI::Record
    //##ModelId=400E5305010B
  virtual void validateContent (bool recursive);

  double start (int iaxis) const
  {
    DbgFailWhen(iaxis<0 || iaxis>=Axis::MaxAxis,"illegal axis argument");
    return range_[iaxis][0];
  }
  
  double end   (int iaxis) const
  {
    DbgFailWhen(iaxis<0 || iaxis>=Axis::MaxAxis,"illegal axis argument");
    return range_[iaxis][1];
  }
  
  bool isDefined (int iaxis) const
  {
    DbgFailWhen(iaxis<0 || iaxis>=Axis::MaxAxis,"illegal axis argument");
    return defined_[iaxis];
  }

    //##ModelId=400E5305010E
  bool operator == (const Domain& other) const
  { 
    return memcmp(range_,other.range_,sizeof(range_)) == 0; 
  }
  
    //##ModelId=400E5305011A
  bool operator!= (const Domain& other) const
  { return !(*this == other); }

//   // returns true if this domain is a subset of other
//   bool subsetOf (const Domain &other) const
//   { return 
//       start(FREQ) >= other.start(FREQ) && end(FREQ) <= other.end(FREQ) &&
//       start(TIME) >= other.start(TIME) && end(TIME) <= other.end(TIME); }
  
  // returns true if this domain is a superset of the _projection_ of the other
  // domain onto the axes defined by this domain. I.e.:
  // 1. All axes defined by this domain must be defined by other;
  // 2. The extend of each axis in this must be a superset of the other's extent
  bool supersetOfProj (const Domain &other) const;
  
  // returns the envelope of two domains
  static Domain envelope (const Domain &a,const Domain &b);
   
  // returns the envelope of this and the other domain
  Domain envelope (const Domain &other) const
  { return envelope(*this,other); }
  
  // print to stream
    //##ModelId=400E53050125
  void show (std::ostream&) const;

private:
  DMI::Record::protectField;  
  DMI::Record::unprotectField;  
  DMI::Record::begin;  
  DMI::Record::end;  
  DMI::Record::as;
    
    //##ModelId=3F86886E02F8
  double range_[Axis::MaxAxis][2];
  bool   defined_[Axis::MaxAxis];
  
  bool map_attached_;
};

} // namespace Meq

inline std::ostream& operator << (std::ostream& os, const Meq::Domain& dom)
{
  dom.show(os);
  return os;
}

#endif
