#ifndef DMI_DynamicTypeManager_h
#define DMI_DynamicTypeManager_h 1

#include <DMI/DMI.h>
#include <DMI/Registry.h>
#include <DMI/BlockSet.h>
#include <DMI/BObj.h>
#include <map>

namespace DMI
{
    
//##ModelId=3BE96C040003
//##Documentation
//## This utility class contains static functions and members for
//## run-time maintenance of maps of "virtual constructors". Virtual
//## constructors are used to convert data blocks back into Blockable
//## Objects.

class DynamicTypeManager 
{
  ImportDebugContext(DebugDMI);
  public:
    //##ModelId=3DB9343C01AB
    //##Documentation
    //## This defines a pointer to a "constructor" function for constructing
    //## a particular type of object
    typedef BObj * (*PtrConstructor)(int n);
  
    //## Reconstructs an object from a data block set, by calling the
    //## "constructor function" for that type to create an empty object, and
    //## then filling it via DMI::BObj::fromBlock().
    //## If tid is 0, then the tid will be taken from the block header.
    static ObjRef construct (TypeId tid, BlockSet& bset);
    
    //## Reconstructs N objects from a data block set, by calling the
    //## "constructor function" for that type to create an empty object, and
    //## then filling it via DMI::BObj::fromBlock().
    //## If tid is 0, then the tid will be taken from the block header.
    //## An array of objects is allocated with new [].
    static BObj * construct (TypeId tid, BlockSet& bset, int n);

    //##ModelId=3BE96C7402D5
    //##Documentation
    //## Constructs a default object of the given type (simply calls the
    //## "constructor" function from the constructor map).
    static BObj * construct (TypeId tid, int n = 0);

    //##ModelId=3BF905EE020E
    //##Documentation
    //## Checks if a type is registered
    static bool isRegistered (TypeId tid);

  private:
    // Additional Private Declarations
    //##ModelId=3DB934870196
    DeclareRegistry(DynamicTypeManager,int,PtrConstructor);
};

// Class Utility DynamicTypeManager 

};
#endif
