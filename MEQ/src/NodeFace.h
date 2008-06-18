//#  NodeFace.h: abstract class defining a Node's external interface
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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

#ifndef MEQ_NODEFACE_H_HEADER_INCLUDED_E5514413
#define MEQ_NODEFACE_H_HEADER_INCLUDED_E5514413

#include <DMI/Record.h>
#include <MEQ/RequestId.h>

#pragma aidgroup Meq
#pragma types #Meq::NodeFace

namespace Meq 
{ 
using namespace DMI;

class Result;
class Request;

//## NodeFace
//## This is an abstract class describing a Node's external interface.
//## 

class NodeFace : public DMI::BObj
{
  public:
    //## this decribes the interface exposed to the rest of the system
      
    //## CountedRef to a node
    typedef CountedRef<NodeFace> Ref;
  
    //##ModelId=3F698825005B
    //##Documentation
    //## These are flags returned by execute() indicating result properties.
    //## The lower RQIDM_NBITS (currently 16) bits are reserved for request 
    //## dependency masks; see RequestId.h for details.
    //## Note that the meaning of the bits is chosen so that the flags of
    //## of a node's result will generally be a bitwise OR of the child
    //## flags, plus any flags added by the node itself.
    typedef enum 
    {
      //## Result has been updated (as opposed to pulled from the node's cache)
      RES_UPDATED      = 0x01<<RQIDM_NBITS,  
      RES_OK           = RES_UPDATED,  // alias for UPDATED
      //## Normally, results have an implicit dependency on the request type (rqid bit 0).
      //## Return this code to disable this dependency.
      RES_IGNORE_TYPE  = 0x02<<RQIDM_NBITS,  
      //## Result is "missing data". A properly-structured "missing data" result 
      //## must contain a single empty VellSet. Note that an empty Result 
      //## is not considered missing data (since it is a normal return value
      //## for cell-less requests).
      RES_MISSING      = 0x04<<RQIDM_NBITS,    
      //## Result not yet available, must wait. This flag may be combined
      //## with other flags (except FAIL) to indicate dependencies.
      RES_WAIT         = 0x20<<RQIDM_NBITS,    
      //## Execution was aborted via forest's abortFlag()
      RES_ABORT        = 0x40<<RQIDM_NBITS,
      //## Result is a complete fail (i.e. not a mix of failed and OK VellSets,
      //## just a complete fail)
      RES_FAIL         = 0x80<<RQIDM_NBITS
    } ResultAttributes;
    
    NodeFace ()
    : nodeindex_(-1) 
    {}
  
  
    //## Returns name
    const std::string & name () const
    { return name_; }
    
    virtual string className() const
    { return objectType().toString(); }

    //## Returns nodeindex
    int nodeIndex () const 
    { return nodeindex_; }
    
    //## sets name and nodeindex. Can only be called once
    virtual void setNameAndIndex (std::string &name,int ni)
    {
      FailWhen(nodeindex_!=-1,"name and nodeindex can only be set once"); 
      name_ = name; 
      nodeindex_ = ni; 
    }
    
    //## Recursively initializes node and all its children.
    //## Resolves links to children, processes init record, etc.
    //## Called after a forest has been constructed, and before any execute().
    //## Parent is set to the parent node, and stepparent is true
    //## if we are a stepchild of that parent. Node is expected to recursively
    //## call init() on its children. Node is allowed (and even expected) to 
    //## ignore subsequent init() calls with the same init_index.
    //## Root nodes are called with a parent of 0.
    //## Errors should be indicated by throwing an exception.
    virtual void init (NodeFace *parent,bool stepparent,int init_index=0) =0;
    
    //## Reinitializes node after loading from a record (e.g. when restoring
    //## from binary file). Unlike init(), this is non-recusrive, since
    //## at this point everything about parents and children is known.
    virtual void reinit () =0;
    
    
    //## Changes the state of a node. Rec is a partial state record (i.e. it is 
    //## _merged_ into the node state). Node is allowed to transfer the ref.
    //## Errors should be indicated by throwing an exception.
    virtual void setState  (DMI::Record::Ref &rec) = 0;
    

    //## Returns the state of a node by attaching the state record
    //## to the passed ref. 
    virtual void getState (DMI::Record::Ref &ref) const = 0;
    
    //## Similar to state(), but returns a "syncronized" record.
    //## If node keeps some "fast transient" state in data members for 
    //## efficiency, these are not necessarily in sync with the current state 
    //## record. syncState() returns a synced record (and thus is non-const).
    //## Default version uses normal state.
    virtual void getSyncState (DMI::Record::Ref &ref)
    { getState(ref); }
    
    //## Executes a request on the node, returns a Result object (via ref)
    //## and a bitmask describing the properties of the result.
    //## The lower part of the bitmask is generally a dependency mask.
    //## The following high bits indicate various degenerate conditions:
    //## * RES_FAIL: Result is a fail (i.e. a Result object containing nothing
    //##             but fails).
    //## * RES_WAIT: no result available, must wait (currently not implemented anywhere)
    //## * RES_ABORT: no result, execution aborted.
    //## A valid Result object must always be attached to resref on exit, unless
    //## the RES_ABORT or RES_WAIT code is returned.
    //## NO EXCEPTIONS MAY BE THROWN. All errors must be indicated via a RES_FAIL
    //## code and a description of the fail inside the Result.
    virtual int execute   (CountedRef<Result> &resref, const Request &req) throw() =0;
    
    //## Generic command interface. Processes the given command. 
    //## Each subclass may implement its own set of commands.
    //## command: command name
    //## args: a DMI::Record of input arguments.
    //##    Note that args are passed in as a non-const ref that may be taken
    //##    over, its up to the caller to save a copy if needed.
    //##    By convention, an invalid args ref may be interpreted as a 
    //##    boolean "false" or "None" if appropriate.
    //## rqid: if command comes from a request rider, this is the request ID.
    //##    If command comes from another source, this is empty.
    //## Verbosity level: if >0, node may issue events/messages describing
    //##    the operation. 
    //## resref (output): a Result record may be returned by attaching it here.
    //## Return code:
    //##    Should have the RES_OK bit set if a valid command was found and
    //##    processed, or unset if the command is not recognized. It may also
    //##    contain a dependency mask.
    //## Errors (except unknown command) should be indicated by throwing an 
    //## exception.
    virtual int processCommand (CountedRef<Result> &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid = RequestId(),
                                int verbosity=0) =0;
    
    
    //## Clears the node's result cache, optionally recursively.
    //## No exceptions may be thrown.
    virtual void clearCache (bool recursive=false) throw() =0;

    
    //## This is used in the cache resolution mechanism. Called by parent 
    //## node to hint to a child whether it needs to hold its cache until
    //## the next request, or not.
    //## No exceptions may be thrown.
    virtual void holdCache (bool hold) throw() =0;
      
    
    //## This is called from child to parent, to indicate that a child's state
    //## has changed. The information is expected to propagate upstream to
    //## all parents
    //## No exceptions may be thrown.
    virtual void propagateStateDependency () =0;

    
    //## This is called from child to parent, to ask parents to publish
    //## their status information. All upstream parents are expected to
    //## publish their status.
    //## No exceptions may be thrown.
    virtual void publishParentalStatus () =0;
    
    //## sets breakpoint(s)
    virtual void setBreakpoint (int bpmask,bool single_shot=false) =0;
    //## clears breakpoint(s)
    virtual void clearBreakpoint (int bpmask,bool single_shot=false) =0;
    // changes the publishing level
    virtual void setPublishingLevel (int level=1) =0;

    
    //## Standard debug info method. Returns string describing the node object
    //## at the specified level of details. If a multi-line string is returned,
    //## appends prefix.
    virtual std::string sdebug(int detail = 0, const std::string &prefix = "", const char *objname = 0) const
    { return "node "+name(); }

    
    //## SOME UTILITY SHORTCUTS
    //## this defines shortcuts to return a ref to state directly
    DMI::Record::Ref state () const
    { DMI::Record::Ref ref; getState(ref); return ref; }
    
    DMI::Record::Ref syncState ()
    { DMI::Record::Ref ref; getSyncState(ref); return ref; }
    
    
    
  private:
    //## we do have some private data: name and nodeindex    
    std::string name_;
    int         nodeindex_;
    
};

  
};

#endif
