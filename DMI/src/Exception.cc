#include <DMI/Exception.h>
#include <DMI/Record.h>
#include <DMI/List.h>
#include <DMI/AID-DMI.h>
#include <sstream>
      
namespace DMI
{
  
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
