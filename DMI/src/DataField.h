//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef DataField_h
#define DataField_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "DMI/TypeInfo.h"
#include "DMI/HIID.h"

// BlockSet
#include "DMI/BlockSet.h"
// BlockableObject
#include "DMI/BlockableObject.h"
// NestableContainer
#include "DMI/NestableContainer.h"
#include "BlockRef1.h"
#pragma type #DataField


class DataRecord;

//##ModelId=3BB317D8010B

class DataField : public NestableContainer
{
  friend class DataRecord;

  public:
      //##ModelId=3C3D64DC016E
      explicit DataField (int flags = DMI::WRITE);

      //##ModelId=3C3EE3EA022A
      DataField (const DataField &right, int flags = DMI::PRESERVE_RW, int depth = 0);

      //##ModelId=3BFA54540099
      //##Documentation
      //## Constructs an empty data field
      explicit DataField (TypeId tid, int num = -1, int flags = DMI::WRITE, const void *data = 0);

    //##ModelId=3DB9346F0095
      ~DataField();

    //##ModelId=3DB9346F017B
      DataField & operator=(const DataField &right);


      //##ModelId=3C6161190193
      DataField & init (TypeId tid, int num = -1, const void *data = 0);

      //##ModelId=3C627A64008E
      bool valid () const;

      //##ModelId=3C62961D021B
      void resize (int newsize);

      //##ModelId=3C3EC27F0227
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const;

      //##ModelId=3C3EAB99018D
      void clear (int flags = DMI::WRITE);

      //##ModelId=3C3EB9B902DF
      bool isValid (int n = 0);

      //##ModelId=3C0E4619019A
      ObjRef objwr (int n = 0, int flags = DMI::PRESERVE_RW);

      //##ModelId=3C7A305F0071
      DataField & put (int n, ObjRef &ref, int flags = DMI::XFER);

      //##ModelId=3C3C8D7F03D8
      ObjRef objref (int n = 0) const;

      //##ModelId=3C3D5F2001DC
      //##Documentation
      //## Creates object from a set of block references. Appropriate number of
      //## references are removed from the head of the BlockSet. Returns # of
      //## refs removed.
      virtual int fromBlock (BlockSet& set);

      //##ModelId=3C3D5F2403CC
      //##Documentation
      //## Stores an object into a set of blocks. Appropriate number of refs
      //## added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //##ModelId=3C3EC77D02B1
      //##Documentation
      //## Clones a data field. (See CountedRefTarget::clone() for semantics)
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //##ModelId=3C3EE42D0136
      void cloneOther (const DataField &other, int flags, int depth);

      //##ModelId=3C3EDEBC0255
      //##Documentation
      //## Makes a private snapshot of the field, by privatizing all contents.
      //## Use DMI::WRITE to make a writable field.
      void privatize (int flags = 0, int depth = 0);

      //##ModelId=3D05E2F301D2
      //##Documentation
      //## Abstract method. Must returns the number of elements in the
      //## container.
      virtual int size (TypeId tid = 0) const;

      //##ModelId=3C7A19790361
      //##Documentation
      //## Abstract virtual function for dereferencing a container field. Must
      //## be implemented by all child classes. fieldType() and operator [],
      //## below, are (by default) implemented in terms of this function
      //## (although they may be re-implemented in subclasses for efficiency) .
      //## Returns a pointer to the field data (0 for no such field).  Returns
      //## the type and writable property in 'tid' and 'can_write'. If must_
      //## write is True, throws exception if data is read-only. Can throw
      //## exceptions if id is malformed (i.e. contains indices that are out of
      //## range).
      virtual const void * get (const HIID &id, ContentInfo &info, TypeId check_tid = 0, int flags = 0) const;

      //##ModelId=3C7A1983024D
      virtual const void * getn (int n, ContentInfo &info, TypeId check_tid = 0, int flags = 0) const;

      //##ModelId=3C7A198A0347
      virtual void * insert (const HIID &id, TypeId tid, TypeId &real_tid);

      //##ModelId=3C7A19930250
      virtual void * insertn (int n, TypeId tid, TypeId &real_tid);

      //##ModelId=3C877E1E03BE
      //##Documentation
      //## If given a single-index HIID, maps to removen(n). Otherwise, if
      //## field contains a single container, calls remove(id) on that.
      virtual bool remove (const HIID &id);

      //##ModelId=3C877E260301
      //##Documentation
      //## Removes object at specified index. Can only remove from the end of
      //## the array.
      virtual bool removen (int n);

    //##ModelId=3DB934720017
      TypeId type () const;

    //##ModelId=3DB9347201EE
      int mysize () const;

    //##ModelId=3DB9347203B0
      bool isSelected () const;

    //##ModelId=3DB93473019F
      bool isScalar () const;

    // Additional Public Declarations
    //##ModelId=3DB9343B00B9
      typedef CountedRef<DataField> Ref;
      
      // standard debug info method
    //##ModelId=3DB934730394
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

      // helper function for making a type[num] string
    //##ModelId=3DB9347601A8
      inline static string typeString (TypeId tid,int size) 
      { return Debug::ssprintf("%s[%d]",tid.toString().c_str(),size); };
      
      
  protected:

      //##ModelId=3C3D8C07027F
      ObjRef & resolveObject (int n, int flags = 0) const;

    // Additional Protected Declarations
      // Used by various puts() to get the ObjRef at position n.
      // Inits/auto-extends field if necessary, checks types, does
      // various housekeeping.
    //##ModelId=3DB9347800CF
      ObjRef & prepareForPut (TypeId tid,int n);
      
      // gets sub-record at position n, throws exception if field
      // does not contain a DataRecord
    //##ModelId=3DB9347A0027
      const DataRecord * getSubRecord( bool write,int n=0 ) const;
  private:
    // Additional Private Declarations
      // verifies that index is in range
    //##ModelId=3DB9347C00FD
      void checkIndex ( int n ) const;
      
      // header block, maintained as a SmartBlock. Contains type and size
      // info. For built-in types, also contains the data block itself.
      // For dynamic objects, contains info on # of blocks per each object
      
      // state of each object - still in block / unblocked / modified
    //##ModelId=3DB9343B0196
      typedef enum { UNINITIALIZED=0,INBLOCK=1,UNBLOCKED=2,MODIFIED=3 } ObjectState;
    //##ModelId=3DB934680272
      mutable vector<int> objstate;

    //##ModelId=3DB934690197
      TypeInfo typeinfo;  // type info for current field

      // for SPECIAL category types (string, HIID), this holds a vector of objects
    //##ModelId=3DB9346A0026
      void *spvec;
      // this is the address of the delete method, called to delete spvec
    //##ModelId=3DB9346A032D
      TypeInfo::DeleteMethod spdelete;
    //##ModelId=3DB9346B01E4
      mutable bool spvec_modified; // flag: vector has been modified
      
      // flag: field contains a simple type handled by binary copying
      // (TypeInfo category NUMERIC or BINARY)
    //##ModelId=3DB9346C0145
      bool    binary_type;
      // flag: field contains a dynamic type
      // (if both are clear, then it's a SPECIAL type
    //##ModelId=3DB9346D0006
      bool    dynamic_type;
      // flag: field contains a subcontainer
    //##ModelId=3DB9346D02C3
      bool    container_type;
      
      // inlines for accessing the header block
    //##ModelId=3DB9347D02AD
      int & headerType () const { return ((int*)headref->data())[0]; }
    //##ModelId=3DB9347E01B4
      int & headerSize () const { return ((int*)headref->data())[1]; }
    //##ModelId=3DB9347E03E2
      int & headerBlockSize (int n) const { return ((int*)headref->data())[2+n]; }
    //##ModelId=3DB93481001B
      void * headerData () const { return &headerBlockSize(0); }
      
  private:
    // Data Members for Class Attributes

      //##ModelId=3BB317E3002B
      TypeId mytype;

      //##ModelId=3C3D60C103DA
      int mysize_;

      //##ModelId=3BEBE89602BC
      bool selected;

      //##ModelId=3C7A2BC7030F
      bool scalar;

    // Data Members for Associations

      //##ModelId=3BEBD96601BE
      mutable vector<BlockSet> blocks;

      //##ModelId=3BEBD9780228
      mutable vector<ObjRef> objects;
    //##ModelId=3DB9346801A2
    mutable BlockRef headref;


};

//##ModelId=3DB9343B0254
typedef DataField::Ref DataFieldRef;

// throws exception if index is out of range
//##ModelId=3DB9347C00FD
inline void DataField::checkIndex ( int n ) const
{
  FailWhen( n < 0 || n >= mysize_,"index out of range");
}


// Class DataField 


//##ModelId=3C627A64008E
inline bool DataField::valid () const
{
  return mytype.id() != 0;
}

//##ModelId=3C3EC27F0227
inline TypeId DataField::objectType () const
{
  return TpDataField;
}

//##ModelId=3DB934720017
inline TypeId DataField::type () const
{
  return mytype;
}

//##ModelId=3DB9347201EE
inline int DataField::mysize () const
{
  return mysize_;
}

//##ModelId=3DB9347203B0
inline bool DataField::isSelected () const
{
  return selected;
}

//##ModelId=3DB93473019F
inline bool DataField::isScalar () const
{
  return scalar;
}


#endif


// Detached code regions:
#if 0
  return !dynamic_type;

  TypeId dum1; bool dum2;
  return get(n,dum1,dum2,check,must_write);

  return (void*)get(n,check,True);

#endif
