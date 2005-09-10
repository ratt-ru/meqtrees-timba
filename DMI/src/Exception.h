//  Exception.h: DMI exception class
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
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

#include <Common/Exception.h>
#include <DMI/BObj.h>

#include <list>

#pragma aids Message Filename LineNo Function 
    
namespace DMI
{
  
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
            Elem (const Exception &exc)
            : Exception(exc),
              type_(exc.type())
            {}

            Elem (const std::exception &exc)
            : Exception(exc.what()),
              type_("std")
            {}
            
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
      
      // adds an exception to the list
      void add (const std::exception &exc)
      {
        const LOFAR::Exception *le = dynamic_cast<const LOFAR::Exception *>(&exc);
        if( le )
          list_.push_back(Elem(*le));
        else
          list_.push_back(Elem(exc));
      }
      
      // adds an exception to the list
      void add (const Exception &exc)
      { 
        list_.push_back(Elem(exc)); 
      }
      
      // creates list of exception records
      ObjRef makeList () const;
      
    private:
      std::list<Elem> list_;
    
      mutable std::string what_;
    
  };
  
  ObjRef exceptionToObj (const std::exception &exc);
};

#endif
