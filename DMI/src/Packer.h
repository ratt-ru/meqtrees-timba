//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CA2F0DC004E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CA2F0DC004E.cm

//## begin module%3CA2F0DC004E.cp preserve=no
//## end module%3CA2F0DC004E.cp

//## Module: Packer%3CA2F0DC004E; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\Packer.h

#ifndef Packer_h
#define Packer_h 1

//## begin module%3CA2F0DC004E.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3CA2F0DC004E.additionalIncludes

//## begin module%3CA2F0DC004E.includes preserve=yes
#include <set>
//## end module%3CA2F0DC004E.includes

//## begin module%3CA2F0DC004E.declarations preserve=no
//## end module%3CA2F0DC004E.declarations

//## begin module%3CA2F0DC004E.additionalDeclarations preserve=yes
//## end module%3CA2F0DC004E.additionalDeclarations


//## begin Packer%3CA2EF59021E.preface preserve=yes
//## end Packer%3CA2EF59021E.preface

//## Class: Packer%3CA2EF59021E; Parameterized Class Utility
//	Packer is a templated class providing a generic interface for
//	storing elementary objects into blocks of bytes. The default
//	templates call the pack()/unpack()/packSize() methods on the object,
//	while specializations are provided for special cases such as
//	strings.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



template <class T>
class Packer 
{
  //## begin Packer%3CA2EF59021E.initialDeclarations preserve=yes
  //## end Packer%3CA2EF59021E.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: pack%3CA2F01D003F
      //	Packs object into block. Returns the number of bytes written (which
      //	must be equal to packSize() for the same object). It is the caller's
      //	responsibility to insure sufficient space.
      static size_t pack (const T& obj, void* block, size_t &nleft);

      //## Operation: unpack%3CA2F0240180
      //	Unpacks object from a raw data block of the given size. Can throw an
      //	exception if the size is wrong or the data is invalid.
      static void unpack (T& obj, const void* block, size_t sz);

      //## Operation: construct%3CA2F59E02DA
      //	Constructs an object from a raw data block of the given size. Can
      //	throw an exception if the size is wrong or the data is invalid.
      static T construct (const void* block, size_t sz);

      //## Operation: packSize%3CA2F0B60342
      //	Returns the number of bytes required to pack() an object.
      static size_t packSize (const T& obj);

    // Additional Public Declarations
      //## begin Packer%3CA2EF59021E.public preserve=yes
      //## end Packer%3CA2EF59021E.public

  protected:
    // Additional Protected Declarations
      //## begin Packer%3CA2EF59021E.protected preserve=yes
      //## end Packer%3CA2EF59021E.protected

  private:
    // Additional Private Declarations
      //## begin Packer%3CA2EF59021E.private preserve=yes
      //## end Packer%3CA2EF59021E.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin Packer%3CA2EF59021E.implementation preserve=yes
      //## end Packer%3CA2EF59021E.implementation

};

//## begin Packer%3CA2EF59021E.postscript preserve=yes
//## end Packer%3CA2EF59021E.postscript

//## begin SeqPacker%3CA2F25D0160.preface preserve=yes
//## end SeqPacker%3CA2F25D0160.preface

//## Class: SeqPacker%3CA2F25D0160; Parameterized Class Utility
//	SeqPacker is a variation of Packer for sequential containers
//	(including set<>). The packed block includes a header (container
//	size, plus packed size of each object), followed by packed data
//	obtained by using Packer on each object in the container.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3CA2FD7A037E;Packer { -> }

template <class Seq>
class SeqPacker 
{
  //## begin SeqPacker%3CA2F25D0160.initialDeclarations preserve=yes
  //## end SeqPacker%3CA2F25D0160.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: pack%3CA2F2A9034A
      static size_t pack (const Seq& seq, void* block, size_t &nleft);

      //## Operation: unpack%3CA2F2C3006C
      static void unpack (Seq &seq, const void *block, size_t sz);

      //## Operation: packSize%3CA2F327003E
      static size_t packSize (const Seq &seq);

    // Additional Public Declarations
      //## begin SeqPacker%3CA2F25D0160.public preserve=yes
      //## end SeqPacker%3CA2F25D0160.public

  protected:
    // Additional Protected Declarations
      //## begin SeqPacker%3CA2F25D0160.protected preserve=yes
      //## end SeqPacker%3CA2F25D0160.protected

  private:
    // Additional Private Declarations
      //## begin SeqPacker%3CA2F25D0160.private preserve=yes
      //## end SeqPacker%3CA2F25D0160.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin SeqPacker%3CA2F25D0160.implementation preserve=yes
      typedef typename Seq::value_type Val;
      typedef typename Seq::iterator Iter;
      typedef typename Seq::const_iterator CIter;
      //## end SeqPacker%3CA2F25D0160.implementation
};

//## begin SeqPacker%3CA2F25D0160.postscript preserve=yes
//## end SeqPacker%3CA2F25D0160.postscript

//## begin MapPacker%3CA2F995019A.preface preserve=yes
//## end MapPacker%3CA2F995019A.preface

//## Class: MapPacker%3CA2F995019A; Parameterized Class Utility
//	MapPacker is a variation of SeqPacker for associative containers
//	(map<> etc.). The packed block includes a header (container size,
//	plus packed size of each key and value object), followed by packed
//	key/value data obtained by using Packer on each key/value pair in
//	the container.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3CA2FD7E0289;Packer { -> }

template <class Map>
class MapPacker 
{
  //## begin MapPacker%3CA2F995019A.initialDeclarations preserve=yes
  //## end MapPacker%3CA2F995019A.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: pack%3CA2F995021C
      static size_t pack (const Map& mp, void* block, size_t &nleft);

      //## Operation: unpack%3CA2F995021F
      static void unpack (Map &mp, const void *block, size_t sz);

      //## Operation: packSize%3CA2F9950229
      static size_t packSize (const Map &mp);

    // Additional Public Declarations
      //## begin MapPacker%3CA2F995019A.public preserve=yes
      //## end MapPacker%3CA2F995019A.public

  protected:
    // Additional Protected Declarations
      //## begin MapPacker%3CA2F995019A.protected preserve=yes
      //## end MapPacker%3CA2F995019A.protected

  private:
    // Additional Private Declarations
      //## begin MapPacker%3CA2F995019A.private preserve=yes
      //## end MapPacker%3CA2F995019A.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin MapPacker%3CA2F995019A.implementation preserve=yes
      typedef typename Map::key_type Key;
      typedef typename Map::value_type Val;
      typedef typename Map::iterator Iter;
      typedef typename Map::const_iterator CIter;
      //## end MapPacker%3CA2F995019A.implementation
};

//## begin MapPacker%3CA2F995019A.postscript preserve=yes
//## end MapPacker%3CA2F995019A.postscript

//## begin ArrayPacker%3CAB35D201F8.preface preserve=yes
//## end ArrayPacker%3CAB35D201F8.preface

//## Class: ArrayPacker%3CAB35D201F8; Parameterized Class Utility
//	ArrayPacker is a variation of SeqPacker for a C array of objects.
//	The packed block includes a header (array size, plus packed size of
//	each object), followed by packed data obtained by using Packer on
//	each object in the array.
//
//	The pack() and packSize() methods take an extra argument, n, giving
//	the size of the array. The unpack() method allocates and returns an
//	array.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3CAB36000385;Packer { -> }

template <class T>
class ArrayPacker 
{
  //## begin ArrayPacker%3CAB35D201F8.initialDeclarations preserve=yes
  //## end ArrayPacker%3CAB35D201F8.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: pack%3CAB35D20234
      static size_t pack (const T* arr, int n, void* block, size_t &nleft);

      //## Operation: unpack%3CAB35D2023F
      static T * unpack (const void *block, size_t sz, int& n);

      //## Operation: packSize%3CAB35D20248
      static size_t packSize (const T* arr, int n);

    // Additional Public Declarations
      //## begin ArrayPacker%3CAB35D201F8.public preserve=yes
      //## end ArrayPacker%3CAB35D201F8.public

  protected:
    // Additional Protected Declarations
      //## begin ArrayPacker%3CAB35D201F8.protected preserve=yes
      //## end ArrayPacker%3CAB35D201F8.protected

  private:
    // Additional Private Declarations
      //## begin ArrayPacker%3CAB35D201F8.private preserve=yes
      //## end ArrayPacker%3CAB35D201F8.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin ArrayPacker%3CAB35D201F8.implementation preserve=yes
      //## end ArrayPacker%3CAB35D201F8.implementation

};

//## begin ArrayPacker%3CAB35D201F8.postscript preserve=yes
//## end ArrayPacker%3CAB35D201F8.postscript

// Parameterized Class Utility Packer 

// Parameterized Class Utility SeqPacker 

// Parameterized Class Utility MapPacker 

// Parameterized Class Utility ArrayPacker 

// Parameterized Class Utility Packer 


//## Other Operations (implementation)
template <class T>
size_t Packer<T>::pack (const T& obj, void* block, size_t &nleft)
{
  //## begin Packer::pack%3CA2F01D003F.body preserve=yes
  return obj.pack(block,nleft);
  //## end Packer::pack%3CA2F01D003F.body
}

template <class T>
void Packer<T>::unpack (T& obj, const void* block, size_t sz)
{
  //## begin Packer::unpack%3CA2F0240180.body preserve=yes
  obj.unpack(block,sz);
  //## end Packer::unpack%3CA2F0240180.body
}

template <class T>
T Packer<T>::construct (const void* block, size_t sz)
{
  //## begin Packer::construct%3CA2F59E02DA.body preserve=yes
  return T(block,sz);
  //## end Packer::construct%3CA2F59E02DA.body
}

template <class T>
size_t Packer<T>::packSize (const T& obj)
{
  //## begin Packer::packSize%3CA2F0B60342.body preserve=yes
  return obj.packSize();
  //## end Packer::packSize%3CA2F0B60342.body
}

// Additional Declarations
  //## begin Packer%3CA2EF59021E.declarations preserve=yes
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
inline string Packer<string>::construct (const void* block, size_t sz)
{
  return string(static_cast<const char*>(block),sz);
}

template <>
inline size_t Packer<string>::packSize (const string& obj)
{
  return obj.length();
}

  //## end Packer%3CA2EF59021E.declarations
// Parameterized Class Utility SeqPacker 


//## Other Operations (implementation)
template <class Seq>
size_t SeqPacker<Seq>::pack (const Seq& seq, void* block, size_t &nleft)
{
  //## begin SeqPacker::pack%3CA2F2A9034A.body preserve=yes
  // A sequence is stored with the following header:
  //   1 x size_t: N - number of objects in sequence
  //   N x size_t: size of each object's data, in bytes
  // This is followed by the objects' data
  size_t *hdr = static_cast<size_t*>(block), n = *(hdr++) = seq.size();
  size_t sz = (1+n)*sizeof(size_t);
  FailWhen(sz>nleft,"block too small");
  nleft -= sz;
  char   *data = static_cast<char*>(block) + sz;
  for( CIter iter = seq.begin(); iter != seq.end(); iter++ )
  {
    size_t s1 = *(hdr++) = Packer<Val>::pack(*iter,data,nleft);
    data += s1; 
    sz += s1;
  }
  return sz;
  //## end SeqPacker::pack%3CA2F2A9034A.body
}

template <class Seq>
void SeqPacker<Seq>::unpack (Seq &seq, const void *block, size_t sz)
{
  //## begin SeqPacker::unpack%3CA2F2C3006C.body preserve=yes
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t *hdr = static_cast<size_t*>(block);
  size_t n   = *(hdr++),
         sz0 = (1+n)*sizeof(size_t);
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  for( size_t i=0; i<n; i++ )
  {
    size_t s1 = *(hdr++);
    sz0 += s1;
    FailWhen(sz<sz0,"corrupt block");
    seq.insert( seq.end(),Packer<Val>::construct(data,s1) );
    data += s1;
  }
  FailWhen(sz!=sz0,"corrupt block");
  //## end SeqPacker::unpack%3CA2F2C3006C.body
}

template <class Seq>
size_t SeqPacker<Seq>::packSize (const Seq &seq)
{
  //## begin SeqPacker::packSize%3CA2F327003E.body preserve=yes
  size_t sz = 0, count = 0; 
  for( CIter iter = seq.begin(); iter != seq.end(); iter++,count++ )
    sz += Packer<Val>::packSize(*iter);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz + (1+count)*sizeof(size_t);
  //## end SeqPacker::packSize%3CA2F327003E.body
}

// Additional Declarations
  //## begin SeqPacker%3CA2F25D0160.declarations preserve=yes
  //## end SeqPacker%3CA2F25D0160.declarations

// Parameterized Class Utility MapPacker 


//## Other Operations (implementation)
template <class Map>
size_t MapPacker<Map>::pack (const Map& mp, void* block, size_t &nleft)
{
  //## begin MapPacker::pack%3CA2F995021C.body preserve=yes
  // A map is stored with the following header:
  //   1 x size_t: N - number of entries in map
  //   N x 2 x size_t: size of each key and value's data, in bytes
  // This is followed by the key/values data
  size_t *hdr = static_cast<size_t*>(block), n = *(hdr++) = mp.size();
  size_t sz = (1+2*n)*sizeof(size_t);
  char   *data = static_cast<char*>(block) + sz;
  FailWhen(sz>nleft,"block too small");
  nleft -= sz;
  for( CIter iter = mp.begin(); iter != mp.end(); iter++ )
  {
    size_t s1 = *(hdr++) = Packer<Key>::pack(iter->first,data,nleft);
    data += s1;
    size_t s2 = *(hdr++) = Packer<Val>::pack(iter->second,data,nleft);
    data += s2; 
    sz += s1+s2;
  }
  return sz;
  //## end MapPacker::pack%3CA2F995021C.body
}

template <class Map>
void MapPacker<Map>::unpack (Map &mp, const void *block, size_t sz)
{
  //## begin MapPacker::unpack%3CA2F995021F.body preserve=yes
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t *hdr = static_cast<size_t*>(block),
                n   = *(hdr++),
                sz0 = (1+2*n)*sizeof(size_t);
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  for( size_t i=0; i<n; i++ )
  {
    size_t s1 = *(hdr++), s2 = *(hdr++);
    sz0 += s1+s2;
    FailWhen(sz<sz0,"corrupt block");
    mp[Packer<Key>::construct(data,s1)] = Packer<Val>::construct(data+s1,s2);
    data += s1+s2;
  }
  FailWhen(sz!=sz0,"corrupt block");
  //## end MapPacker::unpack%3CA2F995021F.body
}

template <class Map>
size_t MapPacker<Map>::packSize (const Map &mp)
{
  //## begin MapPacker::packSize%3CA2F9950229.body preserve=yes
  size_t sz = 0, count = 0; 
  for( CIter iter = mp.begin(); iter != mp.end(); iter++,count++ )
    sz += Packer<Key>::packSize(iter->first) +
          Packer<Val>::packSize(iter->second);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz + (1+2*count)*sizeof(size_t);
  //## end MapPacker::packSize%3CA2F9950229.body
}

// Additional Declarations
  //## begin MapPacker%3CA2F995019A.declarations preserve=yes
  //## end MapPacker%3CA2F995019A.declarations

// Parameterized Class Utility ArrayPacker 


//## Other Operations (implementation)
template <class T>
size_t ArrayPacker<T>::pack (const T* arr, int n, void* block, size_t &nleft)
{
  //## begin ArrayPacker::pack%3CAB35D20234.body preserve=yes
  // A sequence is stored with the following header:
  //   1 x size_t: N - number of objects in sequence
  //   N x size_t: size of each object's data, in bytes
  // This is followed by the objects' data
  size_t *hdr = static_cast<size_t*>(block);
  *(hdr++) = n;
  size_t sz = (1+n)*sizeof(size_t);
  FailWhen(sz>nleft,"block too small");
  nleft -= sz;
  char   *data = static_cast<char*>(block) + sz;
  for( int i=0; i<n; i++,arr++ )
  {
    size_t s1 = *(hdr++) = Packer<T>::pack(*arr,data,nleft);
    data += s1; 
    sz += s1;
  }
  return sz;
  //## end ArrayPacker::pack%3CAB35D20234.body
}

template <class T>
T * ArrayPacker<T>::unpack (const void *block, size_t sz, int& n)
{
  //## begin ArrayPacker::unpack%3CAB35D2023F.body preserve=yes
  FailWhen(sz<sizeof(size_t),"corrupt block");
  const size_t *hdr = static_cast<size_t*>(block);
  n   = (int) *(hdr++);
  size_t  sz0 = (1+n)*sizeof(size_t);
  T *arr0 = new T[n], *arr=arr0;
  FailWhen(sz<sz0,"corrupt block");
  const char *data = static_cast<const char*>(block) + sz0;
  for( int i=0; i<n; i++,arr++ )
  {
    size_t s1 = *(hdr++);
    sz0 += s1;
    FailWhen(sz<sz0,"corrupt block");
    Packer<T>::unpack(*arr,data,s1);
    data += s1;
  }
  FailWhen(sz!=sz0,"corrupt block");
  return arr0;
  //## end ArrayPacker::unpack%3CAB35D2023F.body
}

template <class T>
size_t ArrayPacker<T>::packSize (const T* arr, int n)
{
  //## begin ArrayPacker::packSize%3CAB35D20248.body preserve=yes
  size_t sz = (1+n)*sizeof(size_t); 
  for( int i=0; i<n; i++,arr++ )
    sz += Packer<T>::packSize(*arr);
  // for storage, we need 1 size_t for # of objects, N size_ts for
  // object sizes, plus the total data size
  return sz;
  //## end ArrayPacker::packSize%3CAB35D20248.body
}

// Additional Declarations
  //## begin ArrayPacker%3CAB35D201F8.declarations preserve=yes
  //## end ArrayPacker%3CAB35D201F8.declarations

//## begin module%3CA2F0DC004E.epilog preserve=yes
//## end module%3CA2F0DC004E.epilog


#endif


// Detached code regions:
#if 0
//## begin SeqPacker::insert%3CA2FE8603BF.body preserve=yes
  seq.push_back(obj);
//## end SeqPacker::insert%3CA2FE8603BF.body

#endif
