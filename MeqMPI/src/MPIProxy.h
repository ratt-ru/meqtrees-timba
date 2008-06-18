
#ifndef MEQMPI_MPIPROXY_H
#define MEQMPI_MPIPROXY_H

#include <MEQ/Node.h>
#include <MeqMPI/TID-MeqMPI.h>

#pragma aidgroup MeqMPI
#pragma types #Meq::MPIProxy
#pragma aids Command Args Request Id Verbose

namespace Meq
{

class MPIProxy : public Node
{
  public:
    virtual ~MPIProxy()
    {}
  
    virtual void init (NodeFace *parent,bool stepparent,int init_index=0);
    
    virtual void setState (DMI::Record::Ref &rec);
    
    // getSyncState() is same as getState(), since we pull it from the
    // remote machine anyway
    virtual void getState (DMI::Record::Ref &ref) const
    { const_cast<MPIProxy*>(this)->getSyncState(ref); }

    virtual void getSyncState (DMI::Record::Ref &ref);
    
    virtual int execute (CountedRef<Result> &resref, const Request &req) throw();
    
    virtual int processCommand (CountedRef<Result> &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid = RequestId(),
                                int verbosity=0);
    
    virtual void clearCache (bool recursive=false) throw();
    
    virtual void holdCache (bool hold) throw();
    
    virtual void propagateStateDependency ();
    
    virtual void publishParentalStatus ();
    
    virtual void setBreakpoint (int bpmask,bool single_shot=false);
    virtual void clearBreakpoint (int bpmask,bool single_shot=false);
    
    virtual void setPublishingLevel (int level=1);
    
    virtual TypeId objectType() const
    { return TpMeqMPIProxy; }

    //## Standard debug info method. Returns string describing the node object
    //## at the specified level of details. If a multi-line string is returned,
    //## appends prefix.
    virtual std::string sdebug(int detail = 0, const std::string &prefix = "", const char *objname = 0) const
    { return "mpiproxy "+name(); }
    
  private:
  
    int remote_proc_;
};



}; // namespace Meq

#endif
