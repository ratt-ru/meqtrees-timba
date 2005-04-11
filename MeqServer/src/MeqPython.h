#ifndef MEQSERVER_MEQPYTHON_H
#define MEQSERVER_MEQPYTHON_H 1

#include <OCTOPython/OctoPython.h>

#include <exception>

namespace Meq
{
  class MeqServer;
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
  
  // runs a python script from file
  void runFile      (MeqServer *pm,const string &filename);
  
  // imports a python module
  void importModule (MeqServer *pm,const string &name);
  
  // calls visibility header handlers, if any are set up
  void processVisHeader (MeqServer *pm,const DMI::Record &hdr);
  
  // -----------------------------------------------------------------------
  // Various internal declarations
  // -----------------------------------------------------------------------
  // MeqServer exception 
  extern PyObject *PyExc_MeqServerError;
};

#endif
