//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC83016C.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC83016C.cm

//## begin module%3C10CC83016C.cp preserve=no
//## end module%3C10CC83016C.cp

//## Module: SmartBlock%3C10CC83016C; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\SmartBlock.h

#ifndef SmartBlock_h
#define SmartBlock_h 1

//## begin module%3C10CC83016C.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C10CC83016C.additionalIncludes

//## begin module%3C10CC83016C.includes preserve=yes
//## end module%3C10CC83016C.includes

// Debug
#include "Common/Debug.h"
// CountedRef
#include "DMI/CountedRef.h"
// CountedRefTarget
#include "DMI/CountedRefTarget.h"
//## begin module%3C10CC83016C.declarations preserve=no
//## end module%3C10CC83016C.declarations

//## begin module%3C10CC83016C.additionalDeclarations preserve=yes
//## end module%3C10CC83016C.additionalDeclarations


//## begin SmartBlock%3BEAACAB0041.preface preserve=yes
//## end SmartBlock%3BEAACAB0041.preface

//## Class: SmartBlock%3BEAACAB0041
//	SmartBlock is a block of bytes with a reference count. Optionally,
//	it can be located in shared memory
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFE634800A3;CountedRef { -> }
//## Uses: <unnamed>%3C1637E80303;Debug::Error { -> }

class SmartBlock : public CountedRefTarget  //## Inherits: <unnamed>%3C0CEB7900AC
{
  //## begin SmartBlock%3BEAACAB0041.initialDeclarations preserve=yes
  //## end SmartBlock%3BEAACAB0041.initialDeclarations

  public:
    //## Constructors (generated)
      SmartBlock();

    //## Constructors (specified)
      //## Operation: SmartBlock%3BEBD44D0103
      //	Creates a SmartBlock around an existing chunk of memory. By default,
      //	the memory will not be deleted when the SmartBlock is deleted, unless
      //	the DMI::DELETE (=DMI::ANON) flag is set.
      SmartBlock (void* data, size_t size, int flags = DMI::NO_DELETE);

      //## Operation: SmartBlock%3BFE299902D7
      //	Allocates a SmartBlock from the heap.
      explicit SmartBlock (size_t size, int flags = 0);

      //## Operation: SmartBlock%3BFA4FCA0387
      //	Creates a SmartBlock in shared memory.
      SmartBlock (size_t size, int shm_flags, int flags);

      //## Operation: SmartBlock%3BFE303F0022
      //	Cloning copy constructor. Must be called explicitly as Smart
      //	Block(other,DMI::CLONE), throws exception otherwise.
      SmartBlock (const SmartBlock &other, int flags);

    //## Destructor (generated)
      ~SmartBlock();


    //## Other Operations (specified)
      //## Operation: init%3BFE37C3022B
      //	Universal initializer. Called from various constructors.
      //	If data=0, then allocates block from heap or shared memory (if
      //	DMI::SHMEM is set in flags); will thow excpeiton if DMI::NO_DELETE
      //	or (=DMI::NON_ANON) is set.
      //	If data!=0, then uses existing block and checks for DMI::DELETE
      //	(=DMI::ANON) in flags to see if it must be deleted.
      void init (void* data, size_t size, int flags, int shm_flags);

      //## Operation: resize%3C639C340295
      //	Resizes block. Old data is copied over as much as possible. If
      //	resizing upwards and DMI::ZERO is specified, the empty space is
      //	filled with 0s.
      void resize (size_t newsize, int flags = 0);

      //## Operation: destroy%3C1E0D8D0391
      void destroy ();

      //## Operation: isShMem%3BEBBB480178
      bool isShMem () const;

      //## Operation: operator *%3BFE1E3703DD
      void * operator * ();

      //## Operation: operator *%3BFE1E4600BD
      const void * operator * () const;

      //## Operation: clone%3BFE23B501F4
      CountedRefTarget * clone (int flags = 0, int depth = 0) const;

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: block%3BEAACB9029A
      const void* data () const;

      //## Attribute: datasize%3BEAACBD0318
      size_t size () const;

      //## Attribute: shmid%3BEAACC40281
      int getShmid () const;

    // Additional Public Declarations
      //## begin SmartBlock%3BEAACAB0041.public preserve=yes
      void * data ();
      
      DefineRefTypes(SmartBlock,Ref);
      
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                              const char *name = 0 ) const;
      //## end SmartBlock%3BEAACAB0041.public
  protected:
    // Additional Protected Declarations
      //## begin SmartBlock%3BEAACAB0041.protected preserve=yes
      //## end SmartBlock%3BEAACAB0041.protected

  private:
    //## Assignment Operation (generated)
      SmartBlock & operator=(const SmartBlock &right);

    // Additional Private Declarations
      //## begin SmartBlock%3BEAACAB0041.private preserve=yes
      //## end SmartBlock%3BEAACAB0041.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin SmartBlock::block%3BEAACB9029A.attr preserve=no  public: void* {U} 
      void* block;
      //## end SmartBlock::block%3BEAACB9029A.attr

      //## begin SmartBlock::datasize%3BEAACBD0318.attr preserve=no  public: size_t {U} 
      size_t datasize;
      //## end SmartBlock::datasize%3BEAACBD0318.attr

      //## begin SmartBlock::shmid%3BEAACC40281.attr preserve=no  public: int {U} 
      int shmid;
      //## end SmartBlock::shmid%3BEAACC40281.attr

      //## Attribute: delete_block%3BFE1E930399
      //## begin SmartBlock::delete_block%3BFE1E930399.attr preserve=no  private: bool {U} 
      bool delete_block;
      //## end SmartBlock::delete_block%3BFE1E930399.attr

    // Additional Implementation Declarations
      //## begin SmartBlock%3BEAACAB0041.implementation preserve=yes
      //## end SmartBlock%3BEAACAB0041.implementation

};

//## begin SmartBlock%3BEAACAB0041.postscript preserve=yes
DefineRefTypes(SmartBlock,BlockRef);
//## end SmartBlock%3BEAACAB0041.postscript

//## begin BlockRef%3BEA7FF50154.preface preserve=yes
class SmartBlock;
//## end BlockRef%3BEA7FF50154.preface

//## Class: BlockRef%3BEA7FF50154
//	This is a reference to a SmartBlock.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C356CD402B2;CountedRef { -> }
//## Uses: <unnamed>%3C356CF10174;SmartBlock { -> }

//## begin BlockRef%3BEA7FF50154.postscript preserve=yes
//## end BlockRef%3BEA7FF50154.postscript

// Class SmartBlock 


//## Other Operations (inline)
inline bool SmartBlock::isShMem () const
{
  //## begin SmartBlock::isShMem%3BEBBB480178.body preserve=yes
  return shmid != 0;
  //## end SmartBlock::isShMem%3BEBBB480178.body
}

inline void * SmartBlock::operator * ()
{
  //## begin SmartBlock::operator *%3BFE1E3703DD.body preserve=yes
  return block;
  //## end SmartBlock::operator *%3BFE1E3703DD.body
}

inline const void * SmartBlock::operator * () const
{
  //## begin SmartBlock::operator *%3BFE1E4600BD.body preserve=yes
  return block;
  //## end SmartBlock::operator *%3BFE1E4600BD.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const void* SmartBlock::data () const
{
  //## begin SmartBlock::data%3BEAACB9029A.get preserve=no
  return block;
  //## end SmartBlock::data%3BEAACB9029A.get
}

inline size_t SmartBlock::size () const
{
  //## begin SmartBlock::size%3BEAACBD0318.get preserve=no
  return datasize;
  //## end SmartBlock::size%3BEAACBD0318.get
}

inline int SmartBlock::getShmid () const
{
  //## begin SmartBlock::getShmid%3BEAACC40281.get preserve=no
  return shmid;
  //## end SmartBlock::getShmid%3BEAACC40281.get
}

//## begin module%3C10CC83016C.epilog preserve=yes
inline void * SmartBlock::data ()
{
  return block;
}
//## end module%3C10CC83016C.epilog


#endif
