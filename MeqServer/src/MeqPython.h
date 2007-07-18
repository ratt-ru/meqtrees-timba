#ifndef MEQSERVER_MEQPYTHON_H
#define MEQSERVER_MEQPYTHON_H 1

#include <OCTOPython/OctoPython.h>
#include <TimBase/Thread/Mutex.h>
#include <exception>

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
