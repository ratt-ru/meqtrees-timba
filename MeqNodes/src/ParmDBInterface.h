
#include <MeqNodes/Parm.h>
#include <TimBase/Thread/Mutex.h>

#ifdef HAVE_PARMDB
using  namespace LOFAR::ParmDB;

static Thread::Mutex & parmdbMutex ()
{ return AipsppMutex::aipspp_mutex; }

ParmDomain toParmDomain(const Meq::Domain &domain);

Meq::Domain fromParmDomain(const ParmDomain &domain);

Meq::Funklet::Ref  ParmValue2Funklet(const ParmValue &pv);

ParmValue Funklet2ParmValue(Meq::Funklet::Ref  funklet);
#endif
