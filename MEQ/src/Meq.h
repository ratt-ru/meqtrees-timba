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

#ifndef MEQ_MEQ_H
#define MEQ_MEQ_H

#include <TimBase/Debug.h>
#include <TimBase/Thread/Mutex.h>
#include <TimBase/AipsppMutex.h>
#include <DMI/DMI.h>
#include <DMI/Exception.h>
    
namespace DebugMeq
{
  extern ::Debug::Context DebugContext;
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
}

namespace Meq
{
  using namespace DMI;
  
  // AIPS++ is not thread-safe, so we protect components with a mutex
  using AipsppMutex::aipspp_mutex;

  //## These exception are meant to be thrown from methods like Node::init(),
  //## getResult(), processCommands() and setStateImpl() when something goes 
  //## wrong. The type of the exception indicates whether any cleanup is 
  //## required.
  
  class FailWithCleanup : public ExceptionList
  {
    public:
      FailWithCleanup(const std::string& text,
                      const std::string& file="",int line=0,
                      const std::string& func="")
      : ExceptionList(Elem(text,file,line,func))
      {}

      FailWithCleanup(const std::string& text,const std::string &object,
                      const std::string& file="",int line=0,
                      const std::string& func="")
      : ExceptionList(Elem(text,object,file,line,func))
      {}
        
  };
  
  class FailWithoutCleanup : public ExceptionList
  {
    public:
      FailWithoutCleanup(const std::string& text,
                         const std::string& file="",int line=0,
                         const std::string& func="")
      : ExceptionList(Elem(text,file,line,func))
      {}

      FailWithoutCleanup(const std::string& text,const std::string &object,
           const std::string& file="",int line=0,
           const std::string& func="")
      : ExceptionList(Elem(text,object,file,line,func))
      {}
        
  };
  
      
}

#endif
