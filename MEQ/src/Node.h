//#  Node.h: base MeqNode class
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$
#ifndef MeqSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413
#define MeqSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413
    
#include <DMI/DataRecord.h>
#include <DMI/Events.h>
#include <MEQ/Result.h>
#include <MEQ/RequestId.h>
#include <MEQ/Request.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/TID-Meq.h>
#include <map>
#include <vector>
    
#pragma aidgroup Meq
#pragma types #Meq::Node
#pragma aid Add Clear Known Active Gen Dep Deps Symdep Symdeps Mask Masks
#pragma aid Parm Value Resolution Domain Dataset Resolve Init
#pragma aid Link Or Create
    

namespace Meq {

class Forest;
class Request;

// flag for child init-records, specifying that child node may be directly
// libnked to if it already exists
const HIID FLinkOrCreate = AidLink|AidOr|AidCreate;

const HIID FDependMask = AidDep|AidMask;
const HIID FKnownSymDeps = AidKnown|AidSymdeps;
const HIID FActiveSymDeps = AidActive|AidSymdeps;
const HIID FSymDepMasks = AidSymdep|AidMasks;

const HIID FGenSymDep       = AidGen|AidSymdep;
const HIID FGenSymDepGroup  = AidGen|AidSymdep|AidGroup;

// Node commands
const HIID FResolveChildren = AidResolve|AidChildren;
const HIID FInitDepMask = AidInit|AidDep|AidMask;
const HIID FClearDepMask = AidClear|AidDep|AidMask;
const HIID FAddDepMask = AidAdd|AidDep|AidMask;

// some standard symbolic deps
const HIID FParmValue  = AidParm|AidValue;
const HIID FResolution = AidResolution;
// const HIID FDomain     = AidDomain;
const HIID FDataset    = AidDataset;

// the All group
const HIID FAll = AidAll;

//##ModelId=3F5F436202FE
class Node : public BlockableObject
{
  public:
    //##ModelId=3F5F43620304
    typedef CountedRef<Node> Ref;
  
    //##ModelId=3F698825005B
    //##Documentation
    //## These are flags returned by execute(), indicating result properties
    //## The lower RQIDM_NBITS (currently 16) bits are reserved for request 
    //## dependency masks; see RequestId.h for details.
    //## Note that the meaning of the bits is chosen so that the flags of
    //## of a node's result will generally be a bitwise OR of the child
    //## flags, plus any flags added by the node itself.
    typedef enum 
    {
      // Result is volatile (i.e. may change even if the request doesn't) and
      // thus should never be taken from cache
      RES_VOLATILE     = 0x01<<RQIDM_NBITS,  
      // Result has been updated (as opposed to pulled from the node's cache)
      RES_UPDATED      = 0x02<<RQIDM_NBITS,  
      // Result not yet available, must wait. This flag may be combined
      // with other flags (except FAIL) to indicate dependencies.
      RES_WAIT         = 0x10<<RQIDM_NBITS,    
      // Result is a complete fail (i.e. not a mix of failed and OK VellSets,
      // just a complete fail)
      RES_FAIL         = 0x80<<RQIDM_NBITS    
    } ResultAttributes;
    
    //##Documentation
    //## Auto-resample modes. Nodes may enable automatic resampling of child
    //## results, for cases where children return results at different 
    //## resolutions
    typedef enum 
    { 
      // fail if child resolutions differ (default for e.g. Function nodes)
      RESAMPLE_FAIL      = -2,
      // do not do any resampling
      RESAMPLE_NONE      =  0,
      // integrate all child results to lowest resolution
      RESAMPLE_INTEGRATE = -1,
      // upsample all child results to highest resolution
      RESAMPLE_UPSAMPLE  =  1,
    } AutoResampleModes; 

    //##ModelId=3F5F43E000A0
    //##Documentation
    //## Child labels may be specified in constructror as a C array of HIIDs.
    //## If labels==0, no labels are defined.
    //## If nchildren>=0, specifies that an exact number of children is expected.
    //## If nmandatory>0, spefifies that at least nmandatory children are 
    //##    expected; note that if labels are supplied, then the first 
    //##    nmand labels are considered the mandatory ones, and the rest are
    //##    optional
    Node (int nchildren=-1,const HIID *labels = 0,int nmandatory=0);
        
    //##ModelId=3F5F44A401BC
    virtual ~Node();

    //##ModelId=3F5F45D202D5
    virtual void init (DataRecord::Ref::Xfer &initrec, Forest* frst);
    
    //##ModelId=400E530F0090
    virtual void reinit (DataRecord::Ref::Xfer &initrec, Forest* frst);
    
    //##ModelId=3F83FAC80375
    void resolveChildren (bool recursive=true);
    
    //##ModelId=400E531101C8
    void relinkChildren ();
        
    //##ModelId=3F5F44820166
    const string & name() const
    { return myname_; }
    
    //##ModelId=400E5311029C
    int nodeIndex() const 
    { return node_index_; }
    
    //##ModelId=400E53110383
    string className() const
    { return objectType().toString(); }
    
    //##ModelId=3F5F441602D2
    const DataRecord & state() const
    { return *staterec_; }
    
    bool hasState () const
    { return staterec_.valid(); }
    
    //##ModelId=400E53120082
    void setNodeIndex (int nodeindex);
    
    //##ModelId=3F5F445A00AC
    void setState (DataRecord &rec);
    
    //##ModelId=3F6726C4039D
    int execute (Result::Ref &resref, const Request &);
    
    //##ModelId=3F9919B00313
    const HIID & currentRequestId () const
    { return current_reqid_; }
    
    int autoResample () const
    { return auto_resample_; }
    
    void setAutoResample (int mode)
    { auto_resample_ = mode; }
    
    //##ModelId=400E531300C8
    //##Documentation
    //## Clears cache (optionally recursively)
    void clearCache (bool recursive=false);
    
    //##Documentation
    //## adds an event slot to which generated results will be published
    void addResultSubscriber    (const EventSlot &slot);
    //##Documentation
    //## removes subscription for specified event slot
    void removeResultSubscriber (const EventSlot &slot);
    //##Documentation
    //## removes all subscriptions for specified recepient
    void removeResultSubscriber (const EventRecepient *recepient);
    
    //##ModelId=3F98D9D20372
    Forest & forest ()
    { return *forest_; }

    //##ModelId=3F85710E002E
    int numChildren () const
    { return children_.size(); }
    
    //##ModelId=3F85710E011F
    Node & getChild (int i);
    
    //##ModelId=3F85710E028E
    Node & getChild (const HIID &id);
    
    //##ModelId=3F98D9D20201
    int getChildNumber (const HIID &id);
    
    
    const std::vector<HIID> & getNodeGroups () const
    { return node_groups_; }
    
    int getDependMask () const
    { return depend_mask_; }
    
    const std::vector<HIID> & getKnownSymDeps () const
    { return known_symdeps_; }
    
    const std::vector<HIID> & getActiveSymDeps () const
    { return active_symdeps_; }
    
    //##Documentation
    //## sets the node's dependency mask
    void setDependMask (int mask);
    
    //##Documentation
    //## sets the node's set of known symbolic dependencies. Should normally 
    //## be done once at init time. Note that it also possible to only call 
    //## setActiveSymDeps() directly from the constructor, if the known and
    //## active set is the same to begin with.
    //## Known symdeps will have their dependency masks tracked
    //## by processCommand(). 
    void setKnownSymDeps (const HIID deps[],int ndeps);
    
    void setKnownSymDeps (const std::vector<HIID> &deps)
    { setKnownSymDeps(&deps.front(),deps.size()); }
    
    void setKnownSymDeps (const HIID &dep)
    { setKnownSymDeps(&dep,1); }
    
    void setKnownSymDeps ()
    { static HIID dum; setKnownSymDeps(&dum,0); }
    
    //##Documentation
    //## Sets the node's set of active symbolic dependencies. Must be a subset
    //## of the known symdeps. This will call recomputeDependMask().
    void setActiveSymDeps (const HIID deps[],int ndeps);
    
    void setActiveSymDeps (const HIID &dep)
    { setActiveSymDeps(&dep,1); }
    
    void setActiveSymDeps (const std::vector<HIID> &deps)
    { setActiveSymDeps(&deps.front(),deps.size()); }
    
    void setActiveSymDeps ()
    { static HIID dum; setActiveSymDeps(&dum,0); }
    
    //##Documentation
    //## computes a dependency mask, by bitwise-ORing tracked symdep masks 
    //## corresponding to currently active symdeps.
    int computeDependMask (const std::vector<HIID> &symdeps);
    
    //##Documentation
    //## Nodes that generate their own requests (e.g. Sink, Solver, ModRes)
    //## have to define a mapping between named symdeps and masks (which are used
    //## to generate new request IDs). These mappings will be sent up the tree
    //## so that other nodes may collect the depmasks corresponding to their set
    //## of known dependencies. This sets the node's generated symdeps.
    //## An optional group argument restricts the symdeps to a specific node
    //## group.
    void setGenSymDeps (const HIID symdeps[],const int depmasks[],int ndeps,const HIID &group = HIID());
    
    void setGenSymDeps (const std::vector<HIID> &symdeps,
                       const std::vector<int>  &depmasks,
                       const HIID &group = HIID())
    { DbgAssert(symdeps.size()==depmasks.size()); 
      setGenSymDeps(&symdeps.front(),&depmasks.front(),symdeps.size(),group); }
                       
    void setGenSymDeps (const HIID &symdep,int depmask,const HIID &group = HIID())
    { setGenSymDeps(&symdep,&depmask,1,group); }
    
    //##Documentation
    //## Gets the full generated symdep mask (bitwise OR of all generated
    //## symdeps)
    int getGenSymDepMask () const
    { return gen_symdep_fullmask_; }
    
    //##Documentation
    //## Gets the generated symdep mask for a specific symdep (0 if not found)
    int getGenSymDepMask (const HIID &symdep) const;
            
    //##Documentation
    //## checking level used for extra sanity checks (presumably expensive), 
    //## set to non-0 for debugging
    static int checkingLevel ()
    { return checking_level_; }
    
    static void setCheckingLevel (int level)
    { checking_level_ = level; }
    
    //##ModelId=3F5F4363030F
    //##Documentation
    //## Clones a node. 
    //## Currently not implemented (throws exception)
    virtual CountedRefTarget* clone(int flags = 0, int depth = 0) const;
    //##ModelId=3F5F43630313
    //##Documentation
    //## Returns the class TypeId
    virtual TypeId objectType() const
    { return TpMeqNode; }
    //##ModelId=3F5F43630315
    //##Documentation
    //## Un-serialize.
    //## Currently not implemented (throws exception)
    virtual int fromBlock(BlockSet& set);
    //##ModelId=3F5F43630318
    //##Documentation
    //## Serialize.
    //## Currently not implemented (throws exception)
    virtual int toBlock(BlockSet &set) const;
    
    //##ModelId=3F5F48180303
    //##Documentation
    //## Standard debug info method
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F8433C1039E
    LocalDebugContext;


    //##Documentation
    //## Rider is a utility class providing functions for manipulating
    //## the request rider.
    class Rider
    {   
      public:
      //##Documentation
      //## bitwise flags for methods below. Note that they are cumulative
      typedef enum {
        NEW_RIDER     = 0x01,
        NEW_GROUPREC  = 0x02,
        NEW_CMDREC    = 0x04,
        NEW_ALL       = 0x07
      } RiderFlags;
        
      //##Documentation
      //## Clears the rider from the request, if any.
      //## Reqref will be privatized for writing if needed.
      static void clear (Request::Ref &reqref);

      //##Documentation
      //## Inits (if necessary) and returns the rider.
      //## Reqref will be privatized for writing if needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      static DataRecord & getRider (Request::Ref &reqref,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the group command record for 'group'.
      //## Reqref will be privatized for writing if needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      static DataRecord & getGroupRec (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_all subrecord for the given group.
      //## Reqref will be privatized for writing if needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DataRecord & getCmdRec_All (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_by_nodeindex subrecord for 
      //## the given group. Reqref will be privatized for writing if needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DataRecord & getCmdRec_ByNodeIndex (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_by_list subrecord (field) for 
      //## the given group. Reqref will be privatized for writing if needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DataField & getCmdRec_ByList (Request::Ref &reqref,const HIID &group,int flags=0);
      
      //## Adds a symdep mask for the given group (FAll by default). Inits
      //## riders and subrecords as necessary.
      static void addSymDepMask (Request::Ref &reqref,const HIID &symdep,
                                 int mask,const HIID &group = AidAll );
      
      //##Documentation
      //## Inits (if necessary) and returns a subrecord for rec[field]
      static DataRecord & getOrInit (DataRecord &rec,const HIID &field);
    };

  protected:
    // ----------------- virtual methods defining node behaviour --------------
      
    //##ModelId=3F83FADF011D
    //##Documentation
    //## called from resolveChildren(), meant to check children types if the node
    //## requires specific children. Throw exception on failure. 
    virtual void checkChildren()
    {} // base version does no checking
    
    //##ModelId=3F98D9D2006B
    //##Documentation
    //## called from init(), meant to check the initrec for required fields,
    //## and to fill in any missing defaults. Throws exception on failure 
    //## (i.e. if a required field is missing)
    virtual void checkInitState (DataRecord &rec)
    {}
    
    //##ModelId=400E531402D1
    //##Documentation
    //## called from init() and setState(), meant to update internal state
    //## in accordance to rec. If initializing==true (i.e. when called from 
    //## init()), rec is a complete state record.
    virtual void setStateImpl (DataRecord &rec,bool initializing);
    
    //##Documentation
    //## virtual method called whenever any symdeps or symdep masks change.
    //## Default version computes & sets the default depend_mask by using the 
    //## currently active symdeps
    virtual void resetDependMasks ();
    
    //##ModelId=400E531600B8
    //##Documentation
    //## called from execute() when a new request is received. Should return
    //## true if it is OK to proceed, false otherwise (RES_WAIT will be returned
    //## by execute() on a false). Nodes tied to external data sources may need 
    //## to override this.
    virtual bool readyForRequest (const Request &)
    { return true; } // base version always ready
    
    //##ModelId=400E531603C7
    //##Documentation
    //## called to process request rider commands, if any. This is allowed
    //## to modify the request object, a ref is passed in to facilitate COW
    //## (since the request is normally received as read-only)
    virtual void processCommands (const DataRecord &rec,Request::Ref &reqref);

    //##ModelId=400E531702FD
    //##Documentation
    //## Called from execute() to collect the child results for a given request.
    //## Child_results vector is pre-sized to the number of children.
    //## The method is expected to pass the request on to the children,  
    //## collect their results in the vector, and return the accumulated
    //## result code. If RES_FAIL is returned, then resref should point
    //## to a Result with the fails in it; this result will be returned by
    //## execute() immediately with the RES_FAIl code.
    //## Default version does just that. If any child returns RES_FAIL,
    //## collects all fails into resref and returns RES_FAIL. If no children
    //## fail, resref is left untouched.
    //## Nodes should only reimplement this if they prefer to poll children 
    //## themselves (i.e. the Solver). 
    virtual int pollChildren (std::vector<Result::Ref> &child_results,
                              Result::Ref &resref,
                              const Request &req);

    //##ModelId=3F98D9D100B9
    //##Documentation
    //## Called from execute() to compute the result of a request.
    //##  childres is a vector of child results (empty if no children);
    //##  req is request; newreq is true if the request is new.
    //## Result should be created and attached to resref. Return code indicates
    //## result properties. If the RES_WAIT flag is returned, then no result is 
    //## expected; otherwise a Result must be attached to the ref.
    //## RES_FAIL may be returned to indicate complete failure.
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);

    // ----------------- misc helper methods ----------------------------------
    
    //##Documentation
    //## resamples children to common resolution according to auto_resample_
    //## setting. Returns output resolution in rescells.
    //## If auto-resampling is disabled, does nothing.    
    void resampleChildren (Cells::Ref rescells,std::vector<Result::Ref> &childres);
    
    //##ModelId=3F83F9A5022C
    //##Documentation
    //## write-access to the state record
    DataRecord & wstate()
    { return staterec_(); }
    
    //##ModelId=3F9919B10014
    //##Documentation
    //## sets the current request
    void setCurrentRequest (const Request &req);

    //##ModelId=400E531A021A
    //##Documentation
    //## Checks for cached result; if hit, attaches it to ref and returns true.
    //## On a miss, clears the cache (NB: for now!)
    bool getCachedResult (int &retcode,Result::Ref &ref,const Request &req);
    
    //##ModelId=400E531C0200
    //##Documentation
    //## Conditionally stores result in cache according to current policy.
    //## Returns the retcode.
    int  cacheResult   (const Result::Ref &ref,int retcode);
    
    //##Documentation
    //## checks the Resampled Child Result (RCR) cache for a cached result 
    //## matching the given resolution.
    //## On a match, attaches the result to ref and returns true.
    //## On a mismatch, clears the cache and returns false. 
    bool checkRCRCache (Result::Ref &ref,int ich,const Cells &cells);

    //##Documentation
    //## clears the RCR cache for child ich. If ich<0, then clears all 
    void clearRCRCache (int ich=-1);
    
    //##Documentation
    //## caches a resampled result for child ich
    void cacheRCR      (int ich,const Result::Ref::Copy &res);
    
    //##ModelId=400E531E008F
    //##Documentation
    //## creates a message of the form "Node CLASS ('NAME'): MESSAGE"
    string makeMessage (const string &msg) const
      { return  "Node " + className() + "('" + name() + "'): " + msg; }
    
    //##Documentation
    //## These exception are meant to be thrown from methods like init(),
    //## getResult(), processCommands() and setStateImpl() when something goes 
    //## wrong. The type of the exception indicates whether any cleanup is 
    //## required.
    EXCEPTION_CLASS(FailWithCleanup,LOFAR::Exception)
    EXCEPTION_CLASS(FailWithoutCleanup,LOFAR::Exception)
  
    //##Documentation
    //## NodeThrow can be used to throw an exception, with the message
    //## passed through makeMessage()
    #define NodeThrow(exc,msg) \
      { THROW(exc,makeMessage(msg)); }
    //##Documentation
    //## NodeThrow1 thows a FailWithoutCleanup exception, with the message
    //## passed through makeMessage()
    #define NodeThrow1(msg) \
      { THROW(FailWithoutCleanup,makeMessage(msg)); }

    //##Documentation
    //## Helper method for init(). Checks that initrec field exists, throws a
    //## FailWithoutCleanup with the appropriate message if it doesn't.
    //## Defined as macro so that exception gets proper file/line info
    #define requiresInitField(rec,field) \
      { if( !(rec)[field].exists() ) \
         NodeThrow(FailWithoutCleanup,"missing initrec."+(field).toString()); } \
    //##Documentation
    //## Helper method for init(). Checks that initrec field exists and inserts
    //## a default value if it doesn't.
    #define defaultInitField(rec,field,deflt) \
      { DataRecord::Hook hook(rec,field); \
        if( !hook.exists() ) hook = (deflt); }
        
    //##Documentation
    //## Helper method for setStateImpl(). Meant to check for immutable state 
    //## fields. Checks if record rec contains the given field, throws a 
    //## FailWithoutCleanup with the appropriate message if it does.
    //## Defined as macro so that exception gets proper file/line info
    #define protectStateField(rec,field) \
      { if( (rec)[field].exists() ) \
          NodeThrow(FailWithoutCleanup,"state."+(field).toString()+" not reconfigurable"); }

// 31/03/04: phased out, since rec[Field].get(variable) does the same thing
//     // Helper method for setStateImpl(). Checks if rec[field] exists, if yes,
//     // assigns it to 'out', returns true. Otherwise returns false.
//     template<class T>
//     bool getStateField (T &out,const DataRecord &rec,const HIID &field)

        
  private:
    //##ModelId=400E531F0085
    void initChildren (int nch);
    //##ModelId=3F9505E50010
    // processes a child specification. 'child' specifies the child 
    // (this can be a true HIID only if child_labels_ are specified;
    // otherwise it's an single-element index) . 'id' is the actual field
    // in 'children' that contains the child specification.
    void processChildSpec (NestableContainer &children,const HIID &chid,const HIID &id);
    
    //##ModelId=3F8433C20193
    void addChild (const HIID &id,Node *childnode);
    
    //##Documentation
    //## processes the request rider, and calls processCommand() as appropriate.
    //## The request object may be modified; a ref is passed in to facilitate
    //## copy-on-write
    void processRequestRider (Request::Ref &reqref);
    
    //##ModelId=400E530A0143
    //##Documentation
    //## child labels specified in constructor, if any. Labelled children may
    //## be assigned via the record [label=child] form in init(). 
    const HIID * child_labels_;      
    //##ModelId=400E530A016A
    //##Documentation
    //## specified in constructor. If non-0, node must have that fixed number
    //## of children
    int check_nchildren_;
    //##Documentation
    //## specified in constructor. If non-0, node must have no less than 
    //## that number of children
    int check_nmandatory_;
    
    //##ModelId=3F5F4363030D
    DataRecord::Ref staterec_;
    
    //##ModelId=3F5F48040177
    string myname_;
    //##ModelId=400E530A0368
    int node_index_;
    //##ModelId=3F5F43930004
    Forest *forest_;
    
    //##ModelId=400E530B018B
    //##Documentation
    //## current (or last executed) request, set in execute()
    HIID current_reqid_;
    //##ModelId=400E530B01AF
    //##Documentation
    //## cached result of current request
    Result::Ref cache_result_;
    //##ModelId=400E530B01D2
    //##Documentation
    //## cached return code of current request
    int cache_retcode_;
    
    //##Documentation
    //## Dependency mask indicating which parts of a RequestId the node's own
    //## value depends on (this is in addition to any child dependencies).
    //## This is (re)generated automatically whenever a Set.Depend.Mask command
    //## is received, based on a node's symbolic dependencies.
    int depend_mask_;
    
    //##Documentation
    //## The set of a node's symbolic dependencies. This can be set by calling
    //## setSymbolicDependencies(), or via the Symbolic.Depend field of the
    //## state record. Note that setting the dependencies always clears 
    //## depend_mask_, so a subsequent Set.Depend.Mask command should be 
    //## issued.
    std::vector<HIID> known_symdeps_;
    std::vector<HIID> active_symdeps_;
    std::map<HIID,int> symdep_masks_;
    
    //##Documentation
    //## The set of symdeps generated by this node (for nodes that generate
    //## requests). This is a mapping between symdeps and thweir masks.
    std::map<HIID,int> gen_symdep_masks_;
    //##Documentation
    //## The full symdep mask: a bitwise-OR of all gen_symdep_masks_
    int gen_symdep_fullmask_;
    //##Documentation
    //## symdeps may apply to a specific node group only. If empty, the All
    //## group will be used    
    HIID gen_symdep_group_;
    
    
    //##ModelId=400E55D00080
    //##Documentation
    //## Group(s) that a node belongs to. Node groups determine 
    std::vector<HIID> node_groups_;
    
    //##ModelId=3F8433ED0337
    //##Documentation
    //## vector of refs to children
    std::vector<Node::Ref> children_;
    
    //##ModelId=3F8433C10295
    typedef std::map<HIID,int> ChildrenMap;

    //##ModelId=400E530B03D6
    //##Documentation
    //## map from child labels to numbers (i.e. indices into the children_ vector)
    //## if child labels are not defined, this a trivial i->i mapping
    ChildrenMap child_map_;
    
    //##ModelId=400E530C0011
    //## container of child names. This is a DataRecord indexed by label 
    //## if the node defines child labels, else a DataField (indexed by
    //## child number) otherwise
    NestableContainer::Ref child_names_;
    
    //##ModelId=400E530C0216
    //##Documentation
    //## container of child node indices
    NestableContainer::Ref child_indices_;
    
    //##Documentation
    //## auto-resample mode for child results
    int auto_resample_;
    
    //##Documentation
    //## cache of resampled child results
    std::vector<Result::Ref> rcr_cache_;
    
    //##Documentation
    //## list of event recepients for when result is available
    typedef std::list<EventSlot> ResultSubscribers;
    ResultSubscribers result_subscribers_;
    
    static int checking_level_;
};

} // namespace Meq

#endif /* MeqSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413 */
