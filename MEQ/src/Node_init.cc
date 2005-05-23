#include "Node.h"
#include "MeqVocabulary.h"
#include "Forest.h"
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>

namespace Meq {

using Debug::ssprintf;

// this initializes the children-related fields
//##ModelId=400E531F0085
void Node::initChildren (int nch)
{
  // check against expected number
  if( check_nchildren_ >= 0 && !check_nmandatory_ )
  {
    FailWhen( nch != check_nchildren_,
              ssprintf("%d children specified, %d expected",nch,check_nchildren_) );
  }
  FailWhen( nch < check_nmandatory_,
            ssprintf("%d children specified, at least %d expected",
            nch,check_nmandatory_) );
  children_.resize(nch);
  // form the children name/index fields
  if( nch )
  {
    DMI::Container *p1,*p2;
    if( !child_labels_.empty() ) // children are labelled: use records
    {
      wstate()[FChildren] <<= new DMI::Record;
      wstate()[FChildrenNames] <<= new DMI::Record;
    }
    else // children are unlabelled: use fields
    {
      wstate()[FChildren] <<= new DMI::Vec(Tpint,nch);
      wstate()[FChildrenNames] <<= new DMI::Vec(Tpstring,nch);
    }
    // set up map from label to child number 
    // (if no labels are defined, trivial "0", "1", etc. are used)
    for( int i=0; i<nch; i++ )
      child_map_[getChildLabel(i)] = i;
  }
  else
  {
    wstate()[FChildren].remove();
    wstate()[FChildrenNames].remove();
  }
}

// this initializes the stepchildren-related fields
//##ModelId=400E531F0085
void Node::initStepChildren (int nch)
{
  stepchildren_.resize(nch);
  // form the children name/index fields
  if( nch )
  {
    wstate()[FStepChildren] <<= new DMI::Vec(Tpint,nch);
    wstate()[FStepChildrenNames] <<= new DMI::Vec(Tpstring,nch);
  }
  else
  {
    wstate()[FStepChildren].remove();
    wstate()[FStepChildrenNames].remove();
  }
}

const std::string & Node::childName (int i) const
{
  FailWhen(i<0 || i>=numChildren(),"illegal child index");
  if( children_[i].valid() )
    return children_[i]->name();
  else
    return state()[FChildrenNames][i];
}


//##ModelId=3F8433C20193
void Node::addChild (const HIID &id,Node::Ref &childnode)
{
  int ich;
  // numeric id is simply child number
  if( id.length() == 1 && id[0].id() >= 0 )
  {
    ich = id[0].id();
    FailWhen(ich<0 || ich>=numChildren(),"child number "+id.toString()+" is out of range");
  }
  else // non-numeric: look in in child labels
  {
    // look for id within child labels
    vector<HIID>::const_iterator lbl;
    lbl = std::find(child_labels_.begin(),child_labels_.end(),id);
    FailWhen(lbl == child_labels_.end(),id.toString() + ": unknown child label");
    ich = lbl - child_labels_.begin();
  }
  // attach ref to child if specified (will stay unresolved otherwise)
  wstate()[FChildrenNames][getChildLabel(ich)] = childnode->name();
  wstate()[FChildren][getChildLabel(ich)] = childnode->nodeIndex();
  children_[ich].xfer(childnode,DMI::SHARED);
  cdebug(3)<<"added child "<<ich<<": "<<id<<endl;
}

void Node::addStepChild (int n,Node::Ref &childnode)
{
  FailWhen(n<0 || n>=numStepChildren(),"stepchild number is out of range");
  // attach ref to child if specified (will stay unresolved otherwise)
  wstate()[FStepChildrenNames][n] = childnode->name();
  wstate()[FStepChildren][n] = childnode->nodeIndex();
  stepchildren_[n].xfer(childnode,DMI::SHARED);
  cdebug(3)<<"added stepchild "<<n<<endl;
}

//##ModelId=3F9505E50010
void Node::processChildSpec (DMI::Container &children,const HIID &chid,const HIID &id,bool stepchild)
{
  const string which = stepchild ? "stepchild" : "child";
  // child specified by init-record: create recursively
  TypeId spec_type = children[id].type();
  if( spec_type == TpDMIRecord )
  {
    cdebug(4)<<"  "<<which<<" "<<id<<" specified by init record"<<endl;
    DMI::Record::Ref child_initrec = children[id].ref();
    // check if named child already exists
    string name = child_initrec[FName].as<string>("");
    int index = -1;
    if( !name.empty() && ( index = forest_->findIndex(name) ) >= 0 )
    {
      cdebug(4)<<"  "<<which<<" already exists as #"<<index<<endl;
      // If link_or_create=T, we allow this, otherwise, throw exception
      if( !child_initrec[FLinkOrCreate].as<bool>(false) )
      {
        Throw("Failed to create child node "+id.toString()+": a node named '"
              +name+"' already exists");
      }
      Node::Ref childref(forest_->get(index),DMI::SHARED);
      cdebug(2)<<"  "<<which<<" "<<id<<"="<<name<<" relinked as #"<<index<<endl;
      stepchild ? addStepChild(chid[0],childref) : addChild(chid,childref);
    }
    else
    {
      try
      {
        cdebug(2)<<"  creating "<<which<<" "<<id<<endl;
        Node::Ref childref(forest_->create(index,child_initrec.ref_cast<DMI::Record>()),DMI::SHARED);
        stepchild ? addStepChild(chid[0],childref) : addChild(chid,childref);
      }
      catch( std::exception &exc )
      {
        Throw("Failed to create "+which+" node "+id.toString()+": "+exc.what());
      }
    }
  }
  else // not an init record
  {
    if( TypeInfo::isArray(spec_type) )
      spec_type = TypeInfo::typeOfArrayElem(spec_type);
    cdebug(4)<<"  "<<which<<" "<<id<<" entry of type "<<spec_type<<endl;
    // child specified by name -- look it up in the forest
    if( spec_type == Tpstring )
    {
      const string & name = children[id].as<string>();
      if( name.length() ) // skip if empty string
      {
        int index = forest_->findIndex(name);
        if( index >= 0 )
        {
          Node::Ref childref(forest_->get(index),DMI::SHARED);
          cdebug(2)<<"  "<<which<<" "<<id<<"="<<name<<" resolves to node "<<index<<endl;
          stepchild ? addStepChild(chid[0],childref) : addChild(chid,childref);
        }
        else
        { // defer until later if not found
          cdebug(2)<<"  "<<which<<" "<<id<<"="<<name<<" currently unresolved"<<endl;
          // add to child names so that we remember the name at least 
          wstate()[stepchild?FStepChildrenNames:FChildrenNames][chid] = name;
        }
      }
    }
    // child specified by index -- just get & attach it directly
    else if( spec_type == Tpint )
    {
      int index = children[id];
      Node::Ref childref(forest_->get(index),DMI::SHARED);
      cdebug(2)<<"  "<<which<<" "<<id<<"="<<index<<endl;
      stepchild ? addStepChild(chid[0],childref) : addChild(chid,childref);
    }
    else
      Throw("illegal specification for "+which+" "+id.toString()+" (type "+
            spec_type.toString()+")");
  }
}

void Node::setupChildren (DMI::Record &initrec,bool stepchildren)
{
  const HIID &id0 = stepchildren ? FStepChildren : FChildren;
  DMI::Record::Hook hchildren(initrec,id0);
  if( hchildren.type() == Tpbool && hchildren.size() == 1 &&
      !hchildren.as<bool>() )
  {
    cdebug(2)<<id0<<"=[F], skipping child creation"<<endl;
  }
  else if( hchildren.exists() )
  {
    ObjRef ref = hchildren.remove();
    // children specified via a record
    if( ref->objectType() == TpDMIRecord )
    {
      DMI::Record &childrec = ref.as<DMI::Record>();
      stepchildren ? initStepChildren(childrec.size()) : initChildren(childrec.size());
      // iterate through children record and create the child nodes
      int ifield = 0;
      for( DMI::Record::Iterator iter = childrec.begin(); iter != childrec.end(); iter++ )
      {
        const HIID &id = iter.id();
        // for normal children with child labels, use the label as index into
        // the record
        processChildSpec(childrec,stepchildren || child_labels_.empty()?AtomicID(ifield):id,id,stepchildren);
        ifield++;
      }
    }
    else if( ref->objectType() == TpDMIVec || ref->objectType() == TpDMIList )
    {
      DMI::Container &childrec = ref.as<DMI::Container>();
      stepchildren ? initStepChildren(childrec.size()) : initChildren(childrec.size());
      for( int i=0; i<childrec.size(); i++ )
        processChildSpec(childrec,AtomicID(i),AtomicID(i),stepchildren);
    }
    else if( ref->objectType() == TpDMINumArray )
    {
      DMI::NumArray &childarr = ref.as<DMI::NumArray>();
      FailWhen(childarr.rank()!=1,"illegal child array");
      int nch = childarr.shape()[0];
      stepchildren ? initStepChildren(nch) : initChildren(nch);
      for( int i=0; i<nch; i++ )
        processChildSpec(childarr,AtomicID(i),AtomicID(i),stepchildren);
    }
  }
}

// relink children -- resets pointers to all children. This is called
// after restoring a node from a file. 
//##ModelId=400E531101C8
void Node::relinkChildren ()
{
  for( int i=0; i<numChildren(); i++ )
    children_[i].attach(forest().get(state()[FChildren][getChildLabel(i)]),DMI::SHARED);
  for( int i=0; i<numStepChildren(); i++ )
    stepchildren_[i].attach(forest().get(state()[FStepChildren][i]),DMI::SHARED);
  checkChildren();
}

//##ModelId=3F83FAC80375
void Node::resolveChildren (bool recursive)
{
  cdebug(2)<<"resolving children\n";
  for( int i=0; i<numChildren(); i++ )
  {
    if( !children_[i].valid() )
    {
      HIID label = getChildLabel(i);
      string name = state()[FChildrenNames][label].as<string>();
      cdebug(3)<<"resolving child "<<i<<":"<<name<<endl;
      // findNode() will throw an exception if the node is not found,
      // which is exactly what we want
      try
      {
        Node &childnode = forest_->findNode(name);
        children_[i].attach(childnode,DMI::SHARED);
        wstate()[FChildren][label] = childnode.nodeIndex();
      }
      catch( ... )
      {
        Throw(Debug::ssprintf("failed to resolve child %d:%s",i,name.c_str()));
      }
    }
    // recursively call resolve on the children
    if( recursive )
      children_[i]().resolveChildren();
  }
  // check children for consistency
  checkChildren();
  
  cdebug(2)<<"resolving stepchildren\n";
  for( int i=0; i<numStepChildren(); i++ )
  {
    if( !stepchildren_[i].valid() )
    {
      string name = state()[FStepChildrenNames][i].as<string>();
      cdebug(3)<<"resolving stepchild "<<i<<":"<<name<<endl;
      // findNode() will throw an exception if the node is not found,
      // which is exactly what we want
      try
      {
        Node &childnode = forest_->findNode(name);
        stepchildren_[i].attach(childnode,DMI::SHARED);
        wstate()[FStepChildren][i] = childnode.nodeIndex();
      }
      catch( ... )
      {
        Throw(Debug::ssprintf("failed to resolve stepchild %d:%s",i,name.c_str()));
      }
    }
    // recursively call resolve on the children
    if( recursive )
      stepchildren_[i]().resolveChildren();
  }
}

//##ModelId=3F5F45D202D5
void Node::init (DMI::Record::Ref &initrec, Forest* frst)
{
  cdebug(1)<<"initializing node"<<endl;
  forest_ = frst;
  
  // init symdeps and depmask
  symdep_masks_ = frst->getSymdepMasks();
  resetDependMasks();
  
  // xfer & COW the state record
  DMI::Record &rec = staterec_.xfer(initrec).dewr();
  
  // set defaults and check for missing fields
  cdebug(2)<<"initializing node (checkInitState)"<<endl;
  // add node class if needed, else check for consistency
  if( rec[FClass].exists() )
  {
    FailWhen(strlowercase(rec[FClass].as<string>()) != strlowercase(objectType().toString()),
      "node class does not match initrec.class. This is not supposed to happen!");
  }
  else
    rec[FClass] = objectType().toString();
  // do other checks
  FailWhen(rec[FResolveParentId].exists(),"can't specify "+FResolveParentId.toString()+" in init record");
  node_resolve_id_ = -1;
  checkInitState(staterec_);
  // add state word
  rec[FControlStatus] = control_status_;
  // set node index, if specified
  if( rec[FNodeIndex].exists() )
    node_index_ = rec[FNodeIndex].as<int>();
  
  // setup children
  cdebug(2)<<"initializing node children"<<endl;
  setupChildren(rec,false);
  // if a mandatory number of children (NM) is requested, make sure
  // that the first NM children are set
  if( check_nmandatory_ )
  {
    FailWhen(numChildren()<check_nmandatory_,"too few children specified");
    for( int i=0; i<check_nmandatory_; i++ )
      if( !children_[i].valid() && 
          state()[FChildrenNames][child_map_[getChildLabel(i)]].as<string>().empty() )
      {
        Throw("mandatory child "+getChildLabel(i).toString()+" not specified" );
      }
  }
  rcr_cache_.resize(numChildren());
  cdebug(2)<<"initialized with "<<numChildren()<<" children"<<endl;
  cdebug(2)<<"initializing node step children"<<endl;
  setupChildren(rec,true);
  cdebug(2)<<"initialized with "<<numStepChildren()<<" stepchildren"<<endl;
  
  cdebug(2)<<"initializing node (setStateImpl)"<<endl;
  cdebug(3)<<"initial state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_,true);
}

//##ModelId=400E530F0090
void Node::reinit (DMI::Record::Ref &initrec, Forest* frst)
{
  cdebug(1)<<"reinitializing node"<<endl;
  forest_ = frst;
      
  // xfer & COW the state record -- we don't want anyone
  // changing it under us
  DMI::Record &rec = staterec_.xfer(initrec).dewr();

  // set control state
  control_status_ = rec[FControlStatus].as<int>();
  // set num children based on the FChildren field
  cdebug(2)<<"reinitializing node children"<<endl;
  // set node index, if specified
  if( rec[FNodeIndex].exists() )
    node_index_ = rec[FNodeIndex].as<int>();
  // set resolve ID, if any
  node_resolve_id_ = rec[FResolveParentId].as<int>(-1);
  
  // setup children directly from relevant fields
  int nch = rec[FChildrenNames].size();
  if( nch )
  {
    children_.resize(nch);
    child_retcodes_.resize(nch);
    for( int i=0; i<nch; i++ )
      child_map_[getChildLabel(i)] = i;
    rcr_cache_.resize(nch);
    cdebug(2)<<"reinitialized with "<<nch<<" children"<<endl;
  }
  else
  {
    cdebug(2)<<"no children to reintialize"<<endl;
  }
  // setup stepchildren directly from relevant fields
  nch = rec[FStepChildrenNames].size();
  if( nch )
  {
    stepchildren_.resize(nch);
    stepchild_retcodes_.resize(nch);
    cdebug(2)<<"reinitialized with "<<nch<<" stepchildren"<<endl;
  }
  else
  {
    cdebug(3)<<"no stepchildren to reintialize"<<endl;
  }
  // finally, call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"reinitializing node (setStateImpl)"<<endl;
  cdebug(3)<<"state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_,true);
}  


};
