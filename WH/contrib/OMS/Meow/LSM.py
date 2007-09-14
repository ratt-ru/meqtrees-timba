# Meow.LSM
# Meow interface to LSM files

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.LSM.LSM import LSM
import Meow

# constants for available LSM formats
# these are also used as labels in the GUI
NATIVE = "native [.lsm]";
NEWSTAR = "NEWSTAR [.mdl]";
NVSS = "NVSS file";
CLEAN = "clean components";
TEXT_RAD  = "text file (rad)";
TEXT_DMS  = "text file (hms/dms)";
VIZIER = "VizieR file";

class MeowLSM (object):
  def __init__ (self,filename=None,format=NATIVE,include_options=True,option_namespace='lsm'):
    """Initializes a MeowLSM object.
    A filename and a format may be specified, although the actual file will\
    only be loaded on demand.
    If include_options=True, immediately instantiates the options. If False, it is up to
    the caller to include the options in his menus.
    """;
    self.tdloption_namespace = option_namespace;
    self._compile_opts = [];
    self._runtime_opts = [];
    self.filename = filename;
    self.format = format;
    self.lsm = None;
    self.show_gui = False;
    # immediately include options, if needed
    if include_options:
      TDLCompileOptions(*self.compile_options());
      TDLRuntimeOptions(*self.runtime_options());
    
  def compile_options (self):
    """Returns list of compile-time options""";
    if not self._compile_opts:
      self._compile_opts.append(
        TDLOption("filename","LSM file",
                   TDLFileSelect("*.lsm *.txt *.*",default=self.filename,exist=True),
                   namespace=self)
      );
      format_opt = TDLOption("format","File format",
                 [ NATIVE,NEWSTAR,NVSS,CLEAN,TEXT_RAD,TEXT_DMS,VIZIER ],
                 namespace=self);
      self._compile_opts.append(format_opt);
      self._compile_opts.append(
        TDLOption("max_sources","Restrict to N brightest sources",
                  [5,10,20],more=int,namespace=self)
      );
      save_opt = TDLOption("save_native","Save LSM in native format",False,namespace=self);
      self._compile_opts.append(save_opt);
      save_filename_opt = TDLOption("save_native_filename","Filename to save as",
                                     TDLFileSelect("*.lsm",exist=False),
                                     namespace=self);
      self._compile_opts.append(save_filename_opt);
      save_opt.when_changed(save_filename_opt.show);

      def _select_format (format):
        if format == NATIVE:
          save_opt.set_value(False,save=False);
      format_opt.when_changed(_select_format);

      self._compile_opts.append(
        TDLOption("show_gui","Show LSM GUI",False,namespace=self)
      );
    return self._compile_opts;
    
  def runtime_options (self):
    """Makes and returns list of compile-time options""";
    # no runtime options, for now
    return self._runtime_opts;

  def load (self,ns,filename=None,format=None):
    """Loads LSM file. Filename/format arguments may be used to override those
    specified in the constructor or via options""";
    filename = filename or self.filename;
    format = format or self.format;
    
    self.lsm = LSM();
    
    # set up table of format readers
    # all are expected to take an lsm object (e.g. self) as arg 1,
    # a filename as arg2, and a node scope as arg3
    FORMAT_READERS = {};
    FORMAT_READERS[NATIVE]   = LSM.load;
    FORMAT_READERS[NEWSTAR]  = LSM.build_from_newstar;
    FORMAT_READERS[NVSS]     = LSM.build_from_catalog;
    FORMAT_READERS[CLEAN]    = LSM.build_from_complist;
    FORMAT_READERS[TEXT_RAD] = LSM.build_from_extlist_rad;
    FORMAT_READERS[TEXT_DMS] = LSM.build_from_extlist;
    FORMAT_READERS[VIZIER]   = LSM.build_from_vizier;
    
    # read LSM using the selected format reader
    reader = FORMAT_READERS.get(format,None);
    if reader is None:
      raise TypeError,"Unknown LSM format '%s'"%format;
      
    reader(self.lsm,filename,ns);
    
    # save if needed
    if self.save_native and self.save_native_filename:
      self.lsm.save(self.save_native_filename);
    
    if self.show_gui:
      self.lsm.display(count=self.max_sources)
    
  def source_list (self,ns,max_sources=None,**kw):
    """Reads LSM and returns a list of Meow objects.
    ns is node scope in which they will be created.
    Keyword arguments may be used to indicate which of the source attributes are to be created
    as Parms, use e.g. I=Meow.Parm(tags="flux") for this.
    """;
    if self.filename is None:
      return [];
    if self.lsm is None:
      self.load(ns);
      
    # make Meow list
    source_model = []
  
  ## Note: conversion from AIPS++ componentlist Gaussians to Gaussian Nodes
  ### eX, eY : multiply by 2
  ### eP: change sign
  
    plist = self.lsm.queryLSM(count=max_sources or self.max_sources);
    
    for pu in plist:
      src = {};
      ( src['ra'],src['dec'],
        src['I'],src['Q'],src['U'],src['V'],
        src['spi'],src['freq0'],src['RM']    ) = pu.getEssentialParms(ns)
      (eX,eY,eP) = pu.getExtParms()
      # scale 2 difference
      src['sx'] = eX*2
      src['sy'] = eY*2
      src['phi'] = -eP
      # override zero values with None so that Meow can make smaller trees
      if not src['spi']:
        src['spi'] = src['freq0'] = None;
      if not src['RM']:
        src['RM'] = None;
      ## construct parms or constants for source attributes
      for key,value in src.iteritems():
        meowparm = kw.get(key);
        if isinstance(meowparm,Meow.Parm):
          src[key] = meowparm.new(value);
        elif meowparm is not None:
          src[key] = value;
        
      direction = Meow.Direction(ns,pu.name,src['ra'],src['dec']);
  
      if eX or eY or eP:
        # Gaussians
        source_model.append( 
          Meow.GaussianSource(ns,name=pu.name,
              I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
              direction=direction,
              spi=src['spi'],freq0=src['freq0'],
              size=[src['sx'],src['sy']],phi=src['phi']));
      else:
        # point Sources
        source_model.append( 
          Meow.PointSource(ns,name=pu.name,
              I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
              direction=direction,
              spi=src['spi'],freq0=src['freq0'],RM=src['RM']));
  
    return source_model
    
    
    