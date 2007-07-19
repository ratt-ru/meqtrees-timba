//  Exception.h: DMI exception class
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#ifndef DMI_Exceptions_h
#define DMI_Exceptions_h 1

#include <TimBase/Exception.h>
#include <DMI/BObj.h>

#include <list>

#pragma aids Message Filename LineNo Function Object Type
    
namespace DMI
{
  class Record;
  class List;
  
  // ExceptionList is used to accumulate list of exceptions.
  //
  class ExceptionList : public LOFAR::Exception
  {
    public:
      // Elem represents an exception object with the type information
      // encoded as an actual data member. Elems may be created from
      // std::exception or LOFAR::Exceptions.
      class Elem : public LOFAR::Exception
      {
        public:
            Elem(const std::string& text,
                 const std::string& file="",int line=0,
                 const std::string& func="",
                 const std::string& type="Exception")
            : Exception(text,file,line,func),
              type_(type)
            {}
        
            Elem(const std::string& text,const std::string &object,
                 const std::string& file="",int line=0,
                 const std::string& func="",
                 const std::string& type="Exception")
            : Exception(text,object,file,line,func),
              type_(type)
            {}
            
            Elem (const Exception &exc)
            : Exception(exc),
              type_(exc.type())
            {}

            Elem (const std::exception &exc)
            : Exception(exc.what()),
              type_("std")
            {}
            
            // Constructs from a fail-record. A fail-record should be 
            // similar to what is produced by exceptionToObj(), and can
            // contain the following fields (all optional):
            //   Message,Object,Filename,Function,Type  (strings)
            //   LineNo (int)
            Elem (const DMI::Record &rec);
            
            virtual ~Elem () throw()
            {}

            virtual const std::string & type() const 
            { return type_; }
            
        private:
            std::string type_;
      };
        
      ExceptionList ();
    
      // create  list from an exception
      ExceptionList (const std::exception &exc)
      : Exception("ExceptionList")
      { add(exc); }
      
      ExceptionList (const LOFAR::Exception &exc)
      : Exception("ExceptionList")
      { add(exc); }
      
      // create  list from an exception element
      ExceptionList (const Elem &elem)
      : Exception("ExceptionList")
      { add(elem); }
      
      virtual ~ExceptionList () throw()
      {}
      
      // Return the class type of the exception.
      virtual const std::string& type() const 
      {
        static const std::string type_("ExceptionList");
        return type_;
      }
      
      virtual const char* what() const throw();
      
      virtual const std::string message() const;
      
      // adds an exception to the list
      ExceptionList & add (const std::exception &exc);
      
      // adds a LOFAR exception to the list
      ExceptionList & add (const Exception &exc)
      { 
        list_.push_back(Elem(exc)); 
        return *this;
      }
      
      // adds an object to the list. Object should be an exception record
      // or list (such as one produced by exceptionToObj()), otherwise an 
      // "unknown exception" is added.
      ExceptionList & add (const ObjRef &obj);
      
      // adds a list of fail-objects to the list. 
      ExceptionList & add (const DMI::List &list);
      
      int size () const
      { return list_.size(); }
      
      bool empty () const
      { return list_.empty(); }
      
      void clear ()
      { list_.clear(); }
      
      // creates list of exception records
      ObjRef makeList () const;
      
    private:
      std::list<Elem> list_;
    
      mutable std::string what_;
    
  };

  // converts exception (or list) to object (list or record) depending on type
  ObjRef exceptionToObj (const std::exception &exc);
  
  std::string exceptionToString (const std::exception &exc);
  
// ThrowMoreExcObj(exc0,exc)
// Given a previous exception (exc0) and a new exception (exc), throws
// an ExceptionList containing both. If exc0 is already an exception list,
// the new exception is added on, and the list is rethrown
#define ThrowMoreExcObj(exc0,exc) { \
  std::exception * pexc0 = &exc0; \
  DMI::ExceptionList *pelist = dynamic_cast<DMI::ExceptionList *>(pexc0); \
  if( pelist ) \
    throw pelist->add(exc); \
  DMI::ExceptionList elist(exc0); \
  throw elist.add(exc); \
}
  
// ThrowMoreExc(exc0,msg,exctype)
// Forms a new exception of type exctype from given message, and calls the
// previous macro to add it to previous exception and rethrow
#define ThrowMoreExc(exc0,msg,exctype) \
  ThrowMoreExcObj(exc0,exctype(msg,sdebug(),__HERE__));
// ThrowMoreExc1(exc0,msg,exctype)
// version to be called in context when sdebug() is not available (i.e. not
// from within a standand object)
#define ThrowMoreExc1(exc0,msg,exctype) \
  ThrowMoreExcObj(exc0,exctype(msg,__HERE__));

// ThrowMore(exc0,msg)
// Like ThrowMoreExc(), but throws a LOFAR::Exception
#define ThrowMore(exc,msg) ThrowMoreExc(exc,msg,LOFAR::Exception)
#define ThrowMore1(exc,msg) ThrowMoreExc1(exc,msg,LOFAR::Exception)


};

#endif
