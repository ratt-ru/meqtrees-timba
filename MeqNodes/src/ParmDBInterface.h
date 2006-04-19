
#include <MeqNodes/Parm.h>

using  namespace LOFAR::ParmDB;

ParmDomain toParmDomain(const Meq::Domain &domain);

Meq::Domain fromParmDomain(const ParmDomain &domain);

Meq::Funklet::Ref  ParmValue2Funklet(const ParmValue &pv);

ParmValue Funklet2ParmValue(Meq::Funklet::Ref  funklet);
