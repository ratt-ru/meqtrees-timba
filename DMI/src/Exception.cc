#include <DMI/Exception.h>
#include <DMI/Record.h>
#include <DMI/List.h>
#include <DMI/AID-DMI.h>
      
namespace DMI
{
  
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

ObjRef exceptionToObj (const LOFAR::Exception &exc)
{
  DMI::Record * prec = new DMI::Record;
  ObjRef res(prec);
  (*prec)[AidMessage]  = exc.text();
  (*prec)[AidFilename] = exc.file();
  (*prec)[AidLineNo]   = exc.line();
  (*prec)[AidFunction] = exc.function();
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
  (*prec)[AidMessage]  = exc.what();
  return res;
}
  
};
