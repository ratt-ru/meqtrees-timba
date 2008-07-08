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

#include "Node.h"
#include "MeqVocabulary.h"
#include "Forest.h"
#include "MTPool.h"
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>

namespace Meq {

using Debug::ssprintf;

//##ModelId=400E531101C8
void Node::setupNurseries ()
{
  // basic setup
  children().attachAbortFlag(&(forest().getAbortFlag()));
  stepchildren().attachAbortFlag(&(forest().getAbortFlag()));
  children().setIdleCallbacks(Node_unlockStateMutex,Node_lockStateMutex,this);
  stepchildren().setIdleCallbacks(Node_unlockStateMutex,Node_lockStateMutex,this);

  // sets up nursery objects based on the child_indices_ and stepchild_indices_
  // vectors
  int num_children = child_indices_.size();
  children().init(num_children,name());
  for( int i=0; i<num_children; i++ )
  {
    if( child_indices_[i] >= 0 )
      children().setChild(i,forest().get(child_indices_[i]),getChildLabel(i));
  }
  
  int num_stepchildren = stepchild_indices_.size();
  stepchildren().init(num_stepchildren,name()+"/s");
  for( int i=0; i<num_stepchildren; i++ )
    stepchildren().setChild(i,forest().get(stepchild_indices_[i]));
}

void Node::relinkParents ()
{
  const DMI::Record & strec = *staterec_;
  // recreates the parents_ vector based on fields in the state record
  std::vector<int>  parent_indices = strec[FParentIndices].as_vector<int>();
  std::vector<bool> stepparent = strec[FIsStepParent].as_vector<bool>();
  FailWhen(parent_indices.size()!=stepparent.size(),"corrupt state record -- parents info size mismatch");
  parents_.resize(parent_indices.size());
  for( uint i=0; i<parents_.size(); i++ )
  {
    parents_[i].ref.attach(forest().get(parent_indices[i]),DMI::SHARED);
//    parents_[i].stepparent = stepparent[i];
  }
} 

// #ifndef DISABLE_NODE_MT
// class NodeInitWorkOrder : public MTPool::AbstractWorkOrder
// {
//   public:
//     NodeInitWorkOrder (NodeFace &parent,NodeFace &child,int ichild,bool stepparent,int init_idx)
//     : parentref(parent,DMI::SHARED),
//       noderef(child,DMI::SHARED),
//       ichild(ich),
//       is_stepparent(steppar),
//       init_index(init_idx)
//     {}
//     
//     virtual void execute (Brigade &brig);      // runs the work order
//     {
//       int retcode = -1;
//       NodeFace &node = noderef();
//       NodeFace &parent = parentref();
//       try
//       {
//         cdebug1(1)<<brigade.sdebug(1)+" init on node "+node.name()+"\n";
//         node.init(&parent,is_stepparent,init_index);
//         retcode = 0;
//         cdebug1(1)<<brigade.sdebug(1)+" init on node "+node.name()+"\n";
//       }
//       catch( std::exception &exc )
//       {
//         string str = Debug::ssprintf("caught exception while initializing a node: %s",exc.what());
//         cdebug(0)<<str<<endl;
//         DMI::ExceptionList exclist(exc);
//         exclist.add(LOFAR::Exception(str));
//         node.forest().postError(exclist);
//       }
//       catch(...)
//       {
//         string str = "caught unknown exception while initializing a node";
//         cdebug(0)<<str<<endl;
//         node.forest().postError(str);
//       }
//       // notify parent
//       parent.completeChildInit(ichild,is_stepparent);
//     } 
//     
//     NodeFace::Ref parentref,noderef;  
//     int ichild; 
//     bool stepparent;
//     int init_index; 
// };
// 
// void Node::completeChildInit (int,bool)
// {
//   Thread::Mutex::Lock lock(child_init_cond_);
//   child_init_count_--;
//   if( child_init_count_<=0 )
//     child_init_cond_.signal();
// }
// #endif

void Node::init ()
{
  try
  {
    // set the parents
    int npar = parent_indices_.size();
    parents_.resize(npar);
    pcparents_->npar = npar;
    for( int i=0; i<npar; i++ )
    {
      NodeFace & parent = forest().get(parent_indices_[i]);
      parents_[i].ref.attach(parent,DMI::SHARED);
    }
    // if node already resolved with this resolve parent ID, do nothing
    wstate()[FInternalInitIndex] = internal_init_index_ = 0;
    // init nurseries and resolve children
    setupNurseries();
    // call the state init method
    cdebug(2)<<"initializing node (setStateImpl)"<<endl;
    cdebug(3)<<"initial state is "<<staterec_().sdebug(10,"    ")<<endl;
    setStateImpl(staterec_,true);
  }
  catch( std::exception &exc )
  {
    ThrowMore(exc,"failed to init node '"+name()+"'");
  }
  catch( ... )
  {
    Throw("failed to init node '"+name()+"'");
  }
}


void Node::reinit ()
{ 
  // do nothing if already initialized -- this avoids recursive reinit()
  // of children below
  if( internal_init_index_ >= 0 )
    return; 
  // setup children and parents
  setupNurseries();
  relinkParents();
  // get init index, if any
  internal_init_index_ = (*staterec_)[FInternalInitIndex].as<int>();
  // call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"reinitializing node (setStateImpl)"<<endl;
  cdebug(3)<<"state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_,true);
  // recursively reinit() all children
  for( int i=0; i<children().numChildren(); i++ )
    if( children().isChildValid(i) )
      children().getChild(i).reinit();
  for( int i=0; i<stepchildren().numChildren(); i++ )
    stepchildren().getChild(i).reinit();
  // call checkChildren() since all children are now valid
  checkChildren();
}


void Node::saveState (DMI::Record::Ref &ref)
{
  // updates state so that it is suitable for saving to a file
  std::vector<int>  parent_indices(numParents());
  std::vector<bool> stepparent(numParents());
  for( int i=0; i<numParents(); i++ )
  {
    parent_indices[i] = getParent(i).nodeIndex();
//    stepparent[i] = isStepParent(i);
  }
  Thread::Mutex::Lock lock(stateMutex());
  DMI::Record &strec = wstate();
  strec[FParentIndices].replace() = parent_indices;
  strec[FIsStepParent].replace() = stepparent;
  // sync remaining state
  getSyncState(ref);
}

//##ModelId=3F5F45D202D5
void Node::attachInitRecord (DMI::Record::Ref &initrec, Forest* frst)
{
  cdebug(1)<<"attaching init record"<<endl;
  forest_ = frst;
  // init symdeps and depmask with forest defaults
  depend_mask_ = symdeps().copyMap(forest().symdeps());
  
  // xfer the state record, deref for writing
  DMI::Record &strec = staterec_.xfer(initrec).dewr();

  strec[FInternalInitIndex] = internal_init_index_ = -1;
  
  // Check children specification
  // FChildren: may be a Record of {label=nodeindex} fields, or a vector of indices.
  //    Either way we create a FChildrenIndices entry containg a Vec of indices
  // FStepChildren: may only be a vector of indices.
  // Actual child nodes will be linked later on at resolveLinks() time;
  // in the meantime, we make sure all child-related state is stored in the
  // state record and not in data members, so that we can be reinit()'d from
  // the state record at any time.
  cdebug(2)<<"initializing node children"<<endl;
  DMI::Record::Hook hchildren(strec,FChildren);
  // no children if no field
  if( !hchildren.exists() )
    child_indices_.clear();
  // If children field is a record, convert to children index vector
  else if( hchildren.type() == TpDMIRecord )
  {
    const DMI::Record & childrec = hchildren.as<DMI::Record>();
    child_indices_.resize(childrec.size(),-1);
    // iterate through record and apply child labels. Note that
    // record may be iterated out of order and may contain numeric-only
    // labels
    for( DMI::Record::const_iterator iter = childrec.begin(); iter != childrec.end(); iter++ )
    {
      int chnum = childLabelToNumber(iter.id());
      FailWhen(chnum<0,"illegal child '"+iter.id().toString()+"' specified");
      if( chnum >= int(child_indices_.size()) )
        child_indices_.resize(chnum+1,-1);
      // access field as an integer
      const DMI::Container &cont = iter.ref().as<DMI::Container>();
      int child_index = cont[HIID()].as<int>();
      child_indices_[chnum] = child_index;
    }
  }
  // If array/vector of ints, simply copy to children index vector.
  else if( hchildren.type() == Tpint )
  {
    hchildren.get_vector<int>(child_indices_);
  }
  else
    Throw("illegal 'children' field of type "+hchildren.type().toString());
  
  // now check for correct number of children
  int nchildren = child_indices_.size();
  if( nchildren < check_min_children_ )
    Throw("too few children specified");
  if( check_max_children_ >=0 && nchildren > check_max_children_ )
    Throw("too few children specified");
  // since child_indices_ may be sparsely populated (i.e. if filled from
  // a record above), also check that the first check_min_children are valid
  for( int i=0; i<check_min_children_; i++ )
    FailWhen( child_indices_[i]<0,
        "mandatory child '"+getChildLabel(i).toString()+"' not specified");
  // finally, if labels are specified but we actually have fewer children
  // (because not all labelled children are mandatory), make sure the indices
  // vector is at least as big as the number of labels
//  if( child_indices_.size() < child_labels_.size() )
//    child_indices_.resize(child_labels_.size(),-1);
  
  // put index vector into state record if not empty
  if( !child_indices_.empty() )
    strec[FChildIndices] = child_indices_;
  
  // check that stepchildren field is a vector of indices
  DMI::Record::Hook hstep(strec,FStepChildren);
  if( hstep.exists() )
  {
    FailWhen(hstep.type()!=Tpint,"illegal 'step_children' field of type "+hstep.type().toString());
    hstep.get_vector(stepchild_indices_);
  }
  // check that parents field is a vector of indices
  DMI::Record::Hook hpar(strec,FParents);
  if( hpar.exists() )
    hpar.get_vector(parent_indices_);
}
  
//##ModelId=400E530F0090
void Node::reattachInitRecord (DMI::Record::Ref &initrec, Forest* frst)
{
  cdebug(1)<<"reattaching init record"<<endl;
  forest_ = frst;
      
  // init symdeps and depmask with forest defaults
  depend_mask_ = symdeps().copyMap(forest().symdeps());
  
  // xfer & COW the state record -- we don't want anyone
  // changing it under us
  DMI::Record &rec = staterec_.xfer(initrec).dewr();
  
  // set control state
  control_status_ = rec[FControlStatus].as<int>();
  // set num children based on the FChildren field
  cdebug(2)<<"reinitializing node children"<<endl;
  
  // link up with child nodes
  rec[FChildIndices].get_vector(child_indices_);
  rec[FStepChildren].get_vector(stepchild_indices_);
};


};
