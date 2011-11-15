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

#ifndef MEQSERVER_MEQPYTHON_H
#define MEQSERVER_MEQPYTHON_H 1

#include <OCTOPython/OctoPython.h>
#include <TimBase/Thread/Mutex.h>
#include <exception>

// this makes the OctoPythion return macros thread-aware
#undef PyThreadBegin
#undef PyThreadEnd
#define PyThreadBegin   PyGILState_STATE gilstate = PyGILState_Ensure();
#define PyThreadEnd     PyGILState_Release(gilstate);


namespace Meq
{
  class MeqServer;
}

namespace VisCube
{
  class VTile;
}

namespace MeqPython
{
  using namespace Meq;
  using namespace OctoPython;
  using std::string;
  LocalDebugContext_ns;

  inline std::string sdebug (int=0) { return "MeqPy"; }

  // mutex acquired before calling any python. This is a bit of a kludge
  // for now, the proper way to do it is with the Global Interpreter Lock
  // and various thread structures, as described in the Python/C API
  // document chapter 8.
  extern "C" Thread::Mutex python_mutex;

  // Inits Python if needed, attaches meqserver module to MeqServer object.
  void initMeqPython (MeqServer *pm);

  // Destroys Python interpreter if it was running
  void destroyMeqPython ();

  // calls init-record handler, if one is set up
  void processInitRecord (const DMI::Record &initrec);

  // calls visibility header handlers, if any are set up
  void processVisHeader (const DMI::Record &hdr);
  void processVisTile   (const VisCube::VTile &tile);
  void processVisFooter (const DMI::Record &hdr);

  // creates a Python-side PyNode object with the given node name and
  // class, and associates it with the given Node object
  PyObjectRef createPyNode (Node &pynode,const string &classname,const string &modulename);

  // marks all modules imported by MeqPython for a reload next time they are
  // imported. SHould be called before defining a new forest.
  void forceModuleReload ();

  // testing function -- converts object to python object, then discards
  void testConversion   (const BObj &obj);

  // these are wrapped in a class because we use it in a friend
  // declaration in MEQ/Node.h
  class PyNodeAccessor
  {
    public:
      static PyObject * set_node_state_field (PyObject *, PyObject *args);
      static PyObject * set_node_active_symdeps (PyObject *, PyObject *args);
  };


  // -----------------------------------------------------------------------
  // Various internal declarations
  // -----------------------------------------------------------------------
  // MeqServer exception
  extern PyObject *PyExc_MeqServerError;
};

#endif
