//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820126.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820126.cm

//## begin module%3C10CC820126.cp preserve=no
//## end module%3C10CC820126.cp

//## Module: DataField%3C10CC820126; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataField.cc

//## begin module%3C10CC820126.additionalIncludes preserve=no
//## end module%3C10CC820126.additionalIncludes

//## begin module%3C10CC820126.includes preserve=yes
#include "DynamicTypeManager.h"
//## end module%3C10CC820126.includes

// DataField
#include "DataField.h"
//## begin module%3C10CC820126.declarations preserve=no
//## end module%3C10CC820126.declarations

//## begin module%3C10CC820126.additionalDeclarations preserve=yes
static int nullheader_data[] = {0,0};
static SmartBlock nullheader_block( nullheader_data,sizeof(nullheader_data),DMI::NO_DELETE );
static BlockRef nullheader(nullheader_block,DMI::EXTERNAL|DMI::LOCK|DMI::READONLY);
static ObjRef NullRef;

// this gives the sizes of the built-in types
const size_t typeSizeArray [] = {
   sizeof(char), sizeof(uchar), sizeof(short), sizeof(ushort), sizeof(int), sizeof(uint), 
   sizeof(long), sizeof(ulong), sizeof(float), sizeof(double), sizeof(ldouble), sizeof(string),
   sizeof(bool) };
// correct for first index
const size_t * typeSizeMap = typeSizeArray - Tpbool;

// this inline function returns the size of a built-intype
inline size_t typeSize ( int tid )
    { return typeSizeMap[tid]; }

// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int StdTypeFirst=Tpbool,StdTypeLast=Tpchar;

// returns True if a type is built-in
inline bool isBuiltInType( int tid ) 
    { return tid >= StdTypeFirst && tid <= StdTypeLast; }

//## end module%3C10CC820126.additionalDeclarations


// Class DataField 

DataField::DataField (int flags)
  //## begin DataField::DataField%3C3D64DC016E.hasinit preserve=no
  //## end DataField::DataField%3C3D64DC016E.hasinit
  //## begin DataField::DataField%3C3D64DC016E.initialization preserve=yes
  : mytype(0),selected(False),writable((flags&DMI::WRITE)!=0)
  //## end DataField::DataField%3C3D64DC016E.initialization
{
  //## begin DataField::DataField%3C3D64DC016E.body preserve=yes
  dprintf(2)("default constructor\n");
  //## end DataField::DataField%3C3D64DC016E.body
}

DataField::DataField (const DataField &right, int flags)
  //## begin DataField::DataField%3C3EE3EA022A.hasinit preserve=no
  //## end DataField::DataField%3C3EE3EA022A.hasinit
  //## begin DataField::DataField%3C3EE3EA022A.initialization preserve=yes
    : BlockableObject()
  //## end DataField::DataField%3C3EE3EA022A.initialization
{
  //## begin DataField::DataField%3C3EE3EA022A.body preserve=yes
  dprintf(2)("copy constructor (%s,%x)\n",right.debug(),flags);
  cloneOther(right,flags);
  //## end DataField::DataField%3C3EE3EA022A.body
}

DataField::DataField (TypeId tid, int num, int flags)
  //## begin DataField::DataField%3BFA54540099.hasinit preserve=no
  //## end DataField::DataField%3BFA54540099.hasinit
  //## begin DataField::DataField%3BFA54540099.initialization preserve=yes
    : mytype(tid),mysize(num),writable((flags&DMI::WRITE)!=0)
  //## end DataField::DataField%3BFA54540099.initialization
{
  //## begin DataField::DataField%3BFA54540099.body preserve=yes
  dprintf(2)("constructor(%s,%d,%x)\n",tid.toString().c_str(),num,flags);
  if( !mytype )
  {
    mysize = 0;
    writable = True;
    return;
  }
  built_in = isBuiltInType(mytype);
  if( built_in ) 
  {
    if( mytype == Tpstring )
    {
      headref.attach( new SmartBlock( sizeof(int)*(2+mysize) ),
                      DMI::WRITE|DMI::ANON|DMI::LOCK );
      strvec.resize(mysize);
      strvec_modified = False;
    }
    else
    {
      headref.attach( new SmartBlock( sizeof(int)*2 + typeSize(mytype)*mysize,DMI::ZERO ),
                      DMI::WRITE|DMI::ANON|DMI::LOCK);
    }
  }
  else
  {
    headref.attach( new SmartBlock( sizeof(int)*(2+mysize),DMI::ZERO ),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    objects.resize(mysize);
    blocks.resize(mysize);
    objstate.resize(mysize);
    objstate.assign(mysize,UNINITIALIZED);
  }
  headerType() = mytype;
  headerSize() = mysize;
  // make header block non-writable
  if( !isWritable() )
    headref.change(DMI::READONLY);
  //## end DataField::DataField%3BFA54540099.body
}


DataField::~DataField()
{
  //## begin DataField::~DataField%3BB317D8010B_dest.body preserve=yes
  dprintf(2)("destructor\n");
  destroy();
  //## end DataField::~DataField%3BB317D8010B_dest.body
}


DataField & DataField::operator=(const DataField &right)
{
  //## begin DataField::operator=%3BB317D8010B_assign.body preserve=yes
  dprintf(2)("assignment of %s\n",right.debug());
  destroy();
  cloneOther(right);
  return *this;
  //## end DataField::operator=%3BB317D8010B_assign.body
}



//## Other Operations (implementation)
void DataField::destroy ()
{
  //## begin DataField::destroy%3C3EAB99018D.body preserve=yes
  dprintf(2)("clearing\n");
  if( headref.isValid() )
    headref.unlock().detach();
  strvec.resize(0);
  if( objects.size() ) objects.resize(0);
  if( blocks.size() ) blocks.resize(0);
  objstate.resize(0);
  //## end DataField::destroy%3C3EAB99018D.body
}

bool DataField::isValid (int n)
{
  //## begin DataField::isValid%3C3EB9B902DF.body preserve=yes
  if( !mytype )
    return False;
  checkIndex(n);
  if( built_in ) // built-ins always valid
    return True;
  else
    return objstate[n] != UNINITIALIZED;
  //## end DataField::isValid%3C3EB9B902DF.body
}

const void * DataField::get (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const
{
  //## begin DataField::get%3C5FB272037E.body preserve=yes
  FailWhen( !mytype,"uninitialized data field");
  tid = mytype;
  FailWhen( check_tid && check_tid != tid,"type mismatch in DataField::get" ); 
  can_write = isWritable();
  FailWhen( must_write && !can_write,"r/w access violation" );
  
  checkIndex(n);
  if( built_in )
  {
    if( mytype == Tpstring ) // string? return the string
    {
      ((DataField*)this)->strvec_modified |= can_write; // mark as modified
      return &strvec[n];
    }
    // else return pointer to item
    return n*typeSize(mytype) + (char*)headerData();
  }
  else
  {
    if( must_write )
      return &resolveObject(n,True).dewr();
    else
      return &resolveObject(n,False).deref();
  }
  //## end DataField::get%3C5FB272037E.body
}

ObjRef DataField::objwr (int n, int flags)
{
  //## begin DataField::objwr%3C0E4619019A.body preserve=yes
  FailWhen( !mytype,"uninitialized data field");
  FailWhen( !isWritable(),"field is read-only" );
  checkIndex(n);
  if( isBuiltInType(mytype) )
    return NullRef;
  return resolveObject(n,True).copy(flags);
  //## end DataField::objwr%3C0E4619019A.body
}

ObjRef DataField::objref (int n) const
{
  //## begin DataField::objref%3C3C8D7F03D8.body preserve=yes
  FailWhen( !mytype,"uninitialized data field");
  checkIndex(n);
  if( isBuiltInType(mytype) )
    return NullRef;
  // return a copy as a read-only ref
  return resolveObject(n,False).copy(DMI::READONLY);
  //## end DataField::objref%3C3C8D7F03D8.body
}

void DataField::put (const ObjRef &obj, int n, int flags)
{
  //## begin DataField::put%3C3C84A40176.body preserve=yes
  dprintf(2)("inserting @%d: %s\n",n,obj.debug(2));
  FailWhen( !mytype,"uninitialized data field" );
  FailWhen( !isWritable(),"field is read-only" );
  FailWhen( obj->objectType() != mytype, "type mismatch in DataField::put()" );
  checkIndex(n);
  // grab the ref, and mark object as modified
  if( flags&DMI::COPYREF )
    objects[n].copy(obj,flags);
  else
    objects[n] = obj;
  blocks[n].clear();
  objstate[n] = MODIFIED;
  //## end DataField::put%3C3C84A40176.body
}

ObjRef DataField::remove (int n)
{
  //## begin DataField::remove%3C3EC3470153.body preserve=yes
  FailWhen( !mytype,"uninitialized data field" );
  FailWhen( !isWritable(),"field is read-only" );
  checkIndex(n);
  if( isBuiltInType(mytype) )
    return NullRef;
  // transfer object reference
  ObjRef ret = resolveObject(n,True);
  objstate[n] = UNINITIALIZED;
  dprintf(2)("removing @%d: %s\n",n,ret.debug(2));
  return ret;
  //## end DataField::remove%3C3EC3470153.body
}

int DataField::fromBlock (BlockSet& set)
{
  //## begin DataField::fromBlock%3C3D5F2001DC.body preserve=yes
  dprintf1(2)("%s: fromBlock\n",debug());
  destroy();
  // get header block, privatize & cache it as headref
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(int)*2,"malformed header block" );
  headref.privatize((isWritable()?DMI::WRITE:0)|DMI::LOCK);
  // get type and size from header
  mytype = headerType();
  mysize = headerSize();
  built_in = isBuiltInType(mytype);
  if( !mytype )  // uninitialized field
    return 1;
  // for built-in types, the header block already contains the data. 
  // strings do require some extra treatment
  if( built_in )
  {
    dprintf(2)("fromBlock: built-in type %s[%d]\n",mytype.toString().c_str(),mysize);
    if( mytype == Tpstring )
    {
      // header will contain N string lengths (as ints), followed by the
      // strings themselves
      FailWhen( hsize < sizeof(int)*(2+mysize),"incorrect block size" );
      strvec.resize(mysize);
      // assign the strings
      char *hdata = (char*)headref->data();        // start of header
      size_t istr0 = sizeof(int)*(2+mysize);   // char position of start of first string
      int i=0;
      for( VSI iter = strvec.begin(); iter != strvec.end(); iter++ )
      {
        size_t len = ((int*)hdata)[2+i];
        FailWhen( istr0+len > hsize,"incorrect block size");
        iter->assign(hdata+istr0,len);
        istr0 += len;
      }
      strvec_modified = False; 
    }
    else
      FailWhen( hsize != sizeof(int)*2 + typeSize(mytype)*mysize,
                "incorrect block size" );
    return 1;
  }
  else
  {
    int nref = 1;
    dprintf(2)("fromBlock: dynamic type %s[%d]\n",mytype.toString().c_str(),mysize);
  // for dynamic types, the header contains info on # of blocks to follow
    FailWhen( hsize != sizeof(int)*(2 + mysize),"incorrect block size" );
    objects.resize(mysize);
    blocks.resize(mysize);
    objstate.resize(mysize);
    objstate.assign(mysize,INBLOCK);
  // get blocks from set and privatize them as appropriate
  // do not unblock objects, as that is done at dereference time
    for( int i=0; i<mysize; i++ ) 
    {
      nref += headerBlockSize(i);
      if( headerBlockSize(i) )
      {
        dprintf(3)("fromBlock: [%d] taking over %d blocks\n",i,headerBlockSize(i));
        set.popMove(blocks[i],headerBlockSize(i));
        dprintf(3)("fromBlock: [%d] will privatize %d blocks\n",i,blocks[i].size());
        blocks[i].privatizeAll(isWritable()?DMI::WRITE:0);
      }
      else // no blocks assigned to this object => is uninitialized
        objstate[i] = UNINITIALIZED;
    }
    dprintf(2)("fromBlock: %d blocks were cached\n",nref);
    return nref;
  }
  //## end DataField::fromBlock%3C3D5F2001DC.body
}

int DataField::toBlock (BlockSet &set) const
{
  //## begin DataField::toBlock%3C3D5F2403CC.body preserve=yes
  dprintf1(2)("%s: toBlock\n",debug());
  int nref = 1,tmp; // 1 header block as a minimum
  // if dealing with strings, and they have been modified, the 
  // header block needs to be rebuilt
  if( mytype == Tpstring && strvec_modified )
  {
    // allocate and attach header block
    int hsize = sizeof(int)*(2+mysize);
    for( CVSI iter = strvec.begin(); iter != strvec.end(); iter++ )
      hsize += iter->length();
    headref.attach( new SmartBlock(hsize),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    // write basic fields
    headerType() = mytype;
    headerSize() = mysize;
    // write out lengths and string data into header block
    int *plen = &headerBlockSize(0);
    char *pdata = (char*)(plen + mysize);
    for( CVSI iter = strvec.begin(); iter != strvec.end(); iter++ )
    {
      int len = *plen = iter->length();
      iter->copy(pdata,len); 
      pdata += len;
      plen++;
    }
    strvec_modified = False;
    // if read-only, downgrade block reference
    if( !isWritable() )
      headref.change(DMI::READONLY);
  }
  // push out the header block
  set.push(headref.copy(DMI::READONLY));
  // for dynamic types, do a toBlock on the objects, if needed
  if( !built_in )
  {
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            dprintf(3)("toBlock: [%d] is uninitialized, 0 blocks\n",i);
            headerBlockSize(i) = 0;
            break;
        // then simply copy the blockset
        // if modified, do a toBlock on the object
        case MODIFIED:
            blocks[i].clear();
            tmp = objects[i]->toBlock(blocks[i]);
            dprintf(3)("toBlock: [%d] was modified, converted to %d blocks\n",i,tmp);
            // if no other write refs to the object exist, mark it
            // as unmodified again
            if( objects[i].hasOtherWriters() )
              objstate[i] = UNBLOCKED;
            // fall thru below to add blocks to set
        // if still in block, or unblocked but not modified,
        case INBLOCK:
        case UNBLOCKED:
            dprintf(3)("toBlock: [%d] copying %d blocks\n",i,blocks[i].size());
            set.pushCopy(blocks[i]);
            nref += headerBlockSize(i) = blocks[i].size();
            break;
        default:
            Throw("illegal object state");
      }
    }
  } 
  dprintf(2)("toBlock: %d blocks returned\n",nref);
  return nref;
  //## end DataField::toBlock%3C3D5F2403CC.body
}

ObjRef & DataField::resolveObject (int n, bool write) const
{
  //## begin DataField::resolveObject%3C3D8C07027F.body preserve=yes
  switch( objstate[n] )
  {
    // uninitialized object - create default
    case UNINITIALIZED:
         objects[n].attach( DynamicTypeManager::construct(mytype),
                           (isWritable()?DMI::WRITE:DMI::READONLY)|
                           DMI::ANON|DMI::LOCK );
         objstate[n] = MODIFIED;
         return objects[n];
         
    // object hasn't been unblocked
    case INBLOCK:
         // if write access requested, simply unblock it
         if( write )
         {
           objects[n].attach( DynamicTypeManager::construct(mytype,blocks[n]),
                             (isWritable()?DMI::WRITE:DMI::READONLY)|
                             DMI::ANON|DMI::LOCK );
           // verify that no blocks were left over
           FailWhen( blocks[n].size()>0,"block count mismatch" );
           objstate[n] = MODIFIED;
         }
         // For r/o access, we want to cache a copy of the blockset.
         // This is in case the object doesn't get modified down the road, 
         // so we can just re-use the blockset in a future toBlock()
         else
         {
           // make copy, retaining r/w privileges, and marking the 
           // source as r/o
           BlockSet set( blocks[n],DMI::PRESERVE_RW|DMI::MAKE_READONLY ); 
           // create object and attach a reference
           objects[n].attach( DynamicTypeManager::construct(mytype,set),
                             (isWritable()?DMI::WRITE:DMI::READONLY)|
                             DMI::ANON|DMI::LOCK );
           // verify that no blocks were left over
           FailWhen( set.size()>0,"block count mismatch" );
           // mark object as unblocked but not modified 
           objstate[n] = UNBLOCKED; 
         }
         return objects[n];

    // object exists, hasn't been modified
    case UNBLOCKED:
         if( write )
         {
           // requesting write access to a previously unmodified object:
           // flush cached blocks and mark as modified
           blocks[n].clear();
           objstate[n] = MODIFIED;
         }
         return objects[n];
    
    // object exists and has been modified - simply return the ref
    case MODIFIED:
         return objects[n];
    
    default:
         Throw("illegal object state");
  }
  return objects[n];
  //## end DataField::resolveObject%3C3D8C07027F.body
}

CountedRefTarget* DataField::clone (int flags) const
{
  //## begin DataField::clone%3C3EC77D02B1.body preserve=yes
  return new DataField(*this,flags);
  //## end DataField::clone%3C3EC77D02B1.body
}

void DataField::cloneOther (const DataField &other, int flags)
{
  //## begin DataField::cloneOther%3C3EE42D0136.body preserve=yes
  // setup misc fields
  built_in = isBuiltInType( mytype = other.type() );
  mysize = other.size();
  writable = (flags&DMI::WRITE)!=0;
  selected = False;
  // copy & privatize the header ref
  headref.copy(other.headref).privatize(flags|DMI::LOCK);
  // handle built-in types -- only strings need to be copied
  if( built_in )
  {
    if( mytype == Tpstring ) 
    {
      strvec = other.strvec;
      strvec_modified = other.strvec_modified;
    }
  }
  // handle dynamic types
  else
  {
    objstate = other.objstate;
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            break;
        // if still in block, then copy & privatize the blockset
        case INBLOCK:
            blocks[i] = other.blocks[i]; // blockset copy (=ref.copy)
            if( flags&DMI::DEEP )
              blocks[i].privatizeAll(flags);
            break;
        // otherwise, privatize the object reference
        case UNBLOCKED:
        case MODIFIED:
            objects[i].copy(other.objects[i],flags|DMI::LOCK);
            if( flags&DMI::DEEP );
              objects[i].privatize(flags|DMI::LOCK);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  //## end DataField::cloneOther%3C3EE42D0136.body
}

void DataField::privatize (int flags)
{
  //## begin DataField::privatize%3C3EDEBC0255.body preserve=yes
  writable = (flags&DMI::WRITE) != 0;
  if( !mytype )
    return;
  // privatize the header reference
  headref.privatize(DMI::WRITE|DMI::LOCK);
  // if deep privatization is required, then for dynamic objects, 
  // privatize the field contents as well
  if( flags&DMI::DEEP && !built_in )
  {
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            break;
        // if still in block, then privatize the blockset
        case INBLOCK:
            blocks[i].privatizeAll(flags);
            break;
        // otherwise, privatize the object reference
        case UNBLOCKED:
        case MODIFIED:
            objects[i].privatize(flags|DMI::LOCK);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  //## end DataField::privatize%3C3EDEBC0255.body
}

// Additional Declarations
  //## begin DataField%3BB317D8010B.declarations preserve=yes
string DataField::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataField::sdebug() calls";
    abort();
  }
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:"DataField",(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::append(out,isWritable()?"RW ":"RO ");
    if( !type() )
      out += "empty";
    else
      out += type().toString()+Debug::ssprintf(":%d",size());
    out += " / refs "+CountedRefTarget::sdebug(-1);
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"      ");
    if( str.length() )
      out += "\n"+prefix+"  refs: "+str;
  }
  if( !built_in && (detail >= 2 || detail <= -2) && size()>0 )   // high detail
  {
    // append object list
    for( int i=0; i<size(); i++ )
    {
      if( out.length() )
        out += "\n"+prefix;
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            out += "    "+Debug::ssprintf("%d: uninitialized",i);
            break;
        case INBLOCK:
            out += "    "+Debug::ssprintf("%d: in block: ",i)
                         +blocks[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        case UNBLOCKED:
            out += "    "+Debug::ssprintf("%d: unblocked [",i)
                         +blocks[i].sdebug(abs(detail)-1,prefix+"    ")
                         +"], to"
                         +objects[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        case MODIFIED:
            out += "    "+Debug::ssprintf("%d: modified ",i)
                         +objects[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  nesting--;
  return out;
}
  //## end DataField%3BB317D8010B.declarations
//## begin module%3C10CC820126.epilog preserve=yes
//## end module%3C10CC820126.epilog
