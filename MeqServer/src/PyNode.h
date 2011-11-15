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

#ifndef MEQSERVER_SRC_PYNODE_H
#define MEQSERVER_SRC_PYNODE_H
    
#include <MEQ/Node.h>
#include <MeqServer/MeqPython.h>
#include <MeqServer/AID-MeqServer.h>
#include <MeqServer/TID-MeqServer.h>
#include <OCTOPython/OctoPython.h>

#pragma types #Meq::PyNode
#pragma aid Class Module Name

// handy macro to fail on a condition, checking for a python error,
// printing & clearing it if necessary, and raising an exception
#define PyFailWhen(condition,message) \
  if( condition ) \
  { \
    if( PyErr_Occurred() )\
    { \
      LOFAR::Exception exc = getPyException(); \
      ThrowMore(exc,message); \
    } \
    else \
      Throw(message); \
  }

// if the Python error indicator is raised, prints & clears it,
// and throws an exception
#define PyCheckError(message)  \
  if( PyErr_Occurred() ) \
  { \
    LOFAR::Exception exc = getPyException(); \
    ThrowMore(exc,message); \
  }


// surround your Python section with these two calls as follows:
// PyThreadBeginTry
//   some python-calling code, possibly throwing exceptions
// PyThreadEndCatch
//   no more python calls
#define PyThreadBeginTry PyThreadBegin; try {
#define PyThreadEndCatch } catch(...) { PyThreadEnd; throw; } PyThreadEnd;

namespace Meq {

LOFAR::Exception getPyException ();

class PyNodeImpl 
{
  public:

  // NB: how do we access a node from MeqPython, and still allow multiple classes?
      
    PyNodeImpl (Node *node);
      
    //##ModelId=3F9FF6AA0300
    int getResult (Result::Ref &resref, 
                   const std::vector<Result::Ref> &childres,
                   const Request &req,bool newreq);
    
    int discoverSpids (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &req);

    int processCommand (Result::Ref &resref,
                        const HIID &command,
                        DMI::Record::Ref &args,
                        const RequestId &rqid = RequestId(),
                        int verbosity=0);
                        
    const Request & modifyChildRequest (Request::Ref &newreq,const Request &req);
      
    //##ModelId=3F9FF6AA03D2
    void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    //##ModelId=3F9FF6AA016C
    LocalDebugContext;
    
    string sdebug(int detail = 0, const string &prefix = "", const char *name = 0) const;

    OctoPython::PyObjectRef pynode_obj_;
    OctoPython::PyObjectRef pynode_setstate_;
    OctoPython::PyObjectRef pynode_getresult_;
    OctoPython::PyObjectRef pynode_discoverspids_;
    OctoPython::PyObjectRef pynode_processcommand_;
    OctoPython::PyObjectRef pynode_modifychildreq_;
    
    
  protected:
    // converts request to python (with caching), returns 
    // NEW REFERENCE
    PyObject * convertRequest (const Request &req);
      
    // cached request object
    OctoPython::PyObjectRef py_prev_request_;
    Request::Ref prev_request_;
    
    Node *pnode_;
};


class PyNode : public Node
{
  public:
    PyNode ();
  
    virtual ~PyNode ();
    
    virtual TypeId objectType() const
    { return TpMeqPyNode; }
    
    ImportDebugContext(PyNodeImpl);

  protected:
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
    virtual int discoverSpids (Result::Ref &resref, 
                               const std::vector<Result::Ref> &childres,
                               const Request &req);
    
    virtual int processCommand (Result::Ref &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid = RequestId(),
                                int verbosity=0);
    
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    virtual int pollChildren (Result::Ref &resref,
                              std::vector<Result::Ref> &childres,
                              const Request &req);
    
    PyNodeImpl impl_;
};

}

#endif
