//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820124.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820124.cm

//## begin module%3C10CC820124.cp preserve=no
//## end module%3C10CC820124.cp

//## Module: DataField%3C10CC820124; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\DataField.h

#ifndef DataField_h
#define DataField_h 1

//## begin module%3C10CC820124.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820124.additionalIncludes

//## begin module%3C10CC820124.includes preserve=yes
#include "TypeInfo.h"
#include "HIID.h"
//## end module%3C10CC820124.includes

// NestableContainer
#include "NestableContainer.h"
// BlockSet
#include "BlockSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC820124.declarations preserve=no
//## end module%3C10CC820124.declarations

//## begin module%3C10CC820124.additionalDeclarations preserve=yes
#pragma type #DataField
//## end module%3C10CC820124.additionalDeclarations


//## begin DataField%3BB317D8010B.preface preserve=yes
class DataRecord;
//## end DataField%3BB317D8010B.preface

//## Class: DataField%3BB317D8010B
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BEBD95D007B;BlockSet { -> }

class DataField : public NestableContainer  //## Inherits: <unnamed>%3C7A188A02EF
{
  //## begin DataField%3BB317D8010B.initialDeclarations preserve=yes
  friend DataRecord;
  //## end DataField%3BB317D8010B.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: DataField%3C3D64DC016E
      explicit DataField (int flags = DMI::WRITE);

      //## Operation: DataField%3C3EE3EA022A
      DataField (const DataField &right, int flags = DMI::PRESERVE_RW, int depth = 0);

      //## Operation: DataField%3BFA54540099
      //	Constructs an empty data field
      explicit DataField (TypeId tid, int num = -1, int flags = DMI::WRITE, const void *data = 0);

    //## Destructor (generated)
      ~DataField();

    //## Assignment Operation (generated)
      DataField & operator=(const DataField &right);


    //## Other Operations (specified)
      //## Operation: init%3C6161190193
      DataField & init (TypeId tid, int num = -1, const void *data = 0);

      //## Operation: valid%3C627A64008E
      bool valid () const;

      //## Operation: resize%3C62961D021B
      void resize (int newsize);

      //## Operation: objectType%3C3EC27F0227
      //	Returns the class TypeId
      virtual TypeId objectType () const;

      //## Operation: clear%3C3EAB99018D
      void clear (int flags = DMI::WRITE);

      //## Operation: isValid%3C3EB9B902DF
      bool isValid (int n = 0);

      //## Operation: objwr%3C0E4619019A
      ObjRef objwr (int n = 0, int flags = DMI::PRESERVE_RW);

      //## Operation: put%3C7A305F0071
      DataField & put (int n, ObjRef &ref, int flags = DMI::XFER);

      //## Operation: objref%3C3C8D7F03D8
      ObjRef objref (int n = 0) const;

      //## Operation: fromBlock%3C3D5F2001DC
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

      //## Operation: toBlock%3C3D5F2403CC
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //## Operation: clone%3C3EC77D02B1; C++
      //	Clones a data field. (See CountedRefTarget::clone() for semantics)
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //## Operation: cloneOther%3C3EE42D0136
      void cloneOther (const DataField &other, int flags, int depth);

      //## Operation: privatize%3C3EDEBC0255
      //	Makes a private snapshot of the field, by privatizing all contents.
      //	Use DMI::WRITE to make a writable field.
      void privatize (int flags = 0, int depth = 0);

      //## Operation: get%3C7A19790361
      //	Abstract virtual function for dereferencing a container field. Must
      //	be implemented by all child classes. fieldType() and operator [],
      //	below, are (by default) implemented in terms of this function
      //	(although they may be re-implemented in subclasses for efficiency) .
      //	Returns a pointer to the field data (0 for no such field).  Returns
      //	the type and writable property in 'tid' and 'can_write'. If must_
      //	write is True, throws exception if data is read-only. Can throw
      //	exceptions if id is malformed (i.e. contains indices that are out of
      //	range).
      virtual const void * get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid = 0, int flags = 0) const;

      //## Operation: getn%3C7A1983024D
      virtual const void * getn (int n, TypeId& tid, bool& can_write, TypeId check_tid = 0, int flags = 0) const;

      //## Operation: insert%3C7A198A0347
      virtual void * insert (const HIID &id, TypeId tid, TypeId &real_tid);

      //## Operation: insertn%3C7A19930250
      virtual void * insertn (int n, TypeId tid, TypeId &real_tid);

      //## Operation: remove%3C877E1E03BE
      //	If given a single-index HIID, maps to removen(n). Otherwise, if
      //	field contains a single container, calls remove(id) on that.
      virtual bool remove (const HIID &id);

      //## Operation: removen%3C877E260301
      //	Removes object at specified index. Can only remove from the end of
      //	the array.
      virtual bool removen (int n);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: mytype%3BB317E3002B
      TypeId type () const;

      //## Attribute: mysize%3C3D60C103DA
      int size () const;

      //## Attribute: selected%3BEBE89602BC
      bool isSelected () const;

      //## Attribute: scalar%3C7A2BC7030F
      bool isScalar () const;

    // Additional Public Declarations
      //## begin DataField%3BB317D8010B.public preserve=yes
      typedef CountedRef<DataField> Ref;
      
      // standard debug info method
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

      // helper function for making a type[num] string
      inline static string typeString (TypeId tid,int size) 
      { return Debug::ssprintf("%s[%d]",tid.toString().c_str(),size); };
      
      
      //## end DataField%3BB317D8010B.public
  protected:

    //## Other Operations (specified)
      //## Operation: resolveObject%3C3D8C07027F
      ObjRef & resolveObject (int n, int flags = 0) const;

    // Additional Protected Declarations
      //## begin DataField%3BB317D8010B.protected preserve=yes
      // Used by various puts() to get the ObjRef at position n.
      // Inits/auto-extends field if necessary, checks types, does
      // various housekeeping.
      ObjRef & prepareForPut (TypeId tid,int n,int flags);
      
      // gets sub-record at position n, throws exception if field
      // does not contain a DataRecord
      const DataRecord * getSubRecord( bool write,int n=0 ) const;
      //## end DataField%3BB317D8010B.protected
  private:
    // Additional Private Declarations
      //## begin DataField%3BB317D8010B.private preserve=yes
      // verifies that index is in range
      void checkIndex ( int n ) const;
      
      // header block, maintained as a SmartBlock. Contains type and size
      // info. For built-in types, also contains the data block itself.
      // For dynamic objects, contains info on # of blocks per each object
      mutable BlockRef headref;
      
      // state of each object - still in block / unblocked / modified
      typedef enum { UNINITIALIZED=0,INBLOCK=1,UNBLOCKED=2,MODIFIED=3 } ObjectState;
      mutable vector<int> objstate;

      TypeInfo typeinfo;  // type info for current field

      // for SPECIAL category types (string, HIID), this holds a vector of objects
      void *spvec;
      // this is the address of the delete method, called to delete spvec
      TypeInfo::DeleteMethod spdelete;
      mutable bool spvec_modified; // flag: vector has been modified
      
      // flag: field contains a simple type handled by binary copying
      // (TypeInfo category NUMERIC or BINARY)
      bool    binary_type,
      // flag: field contains a dynamic type
      // (if both are clear, then it's a SPECIAL type
              dynamic_type;
      
      // inlines for accessing the header block
      int & headerType () const { return ((int*)headref->data())[0]; }
      int & headerSize () const { return ((int*)headref->data())[1]; }
      int & headerBlockSize (int n) const { return ((int*)headref->data())[2+n]; }
      void * headerData () const { return &headerBlockSize(0); }
      
      //## end DataField%3BB317D8010B.private
  private: //## implementation
    // Data Members for Class Attributes

      //## begin DataField::mytype%3BB317E3002B.attr preserve=no  public: TypeId {U} 
      TypeId mytype;
      //## end DataField::mytype%3BB317E3002B.attr

      //## begin DataField::mysize%3C3D60C103DA.attr preserve=no  public: int {U} 
      int mysize;
      //## end DataField::mysize%3C3D60C103DA.attr

      //## begin DataField::selected%3BEBE89602BC.attr preserve=no  public: bool {U} 
      bool selected;
      //## end DataField::selected%3BEBE89602BC.attr

      //## begin DataField::scalar%3C7A2BC7030F.attr preserve=no  public: bool {U} 
      bool scalar;
      //## end DataField::scalar%3C7A2BC7030F.attr

    // Data Members for Associations

      //## Association: DOMIN0::<unnamed>%3BEBD9640021
      //## Role: DataField::blocks%3BEBD96601BE
      //## begin DataField::blocks%3BEBD96601BE.role preserve=no  private: BlockSet {0..* -> 0..*VHgN}
      mutable vector<BlockSet> blocks;
      //## end DataField::blocks%3BEBD96601BE.role

      //## Association: DOMIN0::<unnamed>%3BEBD97703D5
      //## Role: DataField::objects%3BEBD9780228
      //## begin DataField::objects%3BEBD9780228.role preserve=no  private: BlockableObject {0..* -> 0..*RHN}
      mutable vector<ObjRef> objects;
      //## end DataField::objects%3BEBD9780228.role

    // Additional Implementation Declarations
      //## begin DataField%3BB317D8010B.implementation preserve=yes
      //## end DataField%3BB317D8010B.implementation

};

//## begin DataField%3BB317D8010B.postscript preserve=yes
typedef DataField::Ref DataFieldRef;

// throws exception if index is out of range
inline void DataField::checkIndex ( int n ) const
{
  FailWhen( n < 0 || n >= mysize,"index out of range");
}

//## end DataField%3BB317D8010B.postscript

// Class DataField 


//## Other Operations (inline)
inline bool DataField::valid () const
{
  //## begin DataField::valid%3C627A64008E.body preserve=yes
  return mytype.id() != 0;
  //## end DataField::valid%3C627A64008E.body
}

inline TypeId DataField::objectType () const
{
  //## begin DataField::objectType%3C3EC27F0227.body preserve=yes
  return TpDataField;
  //## end DataField::objectType%3C3EC27F0227.body
}

//## Get and Set Operations for Class Attributes (inline)

inline TypeId DataField::type () const
{
  //## begin DataField::type%3BB317E3002B.get preserve=no
  return mytype;
  //## end DataField::type%3BB317E3002B.get
}

inline int DataField::size () const
{
  //## begin DataField::size%3C3D60C103DA.get preserve=no
  return mysize;
  //## end DataField::size%3C3D60C103DA.get
}

inline bool DataField::isSelected () const
{
  //## begin DataField::isSelected%3BEBE89602BC.get preserve=no
  return selected;
  //## end DataField::isSelected%3BEBE89602BC.get
}

inline bool DataField::isScalar () const
{
  //## begin DataField::isScalar%3C7A2BC7030F.get preserve=no
  return scalar;
  //## end DataField::isScalar%3C7A2BC7030F.get
}

//## begin module%3C10CC820124.epilog preserve=yes
//## end module%3C10CC820124.epilog


#endif


// Detached code regions:
#if 0
//## begin DataField::isContiguous%3C7F9826016F.body preserve=yes
  return !dynamic_type;
//## end DataField::isContiguous%3C7F9826016F.body

//## begin DataField::get%3C56B1DA0057.body preserve=yes
  TypeId dum1; bool dum2;
  return get(n,dum1,dum2,check,must_write);
//## end DataField::get%3C56B1DA0057.body

//## begin DataField::getWr%3BFCFA2902FB.body preserve=yes
  return (void*)get(n,check,True);
//## end DataField::getWr%3BFCFA2902FB.body

#endif
