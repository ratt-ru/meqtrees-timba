from Timba.TDL import *
from Timba.Meq import meq

import re
import traceback
import sys
import os
import os.path
import Meow
import Meow.Utils
import sets

try:
  import pycasatable
except:
  pycasatable = None;
  
# queue size parameter for MS i/o record
ms_queue_size = 500;
  
class MSContentSelector (object):
  def __init__ (self,ddid=[0],field=None,channels=True,namespace='ms_sel'):
    """Creates options for selecting a subset of an MS.
    ddid:       list of suggested DDIDs, or false for no selector. 
    field:      list of suggested fields. or false for no selector.
      NB: if pycasatable is available, ddid/field is ignored, and selectors are always
      provided, based on the MS content.
    namespace:  the TDLOption namespace name, used to qualify TDL options created here.
        If making multiple selectors, you must give them different namespace names
    """;
    self.tdloption_namespace = namespace;
    self._opts = [];
    self.ddid_index = self.field_index = None;
    self.ms_spws = self.ms_field_names = self.ms_ddid_numchannels = None;
    # field/ddid selectors
    more_ids = int;
    if pycasatable:
      ddid = [0];
      field = [0];
      more_ids = None;  # no more= option to ddid/field: they come from the MS
    if ddid:
      self.ddid_option = TDLOption('ddid_index',"Data description ID",
        ddid,more=more_ids,namespace=self,
        doc="""If the MS contains multiple spectral windows, etc., then use this option to select different DATA_DESCRIPTION_IDs. Default is 0.""");
      self._opts.append(self.ddid_option);
    if field:
      self.field_option = TDLOption('field_index',"Field ID",field,
        more=more_ids,namespace=self,
        doc="""If the MS contains multiple fields, then use this option to select different FIELD_IDs. Default is 0.""");
      self._opts.append(self.field_option);
    # channel selector
    if channels:
      self.channel_options = [
        TDLOption('ms_channel_start',"First channel",[0],more=int,namespace=self),
        TDLOption('ms_channel_end',"Last channel",[0],more=int,namespace=self),
        TDLOption('ms_channel_step',"Channel stepping",[1,2],more=int,namespace=self)
      ];
      chanmenu = TDLMenu("Channel selection",
                         toggle='select_channels',namespace=self,
                         *self.channel_options);
      self._opts.append(chanmenu);
    else:
      self.select_channels = False;
    # additional taql string
    self.taql_option = TDLOption('ms_taql_str',"Additional TaQL selection",
                                [None],more=str,namespace=self)
    self._opts.append(self.taql_option);
    # if pycasatable exists, set up interactivity for ddid/channels
    if pycasatable:
      if channels:
        self.channel_options[0].set_validator(self._validate_first_channel);
        self.channel_options[1].set_validator(self._validate_last_channel);
        self.channel_options[2].set_validator(self._validate_channel_step);
      self.ddid_option.when_changed(self._select_ddid);
        
  def option_list (self):
    """Returns list of all TDL options"""
    return self._opts;
  
  def get_channels (self):
    """Returns start,end,step tuple for selected channels, or None
    if we were created without a channel selector""";
    if self.select_channels:
      return self.ms_channel_start,self.ms_channel_end,self.ms_channel_step;
    else:
      return None;
    
  def get_spectral_window (self):
    """Returns the spw corresponding to the selected DDID. If pycasatable is n/a,
    simply returns the ddid_index (kludgy kludgy)
    """;
    ddid = self.ddid_index or 0;
    if self.ms_spws:
      return self.ms_spws[ddid];
    else:
      return ddid;
    
  def get_field (self):
    """Returns the field number""";
    return self.field_index or 0;
  
  def create_selection_record (self):
    """Forms up a selection record that can be added to an MS input record""";
    selection = record();
    if self.select_channels:
      selection.channel_start_index = self.ms_channel_start;
      selection.channel_end_index = self.ms_channel_end;
      selection.channel_increment = self.ms_channel_step;
    if self.ddid_index is not None:
      selection.ddid_index = self.ddid_index;
    if self.field_index is not None:
      selection.field_index = self.field_index;
    if self.ms_taql_str:
      selection.selection_string = ms_taql_str; 
    return selection;

  def _select_new_ms (self,ms):
    """Called (from MSSelector) when a new MS is selected. ms is a pycasatable.table
    object. Fills ddid/field/channel selectors from the MS. 
    """;
    # DDIDs
    self.ms_spws = list(pycasatable.table(ms.getkeyword('DATA_DESCRIPTION')) \
                              .getcol('SPECTRAL_WINDOW_ID'));
    numchans = pycasatable.table(ms.getkeyword('SPECTRAL_WINDOW')).getcol('NUM_CHAN');
    self.ms_ddid_numchannels = [ numchans[spw] for spw in self.ms_spws ];
    # Fields
    self.ms_field_names = list(pycasatable.table(ms.getkeyword('FIELD')).getcol('NAME'));
    # update selectors
    self._update_ms_options();
  
  def _update_ms_options (self):
    # DDID selector
    if self.ms_ddid_numchannels is not None:
      self.ddid_option.set_option_list(range(len(self.ms_ddid_numchannels)));
      if len(self.ms_ddid_numchannels) < 2:
        self.ddid_option.hide();
    # Field selector
    if self.ms_field_names is not None:
      field_list = [ "%d:%s"%x for x in enumerate(self.ms_field_names) ];
      self.field_option.set_option_list(dict(enumerate(field_list)));
      if len(self.ms_field_names) < 2:
        self.field_option.hide();
      
  def _update_from_other (self,other):
    self.ms_spws = other.ms_spws;
    self.ms_ddid_numchannels = other.ms_ddid_numchannels;
    self.ms_field_names = other.ms_field_names;
    self._update_ms_options();
  
  def _select_ddid (self,value):
    """callback used when a new DDID is selected."""
    if self.ms_ddid_numchannels:
      nchan = self.ms_ddid_numchannels[value];
      self.channel_options[0].set_option_list([0,nchan-1]);
      self.channel_options[0].set_value(min(self.ms_channel_start,nchan-1),save=False);
      self.channel_options[0].set_doc("(max %d) select first channel"%(nchan-1));
      self.channel_options[1].set_option_list([0,nchan-1]);
      self.channel_options[1].set_value(min(self.ms_channel_end,nchan-1),save=False);
      self.channel_options[1].set_doc("(max %d) select last channel"%(nchan-1));
      self.channel_options[2].set_value(min(self.ms_channel_step,nchan),save=False);
      self.channel_options[2].set_doc("(max %d) select channel steping"%nchan);
  
  def _validate_first_channel (self,value):
    """validator for channel selectors."""
    return isinstance(value,int) and \
          value >= 0 and \
          value < self.ms_ddid_numchannels[self.ddid_index] and \
          value < self.channel_options[1].value;
  
  def _validate_last_channel (self,value):
    """validator for channel selectors."""
    return isinstance(value,int) and \
          value >= self.channel_options[0].value and \
          value < self.ms_ddid_numchannels[self.ddid_index];
  
  def _validate_channel_step (self,value):
    """validator for channel selectors."""
    return isinstance(value,int) and \
          value >= 1 and \
          value <= self.ms_ddid_numchannels[self.ddid_index];

class MSSelector (object):
  """An MSSelector implements TDL options for selecting an MS and a subset therein""";
  def __init__ (self,
                filter="*.ms *.MS",
                has_input=True,
                has_output=True,
                forbid_output=["DATA"],
                antsel=True,
                tile_sizes=[1,5,10,20,30,60],
                ddid=[0],
                field=None,
                channels=True,
                flags=False,
                namespace='ms_sel'
                ):
    """Creates an MSSelector object
    filter:     ms name filter. Default is "*.ms *.MS"
    has_input:  is an input column selector initially enabled.
    has_input:  is an output column selector initially enabled.
    forbid_output: a list of forbidden output columns. "DATA" by default.
    antsel:     if True, an antenna subset selector will be provided
    tile_sizes: list of suggested tile sizes. If false, no tile size selector is provided.
    ddid:       list of suggested DDIDs, or false for no selector. 
    field:      list of suggested fields. or false for no selector.
      NB: if pycasatable is available, ddid/field is ignored, and selectors are always
      provided, based on the MS content.
    channels:   if True, channel selection will be provided
    flags:      if True, a "write flags" option will be provided
    namespace:  the TDLOption namespace name, used to qualify TDL options created here.
        If making multiple selectors, you must give them different namespace names.
    """;
    self.tdloption_namespace = namespace;
    self._content_selectors = [];
    self.ms_antenna_names = [];
    self.ms_antenna_sel = self.antsel_option = None;
    ms_option = TDLOption('msname',"MS",TDLDirSelect(filter),namespace=self);
    self._compile_opts = [ ms_option ];
    self._opts = [];
    # antenna selector
    if antsel:
      if isinstance(antsel,str):
        antsel = [None,antsel];
      elif isinstance(antsel,(tuple,list)):
        antsel = [None]+antsel;
      else:
        antsel = [None];
      self.antsel_option = TDLOption("ms_antenna_sel","Antenna subset",
                                     [None],more=str,namespace=self,
        doc="""Selects a subset of antennas to use. You can specify individual indices (1-based) 
        separated by commas or spaces, or ranges, e.g. "M:N" (M to N inclusive), or ":M" (1 to M),
        or "N:" (N to last). Example subset: ":3 5 8 10:12 16:"."""
      );
      self.antsel_option.set_validator(self._antenna_sel_validator);
      # hide until an MS is selected
      if pycasatable:
        self.antsel_option.hide();
      self._compile_opts.append(self.antsel_option);
    # input/output column options
    self.ms_data_columns = ["DATA","MODEL_DATA","CORRECTED_DATA"];
    if isinstance(forbid_output,str):
      self._forbid_output = sets.Set([forbid_output]);
    elif forbid_output:
      self._forbid_output = sets.Set(forbid_output);
    else:
      self._forbid_output = [];
    self.input_column = self.output_column = None;
    self.ms_has_input = has_input;
    self.ms_has_output = has_output;
    # if no access to tables, then allow more input columns to be entered
    if pycasatable:
      more_col = None;
    else:
      more_col = str;
    self.input_col_option = TDLOption('input_column',"Input MS column",
                                      self.ms_data_columns,
                                      namespace=self,more=more_col);
    self.input_col_option.show(has_input);
    self._opts.append(self.input_col_option);
    self.output_col_option = TDLOption('output_column',"Output MS column",
                                      self.ms_data_columns + [None],
                                      namespace=self,more=str,default=2);
    self.output_col_option.show(has_output);
    self._opts.append(self.output_col_option);
    # tile sizes
    if tile_sizes:
      self._opts.append(TDLOption('tile_size',"Tile size (timeslots)",
                                  tile_sizes,more=int,namespace=self));
    else:
      self.tile_size = 1;
    if flags:
      self._opts.append(TDLOption('ms_write_flags',"Write flags to output",
                                  False,namespace=self));
    else:
      self.ms_write_flags = False;
    # add a default content selector
    self._ddid,self._field,self._channels = ddid,field,channels;
    self.subset_selector = self.make_subset_selector(namespace);
    self._opts += self.subset_selector.option_list();
    # if pycasatable exists, set up interactivity for MS options
    if pycasatable:
      ms_option.set_validator(self._select_new_ms);
  
  def enable_input_column (self,enable=True):
    self.ms_has_input = enable;
    self.input_col_option.show(enable);
    
  def enable_output_column (self,enable=True):
    self.ms_has_output = enable;
    self.output_col_option.show(enable);
  
  def option_list (self):
    """Returns list of all TDL options. Note that the MS name is always
    the first option."""
    return self._compile_opts + self._opts;
  
  def compile_options (self):
    """Returns MS name option."""
    return self._compile_opts;
  
  def runtime_options (self):
    """Returns list of all TDL options. Note that the MS name is always
    the first option."""
    return self._opts;
  
  def get_antenna_names (self):
    """Returns the list of antenna names from the current MS. If pycasatable
    is not available, this will be empty""";
    if self.ms_antenna_sel:
      return self._parse_antenna_subset(self.ms_antenna_sel);
    else:
      return self.ms_antenna_names;
  
  def get_antenna_set (self,default=None):
    """Returns the set of selected antenna indices from the current MS, or None
    if no selection info is available."""
    if self.ms_antenna_sel:
      return self._parse_antenna_subset(self.ms_antenna_sel);
    elif self.ms_antenna_names:
      return range(1,len(self.ms_antenna_names)+1);
    else:
      return default;
  
  def make_subset_selector (self,namespace):
    """Makes an MSContentSelector object connected to this MS selector."""
    sel = MSContentSelector(ddid=self._ddid,field=self._field,
                            channels=self._channels,namespace=namespace);
    # extra selectors needs to be initialized with existing info
    if pycasatable and self._content_selectors:
      sel._update_from_other(self.subset_selector);
      sel._select_ddid(self.subset_selector.ddid_index or 0);
    self._content_selectors.append(sel);
    return sel;
    
  def _select_new_ms (self,msname):
    """This callback is called whenever a new MS is selected. Returns False if
    table is misformed""";
    # do nothing if already read this MS
    if msname == getattr(self,'_msname',None):
      return True;
    try:
      ms = pycasatable.table(msname);
      # data columns
      self.ms_data_columns = [ name for name in ms.colnames() if name.endswith('DATA') ];
      self.input_col_option.set_option_list(self.ms_data_columns);
      outcols = [ col for col in self.ms_data_columns if col not in self._forbid_output ];
      self.output_col_option.set_option_list(outcols);
      # antennas
      self.ms_antenna_names = pycasatable.table(ms.getkeyword('ANTENNA')).getcol('NAME');
      if self.antsel_option:
        self.antsel_option.set_option_list(["1:%d"%len(self.ms_antenna_names)]);
        self.antsel_option.show();
      # notify content selectors
      for sel in self._content_selectors:
        sel._select_new_ms(ms);
      self._msname = msname;
      return True;
    except:
      print "error reading MS",msname;
      traceback.print_exc();
      return False;
  
  def _parse_antenna_subset (self,value):
    if not value:
      return None;
    if self.ms_antenna_names:
      nant = len(self.ms_antenna_names);
    else:
      nant = 1;     # unreasonably large...
    subset = [];
    for spec in re.split("[\s,]+",value):
      if spec:
        # single number
        match = re.match("^\d+$",spec);
        if match:
          index = int(spec);
          # if antennas not known, accept any index
          if not self.ms_antenna_names:
            nant = max(nant,index);
          if index < 1 or index > nant:
            raise ValueError,"illegal antenna specifier '%s'"%spec;
          subset.append(index);
          continue;
        # [number]:[number]
        match = re.match("^(\d+)?:(\d+)?$",spec);
        if not match:
          raise ValueError,"illegal antenna specifier '%s'"%spec;
        index1 = 1;
        index2 = nant;
        if match.group(1):
          index1 = int(match.group(1));
        if match.group(2):
          index2 = int(match.group(2));
        if not self.ms_antenna_names:
          nant = max(nant,index1,index2);
        if index1<1 or index2<1 or index1>nant or index2>nant or index1>index2:
          raise ValueError,"illegal antenna specifier '%s'"%spec;
        # add to subset
        subset += range(index1,index2+1);
    return subset;
        
  def _antenna_sel_validator (self,value):
    try:
      antenna_subset = self._parse_antenna_subset(value);
      return True;
    except:
      print "error parsing antenna selection '%s'"%value;
      traceback.print_exc();
      return False;
  
  def imaging_selector (self,*args,**kw):
    """Makes an ImagingSelector connected to this MS selector. All arguments
    are passed to the ImagingSelector constructor""";
    return ImagingSelector(self,*args,**kw);
    
  def create_inputrec (self,tiling=None):
    """Creates an input record with the selected options""";
    if self.msname is None:
      raise ValueError,"Measurement Set not specified";
    rec = record();
    rec.ms_name          = self.msname
    if self.input_column:
      rec.data_column_name = self.input_column;
    tiling = tiling or self.tile_size;
    if isinstance(tiling,(list,tuple)):
      if len(tiling) != 2:
        raise TypeError,"tiling: 2-list or 2-tuple expected";
      (tile_segments,tile_size) = tiling;
      if tile_segments is not None:
        rec.tile_segments    = tile_segments;
      if tile_size is not None:
        rec.tile_size        = tile_size;
    else: 
      rec.tile_size = tiling;
    rec.selection = self.subset_selector.create_selection_record();
    # form top-level record
    iorec = record(ms=rec);
    iorec.python_init = 'Meow.ReadVisHeader';
    iorec.mt_queue_size = ms_queue_size;
    return iorec;
  
  def create_outputrec (self):
    """Creates an output record with the selected options""";
    rec = record();
    rec.write_flags = self.ms_write_flags;
    if self.output_column:
      rec.data_column = self.output_column;
    return record(ms=rec,mt_queue_size=ms_queue_size);
      
  def create_io_request (self,tiling=None):
    """Creates an i/o record with the selected options, suitable for
    passing to a VisDataMux""";
    req = meq.request();
    req.input = self.create_inputrec(tiling);
    if self.ms_write_flags or self.output_column is not None:
      req.output = self.create_outputrec();
    return req;
  
  def run_solve_job (self,mqs,solvables,tiling=None,
                     solver_node="solver",vdm_node="VisDataMux",options=None,
                     wait=False):
    """helper method to run a solution with a bunch of solvables""";
    # set solvables list in solver
    solver_defaults = Meow.Utils.create_solver_defaults(solvables,options=options)
    mqs.setnodestate(mqs,solver_node,solver_defaults,sync=True,wait=wait)
    req = self.create_io_request(tiling);
    mqs.execute(vdm_node,req,wait=wait);
  

class ImagingSelector (object):
  """ImagingSelector provides a set of TDL options for imaging""";
  def __init__ (self,mssel,npix=256,arcmin=5,cellsize=None,subset=True,namespace='img_sel'):
    """Creates an ImagingSelector.
    mssel: an MSSelector object
    npix:       default image size in pixels (or list of suggested sizes)
    arcmin:     default image size in arc minutes (or list of suggested sizes)
    cellsize:   default cell size (as an aips++ quantity string), or list. Note 
                that either arcmin or cellsize should be specified, not both.
    subset:     if True, a separate MSContentSelector will be provided, allowing
                to image a different subset of the MS.
    namespace:  the TDLOption namespace name, used to qualify TDL options created here.
        If making multiple selectors, you must give them different namespace names.
    """;
    self.tdloption_namespace = namespace;
    self.mssel = mssel;
    # add imaging column option
    self.img_col_option = TDLOption('imaging_column',"MS column to image",
                          mssel.ms_data_columns,more=str,namespace=self);
    mssel.output_col_option.when_changed(curry(self.img_col_option.set_value,save=False));
    self._opts = [ self.img_col_option ];
    self._opts += [
      TDLOption('imaging_mode',"Imaging mode",
                ["mfs","channel"],namespace=self),
      TDLOption('imaging_weight',"Imaging weights",
                ["natural","uniform","briggs"],namespace=self),
      TDLOption('imaging_stokes',"Stokes parameters to image",
                ["I","IQUV"],namespace=self) 
    ];
    if npix:
      if not isinstance(npix,(list,tuple)):
        npix = [ npix ];
      self._opts.append(TDLOption('imaging_npix',
                        "Image size, in pixels",npix,more=int,namespace=self));
    self.imaging_arcmin = self.imaging_cellsize = None;
    if arcmin:
      if cellsize:
        raise ValueError,"ImagingSelector: specify either 'arcmin' or 'cellsize', not both";
      if not isinstance(arcmin,(list,tuple)):
        arcmin = [ arcmin ];
      self._opts.append(TDLOption('imaging_arcmin',
                    "Image size, in arcmin",arcmin,more=float,namespace=self));
    elif cellsize:
      if not isinstance(cellsize,(list,tuple)):
        cellsize = [ cellsize ];
      self._opts.append(TDLOption('imaging_cellsize',
                        "Pixel size",cellsize,more=str,namespace=self));
    # add MS subset selector, if needed
    if subset:
      self.subset_selector = mssel.make_subset_selector(namespace);
      custom_sel_menu = TDLMenu("Use custom MS selection for imaging",
                          toggle="imaging_custom_ms_select",namespace=self,
                          *self.subset_selector.option_list());
      self._opts.append(custom_sel_menu);
    else:
      self.subset_selector = mssel.subset_selector;
    # add TDL job to make an image
    def job_make_image (mqs,parent,**kw):
      self.make_dirty_image();
    self._opts.append(TDLJob(job_make_image,"Make a dirty image"));

  def option_list (self):
    """Returns list of all TDL options"""
    return self._opts;
  
  def make_dirty_image (self,npix=None,cellsize=None,arcmin=None):
    """Runs glish script to make an image.
    The following parameters, if supplied, will override the option settings:
      npix:       image size in pixels 
      arcmin:     image size in arc minutes
      cellsize:   default cell size (as an aips++ quantity string). Note 
                  that either arcmin or cellsize may be specified, not both.
    """;
    # choose selector based on custom MS select option
    if self.imaging_custom_ms_select:
      selector = self.subset_selector;
    else:
      selector = self.mssel.subset_selector;
    # check MS name and column
    if not self.mssel.msname:
      raise ValueError,"make_dirty_image: MS not set up";
    col = self.imaging_column;
    if not col:
      raise ValueError,"make_dirty_image: output column not set up";
    # image size
    npix = npix or self.imaging_npix;
    # see if arcmin or cellsize is supplied; if neither, then use TDLOption values
    if arcmin or cellsize:
      if arcmin and cellsize:
          raise ValueError,"ImagingSelector: specify either 'arcmin' or 'cellsize', not both";
    else:
      arcmin = self.imaging_arcmin;
      cellsize = self.imaging_cellsize;
    # resolve to required cellsize, finally
    if arcmin is not None:
      cellsize = str(float(arcmin*60)/npix)+"arcsec";
    # form up initial argument list to run imaging script
    script_name = os.path.join(Meow._meow_path,'make_dirty_image.g');
    script_name = os.path.realpath(script_name);  # glish don't like symlinks...
    args = [ 'glish','-l',
      script_name,
      col,
      'ms='+self.mssel.msname,
      'mode='+self.imaging_mode,
      'weight='+self.imaging_weight,
      'stokes='+self.imaging_stokes,
      'npix=%d'%npix,
      'cellsize='+cellsize,
      'spwid=%d'%(selector.get_spectral_window()+1),
      'field=%d'%(selector.get_field()+1),
    ];
    # add channel arguments
    chans = selector.get_channels();
    if chans:
      nchan = chans[1]-chans[0]+1;
      chanstart = chans[0]+1;
      if len(chans) > 2:
        chanstep = chans[2];
      else:
        chanstep = 1;
      args += [ 'chanmode=channel',
                'nchan='+str(nchan),
                'chanstart='+str(chanstart),
                'chanstep='+str(chanstep) ];
    else:
      args.append("chanmode=none");
    # run script
    print "imaging args",args;
    os.spawnvp(os.P_NOWAIT,'glish',args);
