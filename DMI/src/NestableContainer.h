//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC830067.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC830067.cm

//## begin module%3C10CC830067.cp preserve=no
//## end module%3C10CC830067.cp

//## Module: NestableContainer%3C10CC830067; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\NestableContainer.h

#ifndef NestableContainer_h
#define NestableContainer_h 1

//## begin module%3C10CC830067.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC830067.additionalIncludes

//## begin module%3C10CC830067.includes preserve=yes
//## end module%3C10CC830067.includes

// Registry
#include "Registry.h"
// HIIDSet
#include "HIIDSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC830067.declarations preserve=no
//## end module%3C10CC830067.declarations

//## begin module%3C10CC830067.additionalDeclarations preserve=yes
//## end module%3C10CC830067.additionalDeclarations


//## begin NestableContainer%3BE97CE100AF.preface preserve=yes
// The getField() and getFieldWr() macros return a [const] type * 
// to the field of a NestableCOntainer. Type match is checked.

#define getField(container,type,id)   ((container).getf<type>(id))
#define getFieldWr(container,type,id) ((container).getfwr<type>(id))
//## end NestableContainer%3BE97CE100AF.preface

//## Class: NestableContainer%3BE97CE100AF; Abstract
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFBAF8303C0;HIIDSet { -> }
//## Uses: <unnamed>%3C5A7A4400BF;UniRegistry { -> }

class NestableContainer : public BlockableObject  //## Inherits: <unnamed>%3BFCD87C0106
{
  //## begin NestableContainer%3BE97CE100AF.initialDeclarations preserve=yes
  //## end NestableContainer%3BE97CE100AF.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: get%3C56A6C50088
      //	Abstract virtual function for dereferencing a container field. Must
      //	be implemented by all child classes. fieldType() and operator [],
      //	below, are (by default) implemented in terms of this function
      //	(although they may be re-implemented in subclasses for efficiency) .
      //	Returns a pointer to the field data (0 for no such field).  Returns
      //	the type and writable property in 'tid' and 'can_write'. If must_
      //	write is True, throws exception if data is read-only. Can throw
      //	exceptions if id is malformed (i.e. contains indices that are out of
      //	range).
      virtual const void * get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid = 0, bool must_write = False) const = 0;

      //## Operation: get%3C5FA32402A9
      //	Version of get() with type and access check only. Used by the get
      //	Field() and getFieldWr() macros.
      const void * get (const HIID &id, TypeId check_tid) const;

      //## Operation: getWr%3C5FB39A027F
      void * getWr (const HIID &id, TypeId check_tid);

      //## Operation: getFieldInfo%3BE9828D0266
      //	Universal function to request all  info about a field. Returns False
      //	if no such field. By default, implemented in terms of get(), but
      //	child classes can overload it for efficiency.
      //	Set no_throw to True to disable all exceptions (and return False
      //	instead).
      //	fieldType() and hasField() are implemented in terms of this method.
      virtual bool getFieldInfo (const HIID &id, TypeId &tid, bool& can_write, bool no_throw = False) const;

      //## Operation: hasField%3C56AC2902A1
      //	Returns true if field exists, false if not. Does not throw
      //	exceptions.
      virtual bool hasField (const HIID &id) const;

      //## Operation: fieldType%3C5958C203A0
      //	Returns type of field, or 0 if no such field. Does not throw
      //	exceptions (returns 0 instead).
      virtual TypeId fieldType (const HIID &id) const;

      //## Operation: select%3BE982760231
      virtual bool select (const HIIDSet &id) = 0;

      //## Operation: clearSelection%3BFBDC0D025A
      virtual void clearSelection () = 0;

      //## Operation: selectionToBlock%3BFBDC1D028F
      virtual int selectionToBlock (BlockSet& set) = 0;

      //## Operation: isNestable%3BFCD8180044
      bool isNestable ();

      //## Operation: isNestable%3C5551E201AE
      //	Static function, checks if a type is a nestable (or a subclass
      //	thereof).
      static bool isNestable (TypeId tid);

    // Additional Public Declarations
      //## begin NestableContainer%3BE97CE100AF.public preserve=yes
//       // templated getf() and getfwr() methods provide an alternative interface
//       template<class T> const T * getf( const HIID &id ) const
//       { return (const T *) get(id,type2id(T)); }
//       
//       template<class T> T * getfwr( const HIID &id ) 
//       { return (T *) getWr(id,type2id(T)); }
      //## end NestableContainer%3BE97CE100AF.public
  protected:
    // Additional Protected Declarations
      //## begin NestableContainer%3BE97CE100AF.protected preserve=yes
      //## end NestableContainer%3BE97CE100AF.protected

  private:
    // Additional Private Declarations
      //## begin NestableContainer%3BE97CE100AF.private preserve=yes
      DeclareRegistry(NestableContainer,int,bool);
      //## end NestableContainer%3BE97CE100AF.private
  private: //## implementation
    // Additional Implementation Declarations
      //## begin NestableContainer%3BE97CE100AF.implementation preserve=yes
      //## end NestableContainer%3BE97CE100AF.implementation

};

//## begin NestableContainer%3BE97CE100AF.postscript preserve=yes
//## end NestableContainer%3BE97CE100AF.postscript

// Class NestableContainer 


//## Other Operations (inline)
inline const void * NestableContainer::get (const HIID &id, TypeId check_tid) const
{
  //## begin NestableContainer::get%3C5FA32402A9.body preserve=yes
  TypeId dum1; bool dum2;
  return get(id,dum1,dum2,check_tid,False);
  //## end NestableContainer::get%3C5FA32402A9.body
}

inline void * NestableContainer::getWr (const HIID &id, TypeId check_tid)
{
  //## begin NestableContainer::getWr%3C5FB39A027F.body preserve=yes
  TypeId dum1; bool dum2;
  return (void*)get(id,dum1,dum2,check_tid,True);
  //## end NestableContainer::getWr%3C5FB39A027F.body
}

inline bool NestableContainer::isNestable ()
{
  //## begin NestableContainer::isNestable%3BFCD8180044.body preserve=yes
  //## end NestableContainer::isNestable%3BFCD8180044.body

  return True;

}

inline bool NestableContainer::isNestable (TypeId tid)
{
  //## begin NestableContainer::isNestable%3C5551E201AE.body preserve=yes
  return registry.find(tid);
  //## end NestableContainer::isNestable%3C5551E201AE.body
}

//## begin module%3C10CC830067.epilog preserve=yes
//## end module%3C10CC830067.epilog


#endif


// Detached code regions:
#if 0
//## begin NestableContainer::operator []%3C5575480316.body preserve=yes
  TypeId dum1; bool dum2;
  return get(id,dum1,dum2,0,False);
//## end NestableContainer::operator []%3C5575480316.body

//## begin NestableContainer::operator []%3C55752601EA.body preserve=yes
  TypeId dum1; bool dum2;
  return (void*) get(id,dum1,dum2,0,True);
//## end NestableContainer::operator []%3C55752601EA.body

//## begin NestableContainer::hasField%3C56AC2902A1.body preserve=yes
  TypeId dum1; bool dum2;
  return getFieldInfo(id,dum1,dum2,True);
//## end NestableContainer::hasField%3C56AC2902A1.body

//## begin NestableContainer::fieldType%3C5958C203A0.body preserve=yes
  TypeId tid; bool dum2;
  return getFieldInfo(id,tid,dum2,True) ? tid : TypeId(0);
//## end NestableContainer::fieldType%3C5958C203A0.body

//## begin NestableContainer::getFieldInfo%3BE9828D0266.body preserve=yes
  return get(id,tid,can_write) ? True : False;
//## end NestableContainer::getFieldInfo%3BE9828D0266.body

#endif
