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

#ifndef DMI_Packer_h
#define DMI_Packer_h 1

#include <DMI/DMI.h>
#include <DMI/TypeId.h>
#include <DMI/TypeIterMacros.h>
#include <set>

namespace DMI
{

//##ModelId=3CA2EF59021E
//##Documentation
//## Packer is a templated class providing a generic interface for
//## storing elementary objects into blocks of bytes. The default
//## templates call the pack()/unpack()/packSize() methods on the object,
//## while specializations are provided for special cases such as
//## strings.
template <class T>
class Packer 
{
  ImportDebugContext(DebugDMI);
  
  public:

      //##ModelId=3CA2F01D003F
      //##Documentation
      //## Packs object into block. Returns the number of bytes written (which
      //## must be equal to packSize() for the same object). It is the caller's
      //## responsibility to insure sufficient space.
      static size_t pack (const T& obj, void* block, size_t &nleft);

      //##ModelId=3CA2F0240180
      //##Documentation
      //## Unpacks object from a raw data block of the given size. Can throw an
      //## exception if the size is wrong or the data is invalid.
      static void unpack (T& obj, const void* block, size_t sz);

      //##ModelId=3CA2F0B60342
      //##Documentation
      //## Returns the number of bytes required to pack() an object.
      static size_t packSize (const T& obj);

      //##ModelId=3DB934E3035F
      //##Documentation
      //## If this returns a >0 size, this indicates that the object is binary
      //## (i.e. may be safely copied via memcpy and/or assignment). A binary
      //## object may omit implementation of all other methods.
      static size_t binary ();

};

//##ModelId=3CA2F25D0160
//##Documentation
//## SeqPacker is a variation of Packer for sequential containers
//## (including set<>). The packed block includes a header (container
//## size, plus packed size of each object), followed by packed data
//## obtained by using Packer on each object in the container.

template <class Seq, class ElemPacker = Packer<typename Seq::value_type> >
class SeqPacker 
{
  ImportDebugContext(DebugDMI);
  public:

      //##ModelId=3CA2F2A9034A
      static size_t pack (const Seq& seq, void* block, size_t &nleft);

      //##ModelId=3CA2F2C3006C
      static void unpack (Seq &seq, const void *block, size_t sz);

      //##ModelId=3CA2F327003E
      static size_t packSize (const Seq &seq);

      //##ModelId=3DB934E400C0
      static size_t binary ();

  private:
    // Additional Implementation Declarations
    //##ModelId=3DB9343E0190
      typedef typename Seq::value_type Val;
    //##ModelId=3DB9343E01B8
      typedef typename Seq::iterator Iter;
    //##ModelId=3DB9343E01EA
      typedef typename Seq::const_iterator CIter;
};

//##ModelId=3CA2F995019A
//##Documentation
//## MapPacker is a variation of SeqPacker for associative containers
//## (map<> etc.). The packed block includes a header (container size,
//## plus packed size of each key and value object), followed by packed
//## key/value data obtained by using Packer on each key/value pair in
//## the container.

template <class Map, class KeyPacker = Packer<typename Map::key_type> , class ValuePacker = Packer<typename Map::value_type> >
class MapPacker 
{
  ImportDebugContext(DebugDMI);
  public:

      //##ModelId=3CA2F995021C
      static size_t pack (const Map& mp, void* block, size_t &nleft);

      //##ModelId=3CA2F995021F
      static void unpack (Map &mp, const void *block, size_t sz);

      //##ModelId=3CA2F9950229
      static size_t packSize (const Map &mp);

      //##ModelId=3DB9348E02D6
      static size_t binary ();

  private:
    // Additional Implementation Declarations
    //##ModelId=3DB9343D01DF
      typedef typename Map::key_type Key;
    //##ModelId=3DB9343D01FD
      typedef typename Map::value_type Val;
    //##ModelId=3DB9343D022F
      typedef typename Map::iterator Iter;
    //##ModelId=3DB9343D0257
      typedef typename Map::const_iterator CIter;
};

//##ModelId=3CAB35D201F8
//##Documentation
//## ArrayPacker is a variation of SeqPacker for a C array of objects.
//## The packed block includes a header (array size, plus packed size of
//## each object), followed by packed data obtained by using Packer on
//## each object in the array.
//## 
//## The pack() and packSize() methods take an extra argument, n, giving
//## the size of the array. The unpack() method allocates and returns an
//## array.

template <class T, class ElemPacker = Packer<T> >
class ArrayPacker 
{
  ImportDebugContext(DebugDMI);
  public:

      //##ModelId=3CAB35D20234
      static size_t pack (const T* arr, int n, void* block, size_t &nleft);

      //##ModelId=3CAB35D2023F
      static void unpack (T* arr, int n, const void *block, size_t sz);

      //##ModelId=3CAB35D20248
      static size_t packSize (const T* arr, int n);

      //##ModelId=3DB9344000E1
      static T* allocate (const void *block, size_t sz, int& n);

};

//##ModelId=3DB9343903AF
//##Documentation
//## BinArrayPacker is a version of Packer for fixed-size arrays of
//## fixed-size binary types supporting bitwise copy. This includes
//## built-in types and binary structs.

template <class T, int num = 1>
class BinArrayPacker 
{
  ImportDebugContext(DebugDMI);
  public:

      //##ModelId=3DB9344602C0
      //##Documentation
      //## Packs object into block. Returns the number of bytes written (which
      //## must be equal to packSize() for the same object). It is the caller's
      //## responsibility to insure sufficient space.
      static size_t pack (const T *obj, void* block, size_t &nleft);

      //##ModelId=3DB9344602CC
      //##Documentation
      //## Unpacks object from a raw data block of the given size. Can throw an
      //## exception if the size is wrong or the data is invalid.
      static void unpack (T *obj, const void* block, size_t sz);

      //##ModelId=3DB9344602D7
      //##Documentation
      //## Returns the number of bytes required to pack() an object.
      static size_t packSize (const T*  = 0);

      //##ModelId=3DB9344602DF
      //##Documentation
      //## If this returns a >0 size, this indicates that the object is binary
      //## (i.e. may be safely copied via memcpy and/or assignment). A binary
      //## object may omit implementation of all other methods.
      static size_t binary ();

};

//##ModelId=3DB9343A0018
//##Documentation
//## BinPacker is a version of Packer for fixed-size binary types
//## supporting bitwise copy (and the =) operator. This includes
//## built-in types and binary structs.
//## 
//## The Packer_DefineBinPacker(Type,Args) macro defines the
//## specialization Packer<Type> as BinPacker<Type>. The Args argument is
//## ignored, and is only there for compatibility with TypeIterMacros.h

template <class T>
class BinPacker 
{
  ImportDebugContext(DebugDMI);
  public:

      //##ModelId=3DB9344602F2
      //##Documentation
      //## Packs object into block. Returns the number of bytes written (which
      //## must be equal to packSize() for the same object). It is the caller's
      //## responsibility to insure sufficient space.
      static size_t pack (const T &obj, void* block, size_t &nleft);

      //##ModelId=3DB9344602FF
      //##Documentation
      //## Unpacks object from a raw data block of the given size. Can throw an
      //## exception if the size is wrong or the data is invalid.
      static void unpack (T &obj, const void* block, size_t sz);

      //##ModelId=3DB934460311
      //##Documentation
      //## Returns the number of bytes required to pack() an object.
      static size_t packSize (const T &);

      //##ModelId=3DB93446031B
      //##Documentation
      //## If this returns a >0 size, this indicates that the object is binary
      //## (i.e. may be safely copied via memcpy and/or assignment). A binary
      //## object may omit implementation of all other methods.
      static size_t binary ();

};

// Parameterized Class Utility Packer 


//##ModelId=3CA2F01D003F
template <class T>
inline size_t Packer<T>::pack (const T& obj, void* block, size_t &nleft)
{
  return obj.pack(block,nleft);
}

//##ModelId=3CA2F0240180
template <class T>
inline void Packer<T>::unpack (T& obj, const void* block, size_t sz)
{
  obj.unpack(block,sz);
}

//##ModelId=3CA2F0B60342
template <class T>
inline size_t Packer<T>::packSize (const T& obj)
{
  return obj.packSize();
}

//##ModelId=3DB934E3035F
template <class T>
inline size_t Packer<T>::binary ()
{
  return 0;
}

// Parameterized Class Utility SeqPacker 

// Parameterized Class Utility MapPacker 

// Parameterized Class Utility ArrayPacker 

// Parameterized Class Utility BinArrayPacker 


//##ModelId=3DB9344602C0
template <class T, int num>
inline size_t BinArrayPacker<T,num>::pack (const T *obj, void* block, size_t &nleft)
{
  FailWhen(nleft<sizeof(T)*num,"block too small");
  memcpy(block,obj,sizeof(T)*num);
  nleft -= sizeof(T)*num;
  return sizeof(T)*num;
}

//##ModelId=3DB9344602CC
template <class T, int num>
inline void BinArrayPacker<T,num>::unpack (T *obj, const void* block, size_t sz)
{
  FailWhen(sz!=sizeof(T)*num,"corrupt block");
  memcpy(obj,block,sizeof(T)*num);
}

//##ModelId=3DB9344602D7
template <class T, int num>
inline size_t BinArrayPacker<T,num>::packSize (const T* )
{
  return sizeof(T)*num;
}

//##ModelId=3DB9344602DF
template <class T, int num>
inline size_t BinArrayPacker<T,num>::binary ()
{
  return sizeof(T)*num;
}

// Parameterized Class Utility BinPacker 


//##ModelId=3DB9344602F2
template <class T>
inline size_t BinPacker<T>::pack (const T &obj, void* block, size_t &nleft)
{
  FailWhen(nleft<sizeof(T),"block too small");
  memcpy(block,&obj,sizeof(T));
  nleft -= sizeof(T);
  return sizeof(T);
}

//##ModelId=3DB9344602FF
template <class T>
inline void BinPacker<T>::unpack (T &obj, const void* block, size_t sz)
{
  FailWhen(sz!=sizeof(T),"corrupt block");
  memcpy(&obj,block,sizeof(T));
}

//##ModelId=3DB934460311
template <class T>
inline size_t BinPacker<T>::packSize (const T &)
{
  return sizeof(T);
}

//##ModelId=3DB93446031B
template <class T>
inline size_t BinPacker<T>::binary ()
{
  return sizeof(T);
}

// Parameterized Class Utility Packer 

template <>
inline size_t Packer<string>::pack (const string& obj, void* block,size_t &nleft)
{
  FailWhen(nleft < obj.length(),"block too small");
  nleft -= obj.length();
  return obj.copy(static_cast<char*>(block),string::npos);
}

template <>
inline void Packer<string>::unpack (string& obj, const void* block, size_t sz)
{
  obj.assign(static_cast<const char*>(block),sz);
}

template <>
inline size_t Packer<string>::packSize (const string& obj)
{
  return obj.length();
}

// Parameterized Class Utility SeqPacker 


//##ModelId=3CA2F2A9034A
template <class Seq, class ElemPacker>
size_t SeqPacker<Seq,ElemPacker>::pack (const Seq& seq, void* block, size_t &nleft)
{
  // A sequence is stored with the following header:
  //   1 x size_t: N - number of objects in sequence
  //   N x size_t: size of each object's data, in bytes (unless binary)
  // This is followed by the objects' data
  size_t *hdr = static_cast<size_t*>(block), n = *(hdr++) = seq.size();
  size_t sz = ( 1 + (ElemPacker::binary()?0:n) )*sizeof(size_t);
  FailWhen(sz>nleft,"block too small");
  nleft -= sz;
  char   *data = static_cast<char*>(block) + sz;
  for( CIter iter = seq.begin(); iter != seq.end(); iter++ )
  {
    size_t s1 = ElemPacker::binary();
    if( s1 )
    {
      FailWhen(s1>nleft,"block too small");
      memcpy(data,&(*iter),s1);
      nleft -= s1;
    }
    else
      s1 = *(hdr++) = ElemPacker::pack(*iter,data,nleft);
    data += s1; 
    sz += s1;
  }
  return sz;
}

//##ModelId=3CA2F2C3006C
template <class Seq, class ElemPacker>
void SeqPacker<Seq,ElemPacker>::unpack (Seq &seq, const void *block, size_t sz)
{
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t *hdr = static_cast<const size_t*>(block);
  size_t n   = *(hdr++),
         sz0 = (1+(ElemPacker::binary()?0:n))*sizeof(size_t);
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  seq.clear();
  seq.reserve(n);
  for( size_t i=0; i<n; i++ )
  {
    size_t s1 = ElemPacker::binary();
    seq.push_back(Val());
    Val & val = seq.back();
    if( s1 )
    {
      sz0 += s1;
      FailWhen(sz<sz0,"corrupt block");
      memcpy(&val,data,s1);
    }
    else
    {
      sz0 += s1 = ElemPacker::binary() ? ElemPacker::binary() : *hdr++;
      FailWhen(sz<sz0,"corrupt block");
      ElemPacker::unpack(val,data,s1);
    }
    data += s1;
  }
  FailWhen(sz!=sz0,"corrupt block");
}

//##ModelId=3CA2F327003E
template <class Seq, class ElemPacker>
size_t SeqPacker<Seq,ElemPacker>::packSize (const Seq &seq)
{
  if( ElemPacker::binary() )
    return sizeof(size_t) + ElemPacker::binary()*seq.size();
  size_t sz = 0, count = 0; 
  for( CIter iter = seq.begin(); iter != seq.end(); iter++,count++ )
    sz += ElemPacker::packSize(*iter);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz + (1+count)*sizeof(size_t);
}

//##ModelId=3DB934E400C0
template <class Seq, class ElemPacker>
size_t SeqPacker<Seq,ElemPacker>::binary ()
{
  return 0;
}

// Parameterized Class Utility MapPacker 


//##ModelId=3CA2F995021C
template <class Map, class KeyPacker, class ValuePacker>
size_t MapPacker<Map,KeyPacker,ValuePacker>::pack (const Map& mp, void* block, size_t &nleft)
{
  // A map is stored with the following header:
  //   1 x size_t: N - number of entries in map
  //   N x 2 x size_t: size of each key and value's data, in bytes (unless binary)
  // This is followed by the key/values data
  size_t *hdr = static_cast<size_t*>(block), n = *(hdr++) = mp.size();
  size_t sz = (1+ (KeyPacker::binary()?0:n) + (ValuePacker::binary()?0:n))*sizeof(size_t);
  char   *data = static_cast<char*>(block) + sz;
  FailWhen(sz>nleft,"block too small");
  nleft -= sz;
  for( CIter iter = mp.begin(); iter != mp.end(); iter++ )
  {
    size_t s1 = KeyPacker::binary(), s2 = ValuePacker::binary();
    if( s1 )
    {
      FailWhen(s1>nleft,"block too small");
      memcpy(data,&(iter->first),s1);
      nleft -= s1;
    }
    else
      s1 = *(hdr++) = KeyPacker::pack(iter->first,data,nleft);
    data += s1;
    if( s2 )
    {
      FailWhen(s2>nleft,"block too small");
      memcpy(data,&(iter->second),s2);
      nleft -= s2;
    }
    else
      s2 = *(hdr++) = ValuePacker::pack(iter->second,data,nleft);
    data += s2; 
    sz += s1+s2;
  }
  return sz;
}

//##ModelId=3CA2F995021F
template <class Map, class KeyPacker, class ValuePacker>
void MapPacker<Map,KeyPacker,ValuePacker>::unpack (Map &mp, const void *block, size_t sz)
{
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t 
    *hdr = static_cast<size_t*>(block),
    n   = *(hdr++),
    sz0 = (1+ (KeyPacker::binary()?0:n) + (ValuePacker::binary()?0:n))*sizeof(size_t);
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  for( size_t i=0; i<n; i++ )
  {
    size_t s1 = KeyPacker::binary(), s2 = ValuePacker::binary();
    Key key;
    if( s1 )
    {
      sz0 += s1;
      FailWhen(sz<sz0,"corrupt block");
      memcpy(&key,data,s1);
    }
    else
    {
      s1 = *(hdr++);
      sz0 += s1;
      FailWhen(sz<sz0,"corrupt block");
      KeyPacker::unpack(key,data,s1);
    }
    data += s1;
    if( s2 )
    {
      sz0 += s2;
      FailWhen(sz<sz0,"corrupt block");
      memcpy(&(mp[key]),data,s2);
    }
    else
    {
      s2 = *(hdr++);
      sz0 += s1;
      FailWhen(sz<sz0,"corrupt block");
      ValuePacker::unpack(mp[key],data,s2);
    }
    data += s2;
  }
  FailWhen(sz!=sz0,"corrupt block");
}

//##ModelId=3CA2F9950229
template <class Map, class KeyPacker, class ValuePacker>
size_t MapPacker<Map,KeyPacker,ValuePacker>::packSize (const Map &mp)
{
  size_t sz = 0, count = 0;
  for( CIter iter = mp.begin(); iter != mp.end(); iter++,count++ )
    sz += KeyPacker::binary() ? KeyPacker::binary() : KeyPacker::packSize(iter->first) 
       +  ValuePacker::binary() ? ValuePacker::binary() : ValuePacker::packSize(iter->second);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz +  (1+ (KeyPacker::binary()?0:count) + (ValuePacker::binary()?0:count))*sizeof(size_t);
}

//##ModelId=3DB9348E02D6
template <class Map, class KeyPacker, class ValuePacker>
size_t MapPacker<Map,KeyPacker,ValuePacker>::binary ()
{
  return 0;
}

// Parameterized Class Utility ArrayPacker 


//##ModelId=3CAB35D20234
template <class T, class ElemPacker>
size_t ArrayPacker<T,ElemPacker>::pack (const T* arr, int n, void* block, size_t &nleft)
{
  // An array is stored with the following header:
  //   1 x size_t: N - number of objects in array
  //   N x size_t: size of each object's data, in bytes (unless binary)
  // This is followed by the objects' data:
  size_t elsize = ElemPacker::binary();
  const size_t nnn    = elsize ? 0 : n;  
  size_t sz = (1+ nnn)*sizeof(size_t);
  FailWhen(sz>nleft,"block too small");
  size_t *hdr = static_cast<size_t*>(block);
  *(hdr++) = n;
  nleft -= sz;
  char   *data = static_cast<char*>(block) + sz;
  if( elsize ) // binary (fixed) elements
  {
    elsize *= n;
    FailWhen(nleft<elsize,"block too small");
    memcpy(data,arr,elsize);
    nleft -= elsize; sz += elsize;
  }
  else // variable-length elements
  {
    for( int i=0; i<n; i++,arr++ )
    {
      size_t s1 = *(hdr++) = ElemPacker::pack(*arr,data,nleft);
      data += s1; 
      sz += s1;
    }
  }
  return sz;
}

//##ModelId=3CAB35D2023F
template <class T, class ElemPacker>
void ArrayPacker<T,ElemPacker>::unpack (T* arr, int n, const void *block, size_t sz)
{
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t *hdr = static_cast<const size_t*>(block);
  int n0   = (int) *(hdr++);
  FailWhen(n!=n0,"incorrect number of elements in array block");
  size_t  elsize = ElemPacker::binary();
  size_t  nnn    = (elsize?0:n);
  size_t  sz0 = (1+ nnn)*sizeof(size_t);
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  if( elsize ) // binary (fixed) elements
  {
    sz0 += elsize *= n;
    FailWhen(sz<sz0,"corrupt block");
    memcpy(arr,block,elsize);
  }
  else // variable-length elements
  {
    for( int i=0; i<n; i++,arr++ )
    {
      size_t s1 = *(hdr++);
      sz0 += s1;
      FailWhen(sz<sz0,"corrupt block");
      ElemPacker::unpack(*arr,data,s1);
      data += s1;
    }
  }
  FailWhen(sz!=sz0,"corrupt block");
}

//##ModelId=3CAB35D20248
template <class T, class ElemPacker>
size_t ArrayPacker<T,ElemPacker>::packSize (const T* arr, int n)
{
  if( ElemPacker::binary() ) // fixed length elements
    return sizeof(size_t) + n*ElemPacker::binary();
  size_t sz = (1+n)*sizeof(size_t); 
  for( int i=0; i<n; i++,arr++ )
    sz += ElemPacker::packSize(*arr);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz;
}

//##ModelId=3DB9344000E1
template <class T, class ElemPacker>
T* ArrayPacker<T,ElemPacker>::allocate (const void *block, size_t sz, int& n)
{
  FailWhen(sz<sizeof(size_t),"corrupt block");
  n = (int) *static_cast<const size_t*>(block);
  T *ptr = new T[n];
  try {
    unpack(ptr,n,block,sz);
  } catch( std::exception &exc ) {
    delete [] ptr;
    throw(exc);
  }
  return ptr;
}

// Parameterized Class Utility BinArrayPacker 

// Parameterized Class Utility BinPacker 

// provide specializations of Packer for built-ins
#define DefineBinPacker(Type,arg) template<> class Packer<Type> : public BinPacker<Type> {};
DoForAllNumericTypes(DefineBinPacker,)
#undef DefineBinPacker

// provide specializations of Packer for common containers
template<class T>
class Packer<vector<T> > : public SeqPacker<vector<T> > 
{};

template<class Key,class Val>
class Packer<map<Key,Val> > : public MapPacker<map<Key,Val> > 
{};

};
#endif
