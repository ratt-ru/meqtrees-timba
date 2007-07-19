//#  Vec.h: a container for a single object or a vector of objects
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
#ifndef DMI_Vec_h
#define DMI_Vec_h 1

#include <DMI/Container.h>
#include <DMI/ObjectAssignerMacros.h>
#include <DMI/Allocators.h>

#include <vector>

#pragma type #DMI::Vec

namespace DMI
{

class Record;
  
//##ModelId=3BB317D8010B

class Vec : public Container
{
  protected:
      // state of each object - still in block / unblocked / modified
    //##ModelId=3DB9343B0196
      typedef enum { UNINITIALIZED=0,INBLOCK=1,UNBLOCKED=2,MODIFIED=3 } ElementState;
  
      class Element 
      {
        public:
          ObjRef   ref;
          BlockSet bset;
          int      state;
          
          Element ()
          : state(UNINITIALIZED) {}
      };
      
      typedef DMI_Allocator<Element> ElementAllocator;

      typedef std::vector<Element,ElementAllocator > ElementVector; 
      
  public:
      //##ModelId=3C3D64DC016E
      Vec ();

      //##ModelId=3BFA54540099
      //##Documentation
      //## Constructs an empty data field
      // realtype is required for derived classes -- they should pass in their
      // type id here, as the array block may be filled in the constructor and
      // the virtual objectType() when called from within does not return the
      // correct type
      explicit Vec (TypeId tid, int num = -1, const void *data = 0,TypeId realtype=0);
      
      //##ModelId=3C3EE3EA022A
      Vec (const Vec &right, int flags = 0, int depth = 0,TypeId realtype=0);

    //##ModelId=3DB9346F0095
      ~Vec();

    //##ModelId=3DB9346F017B
      Vec & operator = (const Vec &right);


      //##ModelId=3C6161190193
      Vec & init (TypeId tid, int num = -1, const void *data = 0,TypeId realtype=0);

      //##ModelId=3C627A64008E
      bool valid () const;

      //##ModelId=3C62961D021B
      void resize (int newsize);

      //##ModelId=3C3EC27F0227
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const;

      //##ModelId=3C3EAB99018D
      void clear ();

      //##ModelId=3C3EB9B902DF
      bool isValid (int n = 0) const;

      //##ModelId=3C0E4619019A
      ObjRef getObj (int n = 0) const;

      //##ModelId=3C7A305F0071
      DMI_DeclareObjectAssigner(put,int);
      
      template<class T>
      const T & as (int n,Type2Type<T> =Type2Type<T>()) const
      {
        Thread::Mutex::Lock lock(mutex());
        FailWhen(type() != typeIdOf(T),"DMI::Vec type mismatch");
        FailWhen(!dynamic_type,"DMI::Vec::as<> can only be applied to dynamic objects");
        const ObjRef &ref = resolveObject(n);
        return ref.as<T>();
      }
      
      template<class T>
      T & as (int n,Type2Type<T> =Type2Type<T>()) 
      {
        Thread::Mutex::Lock lock(mutex());
        FailWhen(type() != typeIdOf(T),"DMI::Vec type mismatch");
        FailWhen(!dynamic_type,"DMI::Vec::as<> can only be applied to dynamic objects");
        ObjRef &ref = resolveObject(n);
        return ref.as<T>();
      }
      
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
      void cloneOther (const Vec &other, int flags, int depth, bool constructing,TypeId realtype);

      //##ModelId=3D05E2F301D2
      //##Documentation
      //## Abstract method. Must returns the number of elements in the
      //## container.
      virtual int size (TypeId tid = 0) const;

      //##ModelId=3C7A198A0347
      virtual int insert (const HIID &id,ContentInfo &info);

      //##ModelId=3C877E1E03BE
      //##Documentation
      //## If given a single-index HIID, removes field by #. Otherwise, if
      //## field contains a single container, calls remove(id) on that.
      virtual int remove (const HIID &id);

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
      typedef CountedRef<Vec> Ref;
      
      // standard debug info method
    //##ModelId=3DB934730394
      string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;

      // helper function for making a type[num] string
    //##ModelId=3DB9347601A8
      inline static string typeString (TypeId tid,int size) 
      { return Debug::ssprintf("%s[%d]",tid.toString().c_str(),size); };
      
      friend class Record;      
      
  protected:
      //##ModelId=3C7A19790361
      //##Documentation
      virtual int get (const HIID &id, ContentInfo &info,bool nonconst,int flags) const;

      //##ModelId=3C3D8C07027F
      ObjRef & resolveObject (int n) const;

    // Additional Protected Declarations
      // Used by various puts() to get the ObjRef at position n.
      // Inits/auto-extends field if necessary, checks types, does
      // various housekeeping.
    //##ModelId=3DB9347800CF
      ObjRef & prepareForPut (TypeId tid,int n);
      
  private:
      class HeaderBlock : public BObj::Header
      {
        public: int type;
                int size;
                uchar data[];
      };
      
      void makeNewHeader (size_t extra_size) const;
      
      void makeWritable ();
      
      const BlockRef & emptyObjectBlock () const;
    // Additional Private Declarations
      // verifies that index is in range
    //##ModelId=3DB9347C00FD
      void checkIndex ( int n ) const;
      
      // header block, maintained as a SmartBlock. Contains type and size
      // info. For built-in types, also contains the data block itself.
      // For dynamic objects, contains info on # of blocks per each object
      

    //##ModelId=3F5487DD0214
      TypeInfo typeinfo;  // type info for current field

      // for SPECIAL category types (string, HIID), this holds a vector of objects
    //##ModelId=3DB9346A0026
      void *spvec;
      // this is the address of the delete method, called to delete spvec
    //##ModelId=3F5487DD024C
      TypeInfo::DeleteMethod spdelete;
      
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
      

      //##ModelId=3F5487DD028A
      TypeId mytype;

      //##ModelId=3C3D60C103DA
      int mysize_;

      //##ModelId=3C7A2BC7030F
      bool scalar;

    //##ModelId=3DB934680272
//      mutable vector<int> objstate;
      //##ModelId=3F5487DD031B
      mutable ElementVector elems_;
      
//       typedef std::vector<BlockSet,BlockSetAllocator> BlockVector;
//       mutable BlockVector blocks;
// 
//       //##ModelId=3F5487DE0143
//       typedef std::vector<ObjRef,ObjRefAllocator> ObjectVector;
//       mutable ObjectVector objects;
      
      //##ModelId=3DB9346801A2
      // cached blockset header (+data, for binary types)
      mutable BlockRef headref_;
      mutable HeaderBlock * phead_;
      
      // "empty" header used for uninitialized fields
      mutable BlockRef emptyhdr_;
};

//##ModelId=3DB9343B0254
typedef Vec::Ref VecRef;

// throws exception if index is out of range
//##ModelId=3DB9347C00FD
inline void Vec::checkIndex ( int n ) const
{
  FailWhen( n < 0 || n >= mysize_,"index out of range");
}


// Class Vec 


//##ModelId=3C627A64008E
inline bool Vec::valid () const
{
  return mytype.id() != 0;
}

//##ModelId=3C3EC27F0227
inline TypeId Vec::objectType () const
{
  return TpDMIVec;
}

//##ModelId=3DB934720017
inline TypeId Vec::type () const
{
  return mytype;
}

//##ModelId=3DB9347201EE
inline int Vec::mysize () const
{
  return mysize_;
}

//##ModelId=3DB93473019F
inline bool Vec::isScalar () const
{
  return scalar;
}


};
#endif
