###  debug_methods.g: Standard object debug printing methods
###
###  Copyright (C) 2002-2003
###  ASTRON (Netherlands Foundation for Research in Astronomy)
###  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
###  This program is free software; you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation; either version 2 of the License, or
###  (at your option) any later version.
###
###  This program is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with this program; if not, write to the Free Software
###  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
###  $Id$
pragma include once

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

# define_debug_methods
#   defines a set of standard debug methods inside a Glish object
#
#   Example of use:
#
#   const classname := function (parameters,verbose=1)
#   {
#     self := [=];
#     public := [=];
#     define_debug_methods(self,public,verbose)
#
const define_debug_methods := function (ref self,ref public,initverbose=1)
{
  self.verbose := initverbose;
  
  # dprint(level,...)
  #   prints if level is <= current verbosity level
  const public.dprint := function (level,...)
  {
    wider self;
    if( level <= self.verbose )
      print spaste('[== ',self.appid,' ==] ',...);
    return T;
  }
  # dprintf(level,format,...)
  #   printfs if level is <= current verbosity level
  const public.dprintf := function (level,format,...)
  {
    wider self;
    if( level <= self.verbose )
      print spaste('[== ',self.appid,' ==] ',sprintf(format,...));
    return T;
  }
  # verbose(level)
  #   Returns the verbosity level 
  const public.verbose := function ()
  {
    wider self;
    return self.verbose;
  }
  # setverbose(level)
  #   Sets the verbosity level 
  const public.setverbose := function (level)
  {
    wider self;
    return self.verbose := level;
  }
  # private versions od dprint/dprintf also defined for convenience
  const self.dprint := ref public.dprint;
  const self.dprintf := ref public.dprintf;
  
  return T;
}

# debug_sink()
#   Defines a debug sink: an object with a controllable verbosity level,
#   and with dprint/dprintf methods.
const debug_sink := function (appid,initverbose=1)
{
  self := [appid=appid];
  public := [=];
  define_debug_methods(self,public,initverbose);
  return ref public;
}

const default_debug_sink := debug_sink('',0);
