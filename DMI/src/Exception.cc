//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include <DMI/Exception.h>
#include <DMI/Record.h>
#include <DMI/List.h>
#include <DMI/AID-DMI.h>
#include <sstream>
      
namespace DMI
{
  
ExceptionList::Elem::Elem (const DMI::Record &rec)
: Exception(rec[AidMessage].as<string>("unknown error"),
            rec[AidObject].as<string>(""),
            rec[AidFilename].as<string>(""),
            rec[AidLineNo].as<int>(0),
            rec[AidFunction].as<string>("")),
  type_(    rec[AidType].as<string>("Exception"))
{
}

ExceptionList::ExceptionList ()
: Exception("ExceptionList")
{
}

const char* ExceptionList::what() const throw()
{
  what_ = Debug::ssprintf("<%d exceptions>",list_.size());
  return what_.c_str();
}

// creates list of exception records
ObjRef ExceptionList::makeList () const
{
  DMI::List *plist = new DMI::List;
  ObjRef res(plist);
  
  // add exceptions to list
  for( std::list<Elem>::const_iterator iter = list_.begin(); iter != list_.end(); iter++ )
    plist->addBack(exceptionToObj(*iter));
  
  return res;
}

const std::string ExceptionList::message() const
{
  if( list_.empty() )
    return "ExceptionList: empty\n";
  std::ostringstream oss;
  oss << "ExceptionList (" << list_.size() << " errors):\n";
  for( std::list<Elem>::const_iterator iter = list_.begin(); iter != list_.end(); iter++ )
    oss << "  " << *iter;
  return oss.str();
}

ExceptionList & ExceptionList::add (const std::exception &exc)
{
  const ExceptionList *plist = dynamic_cast<const ExceptionList *>(&exc);
  if( plist )
  {
    std::list<Elem>::const_iterator iter = plist->list_.begin();
    for( ; iter != plist->list_.end(); iter++ )
      list_.push_back(*iter);
    return *this;
  }
  const LOFAR::Exception *le = dynamic_cast<const LOFAR::Exception *>(&exc);
  if( le )
    list_.push_back(Elem(*le));
  else
    list_.push_back(Elem(exc));
  return *this;
}

ExceptionList & ExceptionList::add (const ObjRef &ref)
{
  if( !ref.valid() )
    return *this;
  const BObj &obj = *ref;
  // a record? treat as fail-record
  const DMI::Record *prec = dynamic_cast<const DMI::Record *>(&obj);
  if( prec )
  {
    list_.push_back(Elem(*prec)); 
    return *this;
  }
  // a list? treat as list of fail-records
  const DMI::List *plist = dynamic_cast<const DMI::List *>(&obj);
  if( plist )
    return add(*plist);
  list_.push_back(Elem("unknown error")); 
  return *this;
}

ExceptionList & ExceptionList::add (const DMI::List &list)
{
  for( int i=0; i<list.size(); i++ )
    add(list.get(i));
  return *this;
}

ObjRef exceptionToObj (const LOFAR::Exception &exc)
{
  DMI::Record * prec = new DMI::Record;
  ObjRef res(prec);
  (*prec)[AidMessage]  = exc.text();
  if( !exc.file().empty() )
  {
    (*prec)[AidFilename] = exc.file();
    (*prec)[AidLineNo]   = exc.line();
  }
  if( !exc.function().empty() )
    (*prec)[AidFunction] = exc.function();
  if( !exc.object().empty() )
    (*prec)[AidObject]   = exc.object();
  (*prec)[AidType] = exc.type();
  return res;
}
  
ObjRef exceptionToObj (const std::exception &exc)
{
  // exception list
  const ExceptionList *pl = dynamic_cast<const ExceptionList*>(&exc);
  if( pl )
    return pl->makeList();
  // LOFAR exception with origin info
  const LOFAR::Exception *pe = dynamic_cast<const LOFAR::Exception *>(&exc);
  if( pe )
    return exceptionToObj(*pe);
  // else just return standard record with only a message field
  DMI::Record * prec = new DMI::Record;
  ObjRef res(prec);
  (*prec)[AidMessage] = exc.what();
  (*prec)[AidType] = "std::exception";
  return res;
}

std::string exceptionToString (const std::exception &exc)
{
  const LOFAR::Exception *pe = dynamic_cast<const LOFAR::Exception *>(&exc);
  if( pe )
    return pe->message();
  return std::string(exc.what()) + "\n";
}

};
