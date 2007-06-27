 # standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
from Meow import StdTrees


def _modname (obj):
  if hasattr(obj,'name'):
    return obj.name;
  elif hasattr(obj,'__name__'):
    return obj.__name__;
  else:
    return obj.__class__.__name__;

class MeqMaker (object):
  def __init__ (self,namespace='me'):
    self.tdloption_namespace = namespace;
    self._uv_jones_list = [];
    self._sky_jones_list = [];
    self._compile_options = [];
    self._runtime_options = [];
    self._sky_models = None;
    
  def compile_options (self):
    return self._compile_options;
  
  def runtime_options (self):
    return self._runtime_options;
    
  def add_sky_models (self,modules):
    if self._sky_models:
      raise RuntimeError,"add_sky_models() may only be called once";
    self._compile_options.append(
        self._module_selector("Sky model","sky",modules,use_toggle=False));
    self._sky_models = modules;

  def add_uv_jones (self,label,name,modules,pointing=None):
    return self._add_jones_modules(label,name,True,pointing,modules);

  def add_sky_jones (self,label,name,modules,pointing=None):
    return self._add_jones_modules(label,name,False,pointing,modules);

  def _add_jones_modules (self,label,name,is_uvplane,pointing,modules):
    if not modules:
      raise RuntimeError,"No modules specified for %s Jones"%label;
    if not isinstance(modules,(list,tuple)):
      modules = [ modules ];
    # extra options for pointing
    if pointing:
      if not isinstance(pointing,(list,tuple)):
        pointing = [ pointing ];
      pointing_menu = [ self._module_selector("Apply pointing errors to %s"%label,
                                              label+"pe",pointing,nonexclusive=True) ];
    else:
      pointing_menu = [];
    # make option menus for selecting a jones module
    mainmenu = self._module_selector("Use %s Jones (%s)"%(label,name),
                                     label,modules,extra_opts=pointing_menu);
    self._compile_options.append(mainmenu);
    # add to internal list
    if is_uvplane:
      self._uv_jones_list.append((label,name,modules,None));
    else:
      self._sky_jones_list.append((label,name,modules,pointing));
        
  def _module_selector (self,menutext,label,modules,extra_opts=[],use_toggle=True,**kw):
    # for each module, we either take the options returned by module.compile_options(),
    # or pass in the module itself to let the menu "suck in" its options
    def modopts (mod):
      modopts = getattr(mod,'compile_options',None);
      if callable(modopts):
        return list(modopts());
      else:
        return [mod];
    toggle = self._make_attr(label,"enable");
    exclusive = self._make_attr(label,"module");
    if not use_toggle:
      setattr(self,toggle,True);
      toggle = None;
    if len(modules) == 1:
      modname = _modname(modules[0]);
      mainmenu = TDLMenu(menutext,toggle=toggle,namespace=self,name=modname,
                         *(modopts(modules[0])+list(extra_opts)),**kw);
      setattr(self,exclusive,modname);
    else:
      # note that toggle name is not really used, since we make an exclusive
      # parent menu
      submenus = [ TDLMenu("Use '%s' module"%_modname(mod),name=_modname(mod),
                            toggle='_enable_module',namespace=self,
                            *modopts(mod)) 
                    for mod in modules ];
      mainmenu = TDLMenu(menutext,toggle=toggle,exclusive=exclusive,namespace=self,
                          *(submenus+list(extra_opts)),**kw);
    return mainmenu;
  
  def _make_attr (*comps):
    """Forms up the name of an 'enabled' attribute for a given module group (e.g. a Jones term)"""
    return "_".join(comps);
  _make_attr = staticmethod(_make_attr);
  
  def is_group_enabled (self,label):
    """Returns true if the given module is enabled for the given Jones label"""
    return getattr(self,self._make_attr(label,"enable"));

  def get_inspectors (self):
    """Returns list of inspector nodes created by this MeqMaker""";
    return self._inspectors or None;
  
  def _get_selected_module (self,label,modules):
    # check global toggle for this module group
    if self.is_group_enabled(label):
      # figure out which module we'll be using. If only one is available, use it regardless.
      if len(modules) == 1:
        return modules[0];
      else:
        selname = getattr(self,self._make_attr(label,"module"));
        for mod in modules:
          if _modname(mod) == selname:
            return mod;
    return None;
        
  def estimate_image_size (self):
    module = self._get_selected_module('sky',self._sky_models);
    if module:
      estimate = getattr(module,'estimate_image_size',None);
      if callable(estimate):
        return estimate();
    return None;

  def make_tree (self,ns,sources=None,stations=None):
    self._inspectors = [];
    stations = stations or Meow.Context.array.stations();
    # use sky model if no source list is supplied
    if not sources:
      module = self._get_selected_module('sky',self._sky_models);
      if not module:
        raise RuntimeError,"No source list supplied and no sky model set up";
      sources = module.source_list(ns);
      print [src.name for src in sources];
    
    # corrupt_sources will be replaced with a new source list every time
    # a Jones term is applied
    corrupt_sources = sources;
    
    # now apply all Jones terms
    for label,name,modules,pointing_modules in self._sky_jones_list:
      module = self._get_selected_module(label,modules);
      if not module:
        continue;
      # see if this module has pointing offsets enabled
      dlm = None;
      if pointing_modules:
        pointing_module = self._get_selected_module(label+"pe",pointing_modules);
        # get pointing offsets
        if pointing_module:
          dlm = ns[label]('dlm');
          inspectors = [];
          dlm = pointing_module.compute_pointings(dlm,stations=stations,
                                                  inspectors=inspectors);
          if inspectors:
            self._inspectors += inspectors;
          elif dlm:
            self._inspectors.append(
                ns.inspector(label)('dlm') << StdTrees.define_inspector(dlm,stations));
      
      # now make the appropriate matrices
      # note that Jones terms are computed using the original source list.
      # this is to keep the extra corruption qualifiers from creeping into
      # their names
      Jj = ns[label];
      inspectors = [];
      Jj = module.compute_jones(Jj,sources=sources,stations=stations,
                                pointing_offsets=dlm,
                                inspectors=inspectors);
      # if module does not make its own inspectors, add automatic ones
      if inspectors:
        self._inspectors += inspectors;
      elif Jj:
        self._inspectors.append(
            ns.inspector(label) << StdTrees.define_inspector(Jj,sources,stations));
      # corrupt all sources with the Jones for their direction
      if Jj:
        corrupt_sources = [ src.corrupt(Jj(src0.name)) 
                            for src,src0 in zip(corrupt_sources,sources) ];
    
    # now form up patch
    allsky = Meow.Patch(ns,'sky',Meow.Context.observation.phase_centre);
    allsky.add(*corrupt_sources);
  
    # add uv-plane effects
    for label,name,modules,dum in self._uv_jones_list:
      module = self._get_selected_module(label,modules);
      if not module:
        continue;
      # now make the appropriate matrices
      Jj = ns[label];
      inspectors = [];
      Jj = module.compute_jones(Jj,stations=stations,inspectors=inspectors);
      # if module does not make its own inspectors, add automatic ones
      if inspectors:
        self._inspectors += inspectors;
      elif Jj:
        self._inspectors.append(
            ns.inspector(label) << StdTrees.define_inspector(Jj,stations));
      # corrupt patch with Jones term
      if Jj:
        allsky = allsky.corrupt(Jj);
    
    # add bookmarks for inspectors
    for node in self._inspectors:
      name = node.name.replace('_',' ');
      Meow.Bookmarks.Page(name).add(node,viewer="Collections Plotter");
  
    # return predicted visibilities
    return allsky.visibilities();
