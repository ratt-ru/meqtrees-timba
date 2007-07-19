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

#ifndef DMI_ObjectAssignerMacros
#define DMI_ObjectAssignerMacros 1
    
// This macro inserts declarations for assignment of dynamic object types
// to containers. Only one "canonical" assigner form then
// actually needs to be implemented; the rest are declared as inline aliases.
//
// The canonical form of the assigner method is declared as:
//    void NAME (INDEXTYPE id,ObjRef &ref,int flags=0);
// or alternatively (if the index argument is Null):
//    void NAME (ObjRef &ref,int flags=0);
//
// This is the only assigner method that requires an implementation. Additional
// inlined assigners are automatically inserted for the following object 
// argument types:
//    const ObjRef &
//    CountedRef<T> &
//    const CountedRef<T> &
//    [const] BObj *
//    [const] BObj &
//
// The flags parameter specifies how to add objects. The following flags
// are typically used:
//    DMI::XFER:      transfers ref (default is copy). Available for non-const
//                    ref types only.
//    DMI::EXTERNAL:  attaches object as external   
//    DMI::READONLY:  attaches object as readonly (only for external objects)
//
// INDEXTYPE (the type of the index) is determined by the index argument to
// DMI_DeclareObjectAssigner. The following options are available:
//
//  index = Null:   no index at all
//  index = int:    int index
//  index = HIID:   const HIID & index
//
// More types may be added by defining additional DMI_Cont_#_Index_# macros
// (see below).
//

#define DMI_DeclareObjectAssigner(name,index) \
   void name (DMI_Cont_##index##_IndexSig ObjRef &ref,int flags=0);  \
   void name (DMI_Cont_##index##_IndexSig const ObjRef &ref,int flags=0) \
     { name(DMI_Cont_##index##_IndexCall const_cast<ObjRef&>(ref),flags&~DMI::XFER); } \
   void name (DMI_Cont_##index##_IndexSig BObj *pobj,int flags=0) \
     { ObjRef ref(pobj,flags); name(DMI_Cont_##index##_IndexCall ref,flags); } \
   void name (DMI_Cont_##index##_IndexSig const BObj *pobj,int flags=0) \
     { ObjRef ref(pobj,flags); name(DMI_Cont_##index##_IndexCall ref,flags); } \
   void name (DMI_Cont_##index##_IndexSig BObj &obj,int flags=DMI::AUTOCLONE) \
     { ObjRef ref(obj,flags); name(DMI_Cont_##index##_IndexCall ref,flags); } \
   void name (DMI_Cont_##index##_IndexSig const BObj &obj,int flags=DMI::AUTOCLONE) \
     { ObjRef ref(obj,flags); name(DMI_Cont_##index##_IndexCall ref,flags); } \
   template<class T> \
   void name (DMI_Cont_##index##_IndexSig CountedRef<T> &ref,int flags=0) \
    { name(DMI_Cont_##index##_IndexCall ref.compatible(Type2Type<BObj>()),flags); } \
   template<class T> \
   void name (DMI_Cont_##index##_IndexSig const CountedRef<T> &ref,int flags=0) \
    { name(DMI_Cont_##index##_IndexCall ref.compatible(Type2Type<BObj>()),flags); }
    
#define DMI_Cont_Null_IndexSig
#define DMI_Cont_Null_IndexCall
#define DMI_Cont_int_IndexSig   int id,
#define DMI_Cont_int_IndexCall  id,
#define DMI_Cont_HIID_IndexSig  const HIID &id,
#define DMI_Cont_HIID_IndexCall id,

#endif
