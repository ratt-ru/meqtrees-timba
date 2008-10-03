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
from Timba.utils import curry
import traceback
import sets
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
OR_GSM = "OR_GSM file";
SKA = "Jarvis SKA file";

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
                 [ NATIVE,NEWSTAR,NVSS,CLEAN,TEXT_RAD,TEXT_DMS,VIZIER,OR_GSM,SKA ],
                 namespace=self);
      self._compile_opts.append(format_opt);
      self._compile_opts.append(
        TDLOption("max_sources","Restrict to N brightest sources",
                  ["all",5,10,20],more=int,namespace=self)
      );
      self._compile_opts.append(
        TDLMenu("Make solvable source parameters",
          TDLOption("solve_subset","For which sources",["all"],more=str,
            doc="""You may give a list of source names (separated by spaces) to
            make only those particular sources solvable. For large models this 
            is probably a very good idea.""",namespace=self),
          TDLOption("solve_I","I",False,namespace=self),
          TDLOption("solve_Q","Q",False,namespace=self),
          TDLOption("solve_U","U",False,namespace=self),
          TDLOption("solve_V","V",False,namespace=self),
          TDLOption("solve_spi","spectral index",False,namespace=self),
          TDLOption("solve_pos","position",False,namespace=self),
          TDLOption("solve_RM","rotation measure",False,namespace=self),
          TDLOption("solve_shape","shape (for extended sources)",False,namespace=self),
          toggle='solvable_sources',namespace=self,
        ));
      save_opt = TDLOption("save_native","Save LSM in native format",False,namespace=self);
      self._compile_opts.append(save_opt);
      save_filename_opt = TDLOption("save_native_filename","Filename to save as",
                                     TDLFileSelect("*.lsm",exist=False),
                                     namespace=self);
      self._compile_opts.append(save_filename_opt);
      save_opt.when_changed(save_filename_opt.show);
      save_txt_opt = TDLOption("save_text","Save LSM in text (hms/dms) format",False,namespace=self);
      self._compile_opts.append(save_txt_opt);
      save_txt_filename_opt = TDLOption("save_text_filename","Filename to save as",
                                     TDLFileSelect("*.txt",exist=False),
                                     namespace=self);
      self._compile_opts.append(save_txt_filename_opt);
      save_txt_opt.when_changed(save_txt_filename_opt.show);

      def _select_format (format):
        if format == NATIVE:
          save_opt.set_value(False,save=False);
      format_opt.when_changed(_select_format);

      self._compile_opts.append(
        TDLOption("show_gui","Show LSM GUI",False,namespace=self)
      );
      self._compile_opts.append(TDLOption("export_karma","Export LSM as Karma annotations file",
                                     TDLFileSelect("*.ann",exist=False,default=None),
                                     namespace=self));
      
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
    FORMAT_READERS[OR_GSM]      = LSM.build_from_orgsm;
    FORMAT_READERS[SKA]      = LSM.build_from_ska;

    # read LSM using the selected format reader
    reader = FORMAT_READERS.get(format,None);
    if reader is None:
      raise TypeError,"Unknown LSM format '%s'"%format;

    reader(self.lsm,filename,ns);

    # save if needed
    if self.save_native and self.save_native_filename:
      self.lsm.save(self.save_native_filename);
    # save if needed
    if self.save_text and self.save_text_filename:
      self.lsm.save_as_extlist(self.save_text_filename,ns,prefix='');
      
    if self.export_karma:
      try:
        self.lsm.export_karma_annotations(self.export_karma,ns,count=self.max_sources);
      except:
        traceback.print_exc();
        pass;

    if self.show_gui:
      self.lsm.display(count=self.max_sources)

  def source_list (self,ns,max_sources=None,**kw):
    """Reads LSM and returns a list of Meow objects.
    ns is node scope in which they will be created.
    Keyword arguments may be used to indicate which of the source attributes are to be created
    as Parms, use e.g. I=Meow.Parm(tags="flux") for this.
    The use_parms option may override this.
    """;
    if self.filename is None:
      return [];
    if self.lsm is None:
      self.load(ns);

    if self.solve_subset == "all":
      solvable_source_set = None;
    else:
      solvable_source_set = sets.Set(self.solve_subset.split(" "));
      
    parm = Meow.Parm(tags="source solvable");
    # make copy of kw dict to be used for sources not in solvable set
    kw_nonsolve = dict(kw);
    # and update kw dict to be used for sources in solvable set
    if self.solvable_sources:
      if self.solve_I:
        kw.setdefault("I",parm);
      if self.solve_Q:
        kw.setdefault("Q",parm);
      if self.solve_U:
        kw.setdefault("U",parm);
      if self.solve_V:
        kw.setdefault("V",parm);
      if self.solve_spi:
        kw.setdefault("spi",parm);
      if self.solve_RM:
        kw.setdefault("RM",parm);
      if self.solve_pos:
        kw.setdefault("ra",parm);
        kw.setdefault("dec",parm);
      if self.solve_shape:
        kw.setdefault("sx",parm);
        kw.setdefault("sy",parm);
        kw.setdefault("phi",parm);

    # make Meow list
    source_model = []

  ## Note: conversion from AIPS++ componentlist Gaussians to Gaussian Nodes
  ### eX, eY : multiply by 2
  ### eP: change sign

    max_sources = max_sources or self.max_sources or 0;
    if max_sources == "all":
      max_sources = None;
    if not max_sources:
      plist = self.lsm.queryLSM(count=9999999);  # all=1 returns unsorted list, so use a large count instead
    else:
      plist = self.lsm.queryLSM(count=max_sources);
   
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
      ## if source is in solvable set (solvable_source_set of None means all are solvable),
      ## use the kw dict, else use the nonsolve dict for source parameters
      if solvable_source_set is None or pu.name in solvable_source_set:
        solvable = True;
        kwdict = kw;
      else:
        solvable = False;
        kwdict = kw_nonsolve;
      for key,value in src.iteritems():
        meowparm = kwdict.get(key);
        if isinstance(meowparm,Meow.Parm):
          src[key] = meowparm.new(value);
        elif meowparm is not None:
          src[key] = value;

      direction = Meow.Direction(ns,pu.name,src['ra'],src['dec'],static=True);

      if eX or eY or eP:
        # Gaussians
        if eY:
          size,phi = [src['sx'],src['sy']],src['phi'];
        else:
          size,phi = src['sx'],None;
        src = Meow.GaussianSource(ns,name=pu.name,
                I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
                direction=direction,
                spi=src['spi'],freq0=src['freq0'],
                size=size,phi=phi);
      else:
        src = Meow.PointSource(ns,name=pu.name,
                I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
                direction=direction,
                spi=src['spi'],freq0=src['freq0'],RM=src['RM']);
              
      src.solvable = solvable;
      source_model.append(src);
      
    return source_model


