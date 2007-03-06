#ifndef MEQSERVER_MEQPYTHON_H
#define MEQSERVER_MEQPYTHON_H 1

#include <OCTOPython/OctoPython.h>

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
