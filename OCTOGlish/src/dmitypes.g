### meqtypes.g: defines Glish counterpats to some DMI types
###
### Copyright (C) 2002
### ASTRON (Netherlands Foundation for Research in Astronomy)
### P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; either version 2 of the License, or
### (at your option) any later version.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
### $Id$

pragma include once

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

dmi := [=];

# this record maps supported intrinsic glish types onto their DMI type names
const dmi._supported_types := [ boolean="bool",
                                byte="uchar",
                                short="short",
                                integer="int",
                                float="float",
                                double="double",
                                complex="fcomplex",
                                dcomplex="dcomplex",
                                string="string",
                                record="DataRecord" ];

# print message and returns a fail
const dmi._fail := function (...)
{
  msg := paste(...);
  print msg;
  fail msg;
}

# tags object with the specified DMI type and basetype
#   (basetype should be one of DataField, DataRecord, DataList, or 
#   empty to use type itself)
# The type is stored as ::dmi_actual_type
# The basetype is stored as ::dmi_is_<basetype>
# When converting to C++, the conversion layer will attempt to create an
# object as specified by ::dmi_actual_type; the object will be filled 
# depending on the ::dmi_is_xxx attribute. Thus, basetype actually
# defines the conversion strategy, while type can be used to create 
# objects that are subclasses of the standard containers.
const dmi.set_type := function (ref obj,type,basetype='')
{
  obj::dmi_actual_type := type;
  if( basetype == '' )
    basetype := type;
  obj::[spaste('dmi_is_',to_lower(basetype))] := T;
}

# returns T if object is of the specified DMI type
# checks the ::dmi_is_<type> tag first, if no match, then
# compares with the ::dmi_actual_type tag
const dmi.is_type := function (obj,type)
{
  type := to_lower(type);
  return  has_field(obj::,spaste('dmi_is_',type)) ||
          ( has_field(obj::,'dmi_actual_type') &&
           to_lower(obj::dmi_actual_type) == to_lower(type) );
}

# returns DMI type of object, or '' if not a supported type
const dmi.dmi_type := function (obj)
{
  if( has_field(obj::,'dmi_actual_type') )
    return obj::dmi_actual_type;
  else if( has_field(dmi._supported_types,type_name(obj)) )
    return dmi._supported_types[type_name(obj)];
  else
    return '';
}

# makes a HIID from a string
const dmi.hiid := function (str='',...)
{
  if( num_args(...) > 0 )
    str := paste(str,...,sep='.');
  else
    str := as_string(str);
  dmi.set_type(str,'HIID');
  return str;
}

# makes a HIID list (DataField) from a string array
const dmi.hiid_list := function (strlist)
{
  if( len(strlist) )
    for( i in 1:len(strlist) )
      strlist[i] := dmi.hiid(strlist[i]);
  dmi.set_type(strlist,'DataField');
  strlist::dmi_datafield_content_type := 'HIID';
  return strlist;
}

# returns T if argument is a HIID
const dmi.is_hiid := function (obj)
{
  return dmi.is_type(obj,'HIID');
}

# creates a DMI list from its arguments
const dmi.list := function (...)
{
  list := [=];
  dmi.set_type(list,'DataList');
  return dmi.add_list(list,...);
}

# adds arguments to a DMI list
const dmi.add_list := function (ref list,...)
{
  if( !dmi.is_type(list,'DataList') )
    return dmi._fail('add_list: first argument must be a dmi.list');
  if( num_args(...) )
    for( i in 1:num_args(...) )
    {
      arg := nth_arg(i,...);
      if( dmi.dmi_type(arg) == '' )
        return dmi._fail('cannot add',type_name(arg),'to a dmi.list');
      list[spaste('#',len(list)+1)] := arg;
    }
  return ref list;
}

# merges one list into another
const dmi.merge_list := function (ref list,list2)
{
  if( !dmi.is_type(list,'DataList') || !dmi.is_type(list2,'DataList') )
    return dmi._fail('merge_list: arguments must be dmi.lists');
  if( len(list2) )
    for( i in 1:len(list2) )
      list[spaste('#',len(list)+1)] := list2[i];
  return ref list;
}

# creates a DMI field from its arguments
# arguments should be DMI types, or numerics
const dmi.field := function (...)
{
  narg := num_args(...);
  # empty field is empty record
  if( !narg )
    field := [=];
  # creating numeric field? Use array instead
  else if( is_numeric(nth_arg(1,...)) )
  {
    field := [];
    for( i in 1:narg )
    {
      arg := nth_arg(i,...);
      if( !is_numeric(arg) )
        return dmi._fail('cannot create dmi.field from mixed types: numeric and',type_name(arg));
      field := [field,arg];
    }
    field::dmi_datafield_content_type := dmi.dmi_type(field[1]);
  }
  else  # else other dmi type
  {
    arg1 := nth_arg(1,...);
    type := dmi.dmi_type(arg1);
    if( type == '' )
      return dmi._fail('cannot create dmi.field from',type_name(arg1));
    field := [=];
    for( i in 1:narg )
    {
      arg := nth_arg(i,...);
      if( dmi.dmi_type(arg) != type )
        return dmi._fail('cannot create dmi.field from mixed types: numeric and',type_name(arg));
      field[spaste('#',i)] := arg;
    }
    field::dmi_datafield_content_type := type;
  }
  dmi.set_type(field,'DataField');
  return field;
}

# aliases for backwards compatibility --
# these may be removed at some point
const is_dmi_type := dmi.is_type;
const hiid        := dmi.hiid;
const is_hiid     := dmi.is_hiid;

const dmi := dmi;

