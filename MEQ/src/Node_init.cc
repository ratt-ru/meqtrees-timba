#include "Node.h"
#include "MeqVocabulary.h"
#include "Forest.h"
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>

namespace Meq {

using Debug::ssprintf;

// this initializes the children-related members. Called from init() and reinit()
void Node::allocChildSupport (int nch)
{
  children_.resize(nch);
  child_results_.resize(nch);
  child_retcodes_.resize(nch);
  child_fails_.reserve(nch);
  rcr_cache_.resize(nch);
}

// this initializes the children-related state fields, called from init()
// only. reinit() uses its own code, see below
//##ModelId=400E531F0085
void Node::initChildren (int nch)
{
  // check against expected number
  if( check_min_children_ == check_max_children_ )
  {
    FailWhen(check_max_children_>=0 && nch != check_max_children_,
            ssprintf("%d children specified, %d expected",
            nch,check_max_children_ ));
  }
  else 
  { 
    FailWhen( check_min_children_>=0 && nch < check_min_children_,
              ssprintf("%d children specified, at least %d expected",
              nch,check_min_children_ ));
    FailWhen( check_max_children_>=0 && nch > check_max_children_,
              ssprintf("%d children specified, at most %d expected",
              nch,check_max_children_ ));
  }
  // if initializing fewer children than we have labels, adjust nch upwards,
  // so that we have "missing" children for any unfilled labels
  if( nch < int(child_labels_.size()) )
    nch = child_labels_.size();
  
  allocChildSupport(nch);
  // form the children name/index fields
  if( nch )
  {
    DMI::Container *p1,*p2;
    if( !child_labels_.empty() ) // children are labelled: use records
    {
      DMI::Record *chrec,*namerec;
      wstate()[FChildren] <<= chrec = new DMI::Record;
      wstate()[FChildrenNames] <<= namerec = new DMI::Record;
      for( uint i=0 ;i<child_labels_.size(); i++ )
      {
        (*chrec)[child_labels_[i]] = -1;
        (*namerec)[child_labels_[i]] = "";
      }
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
    FailWhen(ich<0 || ich>numChildren(),"child number "+id.toString()+" is out of range");
    if( ich == numChildren() )
    {
      if( !ich )
        initChildren(1);
      else
        allocChildSupport(ich+1); // vecs in state record will take care of themselves
    }
  }
  else // non-numeric: look in in child labels
  {
    // look for id within child labels
    vector<HIID>::const_iterator lbl;
    lbl = std::find(child_labels_.begin(),child_labels_.end(),id);
    FailWhen(lbl == child_labels_.end(),"'"+id.toString() + "': unknown child label");
    ich = lbl - child_labels_.begin();
  }
  wstate()[FChildrenNames][getChildLabel(ich)] = childnode->name();
  wstate()[FChildren][getChildLabel(ich)] = childnode->nodeIndex();
  children_[ich].xfer(childnode,DMI::SHARED);
  cdebug(3)<<"added child "<<ich<<": "<<id<<endl;
}

void Node::addStepChild (int n,Node::Ref &childnode)
{
  FailWhen(n<0 || n>numStepChildren(),"stepchild number is out of range");
  // adding stepchild on-the-fly?
  if( n == numStepChildren() )
  {
    if( !n )
      initStepChildren(1);
    else
      stepchildren_.resize(n+1); // vecs in state record will take care of themselves
  }
  wstate()[FStepChildrenNames][n] = childnode->name();
  wstate()[FStepChildren][n] = childnode->nodeIndex();
  stepchildren_[n].xfer(childnode,DMI::SHARED);
  cdebug(3)<<"added stepchild "<<n<<endl;
}

//##ModelId=3F9505E50010
bool Node::processChildSpec (DMI::Container &children,const HIID &chid,const HIID &id,bool stepchild)
{
  const string which = stepchild ? "stepchild" : "child";
  DMI::Container::Hook ch_hook(children,id);
  TypeId spec_type = ch_hook.type();
  // child specified by missing ref (i.e. None): no child
  if( ch_hook.isRef() && !(ch_hook.ref(true).valid()) )
  {
    return false;
  }
  // child specified by init-record: create recursively
  else if( spec_type == TpDMIRecord )
  {
    cdebug(4)<<"  "<<which<<" "<<id<<" specified by init record"<<endl;
    DMI::Record::Ref child_initrec = ch_hook.ref();
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
        ThrowMore(exc,"failed to create "+which+" node "+id.toString());
      }
      catch( ... )
      {
        Throw("failed to create "+which+" node "+id.toString());
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
      const string & name = ch_hook.as<string>();
      if( name.empty() )
        return false;
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
    // child specified by index -- just get & attach it directly
    else if( spec_type == Tpint )
    {
      int index = ch_hook.as<int>();
      if( !index )
        return false;
      Node::Ref childref(forest_->get(index),DMI::SHARED);
      cdebug(2)<<"  "<<which<<" "<<id<<"="<<index<<endl;
      stepchild ? addStepChild(chid[0],childref) : addChild(chid,childref);
    }
    else
      Throw("illegal specification for "+which+" "+id.toString()+" (type "+
            spec_type.toString()+")");
  }
  return true;
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
  const DMI::Record &st = state();
  for( int i=0; i<numChildren(); i++ )
  {
    HIID label = getChildLabel(i);
    int nodeindex = st[FChildren][label];
    if( nodeindex >= 0 )
      children_[i].attach(forest().get(nodeindex),DMI::SHARED);
    else
    {
      FailWhen(i<check_min_children_,"mandatory child "+label.toString()+" missing");
    }
  }
  for( int i=0; i<numStepChildren(); i++ )
    stepchildren_[i].attach(forest().get(state()[FStepChildren][i]),DMI::SHARED);
  checkChildren();
}

//##ModelId=3F83FAC80375
void Node::resolveChildren ()
{
  cdebug(2)<<"resolving children\n";
  for( int i=0; i<numChildren(); i++ )
  {
    if( !children_[i].valid() )
    {
      HIID label = getChildLabel(i);
      string name = state()[FChildrenNames][label].as<string>();
      if( name.empty() )
      {
        FailWhen(i<check_min_children_,"mandatory child "+label.toString()+" missing");
        wstate()[FChildren][label] = -1;
      }
      else
      {
        cdebug(3)<<"resolving child "<<i<<":"<<name<<endl;
        int nodeindex = forest_->findIndex(name);
        FailWhen(nodeindex<0,"failed to resolve child "+label.toString()+": node '"+name+"' not found");
        Node &childnode = forest_->get(nodeindex);
        children_[i].attach(childnode,DMI::SHARED);
        wstate()[FChildren][label] = nodeindex;
      }
    }
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
      catch( std::exception &exc )
      {
        ThrowMore(exc,Debug::ssprintf("failed to resolve stepchild %d ('%s')",i,name.c_str()));
      }
      catch( ... )
      {
        Throw(Debug::ssprintf("failed to resolve stepchild %d ('%s')",i,name.c_str()));
      }
    }
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
      "node class does not match initrec.class. This is clearly impossible, please try an alternative universe!");
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
  // if a minimum number of children is expected, make sure that that 
  // number of children is actually supplied
  if( check_min_children_>=0 )
  {
    FailWhen(numChildren()<check_min_children_,"too few children specified");
    for( int i=0; i<check_min_children_; i++ )
      if( !children_[i].valid() && 
          state()[FChildrenNames][getChildLabel(i)].as<string>("").empty() )
      {
        Throw("mandatory child "+getChildLabel(i).toString()+" not specified" );
      }
  }
  // if no children were supplied but we do have labels, init empty arrays for 
  // them anyway
  if( !numChildren() )
  {
    cdebug(2)<<"initialized with no children"<<endl;
    if( !child_labels_.empty() )
    {
      cdebug(2)<<"labels supplied, initializing empty arrays"<<endl;
      initChildren(0);
    }
  }
  else
  {
    cdebug(2)<<"initialized with "<<numChildren()<<" children"<<endl;
  }
  // initialize stepchildren
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
      
  // init symdeps and depmask
  symdep_masks_ = frst->getSymdepMasks();
  resetDependMasks();
  
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
    allocChildSupport(nch);
    for( int i=0; i<nch; i++ )
      child_map_[getChildLabel(i)] = i;
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
