import numpy
import Timba.dmi
import re
import tempfile
import os

from Meow import MSUtils

# figure out which table implementation to use -- try pyrap/casacore first
try:
  import pyrap_tables
  TABLE = pyrap_tables.table
  print "Calico flagger: using the pyrap_tables module"
except:
  # else try the old pycasatable/aips++ thing
  try:
    import pycasatable
    TABLE = pycasatable.table
    print "Calico flagger: using the pycasatable module. WARNING: this is deprecated."
    print "Please install pyrap and casacore!"
  except:
    TABLE = None;
    print "Calico flagger: no tables module found"
    print "Please install pyrap and casacore!"
    
_gli = MSUtils.find_exec('glish');
if _gli:
  _GLISH = 'glish';
  print "Calico flagger: found %s, autoflag should be available"%_gli;
else:
  _GLISH = None;
  print "Calico flagger: glish not found, autoflag will not be available";

_addbitflagcol = MSUtils.find_exec('addbitflagcol');

# Various argument-formatting methods to use with the Flagger.AutoFlagger class
# below. These really should be static methods of the class, but that doesn't work
# with Python (specifically, I cannot include them into static member dicts)
def _format_nbins (bins,argname):
  if isinstance(bins,(list,tuple)) and len(bins) == 2:
    return str(list(bins));
  else:
    return "%d"%bins;
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,bins);
  
def _format_bool (arg,argname):
  if arg: return "T";
  else:   return "F";

def _format_index (arg,argname):
  if isinstance(arg,int):
    if arg<0:
      return str(arg);
    else:
      return str(arg+1);
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);

def _format_list (arg,argname):
  if isinstance(arg,str):
    return "'%s'"%arg;
  elif isinstance(arg,(list,tuple)):
    return "[%s]"%(','.join([_format_list(x,argname) for x in arg]));
  elif isinstance(arg,bool):
    return _format_bool(arg,argname);
  elif isinstance(arg,(int,float)):
    return str(arg);
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);

def _format_ilist (arg,argname):
  if isinstance(arg,str):
    return "'%s'"%arg;
  elif isinstance(arg,(list,tuple)):
    return "[%s]"%(','.join([_format_list(x,argname) for x in arg]));
  elif isinstance(arg,bool):
    return _format_bool(arg,argname);
  elif isinstance(arg,int):
    return _format_index(arg,argname);
  elif isinstance(arg,float):
    return str(arg);
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);

def _format_plotchan (arg,argname):
  if isinstance(arg,bool):
    return _format_bool(arg,argname);
  else:
    return _format_index(arg,argname);
  
def _format_2N (arg,argname):
  if isinstance(arg,(list,tuple)):
    return "%s"%arg;
  elif Timba.dmi.is_array(arg):
    if arg.dtype == Timba.array.int32:
      a = arg + 1;
    else:
      a = arg;
    if a.ndim == 1:
      return str(list(a));
    elif a.ndim == 2 and a.shape[1] == 2:
      return "[%s]"%(','.join([ str(list(a[i,:])) for i in range(a.shape[0]) ]));
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);

def _format_clip (arg,argname):
  if isinstance(arg,(list,tuple)):
    if not isinstance(arg[0],(list,tuple)):
      arg = [ arg ];
    recfields = [];
    for i,triplet in enumerate(arg):
      if not isinstance(triplet,(list,tuple)) or len(triplet) != 3:
        raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);
      expr,minval,maxval = triplet;
      subfields = [ "expr='%s'"%expr ];
      if minval is not None:
        subfields.append("min=%g"%minval);
      if maxval is not None:
        subfields.append("max=%g"%maxval);
      recfields.append("a%d=[%s]"%(i,','.join(subfields)));
    return "[%s]"%','.join(recfields);
  raise TypeError,"invalid value for '%s' keyword (%s)"%(argname,arg);
    
class Flagger (Timba.dmi.verbosity):
  def __init__ (self,msname,verbose=0,chunksize=200000):
    Timba.dmi.verbosity.__init__(self,name="Flagger");
    self.set_verbose(verbose);
    if not TABLE:
      raise RuntimeError,"No tables module found. Please install pyrap and casacore";
    self.msname = msname;
    self.ms = None;
    self.chunksize = chunksize;
    self._reopen();
    
  def close (self):
    if self.ms:
      self.dprint(2,"closing MS",self.msname);
      self.ms.close();
    self.ms = self.flagsets = None;
    
  def _reopen (self):
    if self.ms is None:
      self.ms = ms = TABLE(self.msname,readonly=False);
      self.dprintf(1,"opened MS %s, %d rows\n",ms.name(),ms.nrows());
      self.has_bitflags = 'BITFLAG' in ms.colnames();
      self.flagsets = MSUtils.get_flagsets(ms);
      self.dprintf(1,"flagsets are %s\n",self.flagsets.names());
    return self.ms;
    
  def add_bitflags (self,wait=True):
    if not self.has_bitflags:
      global _addbitflagcol; 
      if not _addbitflagcol:
        raise RuntimeError,"cannot find addbitflagcol utility in $PATH";
      self.close();
      self.dprintf(1,"running addbitflagcol\n");
      if os.spawnvp(os.P_WAIT,_addbitflagcol,['addbitflagcol',self.msname]):
        raise RuntimeError,"addbitflagcol failed";
      
  def remove_flagset (self,*fsnames):
    self._reopen();
    mask = self.flagsets.remove_flagset(*fsnames);
    self.unflag(mask);

  def unflag (self,unflag=-1,*args,**kw):
    return self.flag(flag=0,unflag=unflag,*args,**kw);
  
  def transfer (self,flag=1,replace=False,*args,**kw):
    unflag = (replace and flag) or 0;
    return self.flag(flag=flag,unflag=unflag,transfer=True,*args,**kw);
  
  def get_stats(self,flag=0,legacy=False,**kw):
    stats = self.flag(flag=flag,get_stats=True,include_legacy_stats=legacy,**kw);
    self.dprintf(1,"stats: %.2f%% of rows and %.2f%% of correlations are flagged\n",stats[0]*100,stats[1]*100);
    return stats;

  def flag (self,flag=1,unflag=0,create=False,transfer=False,
          get_stats=False,include_legacy_stats=False,
          ddid=None,fieldid=None,
          channels=None,multichan=None,corrs=None,
          antennas=None,
          baselines=None,
          time=None,reltime=None,
          taql=None,
          progress_callback=None,
          ):
    ms = self._reopen();
    if not self.has_bitflags:
      if transfer:
        raise TypeError,"MS does not contain a BITFLAG column, cannot use flagsets""";
      if get_stats and flag:
        raise TypeError,"MS does not contain a BITFLAG column, cannot get statistics""";
    if get_stats and not flag and not include_legacy_stats:
      flag = -1;
    # lookup flagset name, if so specified
    if isinstance(flag,str):
      flagname = flag;
      flag = self.flagsets.flagmask(flag,create=create);
      self.dprintf(2,"flagset %s corresponds to bitmask 0x%x\n",flagname,flag);
    # lookup same for unflag, except we don't create
    if isinstance(unflag,str):
      flagname = unflag;
      unflag = self.flagsets.flagmask(unflag);
      self.dprintf(2,"flagset %s corresponds to bitmask 0x%x\n",flagname,unflag);
    if self.flagsets.names() is not None:
      if flag:
        self.dprintf(2,"flagging with bitmask 0x%x\n",flag);
      if unflag:
        self.dprintf(2,"unflagging with bitmask 0x%x\n",unflag);
    else:
      self.dprintf(2,"no bitflags in MS, using legacy FLAG/FLAG_ROW columns\n",unflag);
    # form up list of TaQL expressions for subset selectors
    queries = [];
    if taql:
      queries.append(taql);
    if ddid is not None:
      queries.append("DATA_DESC_ID==%d"%ddid);
    if fieldid is not None:
      queries.append("FIELD_ID==%d"%ddid);
    if antennas is not None:
      antlist = str(list(antennas));
      queries.append("(ANTENNA1 in %s || ANTENNA2 in %s)"%(antlist,antlist));
    if time is not None:
      t0,t1 = time;
      if t0 is not None:
        queries.append("TIME>=%g"%t0);
      if t1 is not None:
        queries.append("TIME<=%g"%t1);
    if reltime is not None:
      t0,t1 = reltime;
      time0 = self.ms.getcol('TIME',0,1)[0];
      if t0 is not None:
        queries.append("TIME>=%f"%(time0+t0));
      if t1 is not None:
        queries.append("TIME<=%f"%(time0+t1));
      
    # form up TaQL string, and extract subset of table
    if queries:
      query = ' && '.join(queries);
      self.dprintf(2,"selection string is %s\n",query);
      ms = ms.query(query);
      self.dprintf(2,"query reduces MS to %d rows\n",ms.nrows());
    else:
      self.dprintf(2,"no selection applied\n");
    
    # this will be true if only whole rows are being selected. If channel/correlation
    # criteria are supplied, this will be set to False below
    flagrows = True;
    # form up channel and correlation slicers
    # multichan may specify multiple channel subsets. If not specified,
    # then channels specifies a single subset. In any case, in the end multichan
    # will contain a list of the current channel selection
    if multichan is None:
      if channels is None:
        multichan = [ numpy.s_[:] ];
      else:
        flagrows = False;
        multichan = [ channels ];
    else:
      flagrows = False;
    self.dprintf(2,"channel selection is %s\n",multichan);
    if corrs is None:
      corrs = numpy.s_[:];
    else:
      flagrows = False;
    self.dprintf(2,"correlation selection is %s\n",corrs);
    stat_rows_nfl = stat_rows = stat_pixels = stat_pixels_nfl = 0;
    # go through rows of the MS in chunks
    for row0 in range(0,ms.nrows(),self.chunksize):
      if progress_callback:
        progress_callback(row0,ms.nrows());
      nrows = min(self.chunksize,ms.nrows()-row0);
      self.dprintf(2,"flagging rows %d:%d\n",row0,row0+nrows-1);
      # get mask of matching baselines
      if baselines:
        # init mask of all-false
        rowmask = numpy.zeros(nrows,dtype=numpy.bool);
        a1 = ms.getcol('ANTENNA1',row0,nrows);
        a2 = ms.getcol('ANTENNA2',row0,nrows);
        # update mask
        for p,q in baselines:
          rowmask |= (a1==p) & (a2==q);
        self.dprintf(2,"baseline selection leaves %d rows\n",len(rowmask.nonzero()[0]));
      # else select all rows
      else:
        rowmask = numpy.s_[:];
        self.dprintf(2,"no baseline selection applied, flagging %d rows\n",nrows);
      # form up subsets for channel/correlation selector
      subsets = [ (rowmask,ch,corrs) for ch in multichan ];
      # first, handle statistics mode
      if get_stats:
        # collect row stats
        if include_legacy_stats:
          lfr  = ms.getcol('FLAG_ROW',row0,nrows)[rowmask];
          lf   = ms.getcol('FLAG',row0,nrows);
        else:
          lfr = lf = 0;
        if flag:
          bfr = ms.getcol('BITFLAG_ROW',row0,nrows)[rowmask];
          lfr = lfr + ((bfr&flag)!=0);
          bf = ms.getcol('BITFLAG',row0,nrows);
        stat_rows     += lfr.size;
        stat_rows_nfl += lfr.sum();
        for subset in subsets:
          if include_legacy_stats:
            lfm = lf[subset];
          else:
            lfm = 0;
          if flag:
            lfm = lfm + (bf[subset]&flag)!=0;
          stat_pixels     += lfm.size;
          stat_pixels_nfl += lfm.sum();
      # second, handle transfer-flags mode
      elif transfer:
        bf = ms.getcol('BITFLAG_ROW',row0,nrows);
        bfm = bf[rowmask];
        if unflag:
          bfm &= ~unflag;
        lf = ms.getcol('FLAG_ROW',row0,nrows)[rowmask];
        bf[rowmask] = numpy.where(lf,bfm|flag,bfm);
        stat_rows     += lf.size;
        stat_rows_nfl += lf.sum();
        ms.putcol('BITFLAG_ROW',bf,row0,nrows);
        bf = ms.getcol('BITFLAG',row0,nrows);
        lf = ms.getcol('FLAG',row0,nrows);
        for subset in subsets:
          bfm = bf[subset];
          if unflag:
            bfm &= ~unflag;
          lfm = lf[subset]
          bf[subset] = numpy.where(lfm,bfm|flag,bfm);
          stat_pixels     += lfm.size;
          stat_pixels_nfl += lfm.sum();
        ms.putcol('BITFLAG',bf,row0,nrows);
      # else, are we flagging whole rows?
      elif flagrows:
        if self.has_bitflags:
          bfr = ms.getcol('BITFLAG_ROW',row0,nrows);
          if unflag:
            bfr[rowmask] &= ~unflag;
            # if unflaging, also have to clear flags from BITFLAG too
            bf = ms.getcol('BITFLAG',row0,nrows);
            bf[rowmask,:,:] &= ~unflag;
            ms.putcol('BITFLAG',bf,row0,nrows);
          if flag:
            bfr[rowmask] |= flag;
          ms.putcol('BITFLAG_ROW',bfr,row0,nrows);
        else:
          lf = ms.getcol('FLAG_ROW',row0,nrows);
          lf[rowmask] = (flag!=0);
          ms.putcol('FLAG_ROW',lf,row0,nrows);
      # else flagging individual correlations or channels
      else: 
        # apply flagmask
        if self.has_bitflags:
          bf = ms.getcol('BITFLAG',row0,nrows);
          if unflag:
            for subset in subsets:
              bf[subset] &= ~unflag;
          if flag:
            for subset in subsets:
              bf[subset] |= flag;
          ms.putcol('BITFLAG',bf,row0,nrows);
        else:
          bf = ms.getcol('FLAG',row0,nrows);
          for subset in subsets:
            bf[subset] = (flag!=0);
          ms.putcol('FLAG',bf,row0,nrows);
    if progress_callback:
      progress_callback(ms.nrows(),ms.nrows());
    stat0 = (stat_rows and stat_rows_nfl/float(stat_rows)) or 0;
    stat1 = (stat_pixels and stat_pixels_nfl/float(stat_pixels)) or 0;
    return stat0,stat1;
      
  def set_legacy_flags (self,flags,progress_callback=None):
    """Fills the legacy FLAG/FLAG_ROW column by applying the specified flagmask
    to bitflags.
    * if flags is an int, it is used as a bitflag mask
    * if flags is a str, it is treated as the name of a flagset
    * if flags is a list or tuple, it is treated as a list of flagsets
    """;
    ms = self._reopen();
    if not self.has_bitflags:
      raise TypeError,"MS does not contain a BITFLAG column, cannot use bitflags""";
    if isinstance(flags,str):
      flagmask = self.flagsets.flagmask(flags);
      self.dprintf(1,"filling legacy FLAG/FLAG_ROW using flagset %s\n",flags);
    elif isinstance(flags,(list,tuple)):
      flagmask = 0;
      for fl in flags:
        flagmask |= self.flagsets.flagmask(fl);
      self.dprintf(1,"filling legacy FLAG/FLAG_ROW using flagsets %s\n",flags);
    elif isinstance(flags,int):
      flagmask = flags;
    else:
      raise TypeError,"flagmask argument must be int, str or sequence";
    self.dprintf(1,"filling legacy FLAG/FLAG_ROW using bitmask 0x%d\n",flagmask);
    # now go through MS and fill the column
    # go through rows of the MS in chunks
    for row0 in range(0,ms.nrows(),self.chunksize):
      if progress_callback:
        progress_callback(row0,ms.nrows());
      nrows = min(self.chunksize,ms.nrows()-row0);
      self.dprintf(2,"filling rows %d:%d\n",row0,row0+nrows-1);
      bf  = ms.getcol('BITFLAG',row0,nrows);
      bfr = ms.getcol('BITFLAG_ROW',row0,nrows);
      ms.putcol('FLAG',(bf&flagmask).astype(Timba.array.dtype('bool')),row0,nrows);
      ms.putcol('FLAG_ROW',(bfr&flagmask).astype(Timba.array.dtype('bool')),row0,nrows);
    if progress_callback:
      progress_callback(ms.nrows(),ms.nrows());
      
  def clear_legacy_flags (self,progress_callback=None):
    """Clears the legacy FLAG/FLAG_ROW columns.
    """;
    ms = self._reopen();
    self.dprintf(1,"clearing legacy FLAG/FLAG_ROW column\n");
    # now go through MS and fill the column
    # go through rows of the MS in chunks
    shape = list(ms.getcol('FLAG',0,1).shape);
    shape[0] = self.chunksize
    fzero  = Timba.array.zeros(shape,dtype='bool');
    frzero = Timba.array.zeros((self.chunksize,),dtype='bool');
    for row0 in range(0,ms.nrows(),self.chunksize):
      if progress_callback:
        progress_callback(row0,ms.nrows());
      nrows = min(self.chunksize,ms.nrows()-row0);
      if nrows < self.chunksize:
        fzero = fzero[:nrows,:,:];
        frzero = frzero[:nrows];
      self.dprintf(2,"filling rows %d:%d\n",row0,row0+nrows-1);
      ms.putcol('FLAG',fzero,row0,nrows);
      ms.putcol('FLAG_ROW',frzero,row0,nrows);
    if progress_callback:
      progress_callback(ms.nrows(),ms.nrows());

  
  def autoflagger (self,*args,**kw):
    return Flagger.AutoFlagger(self,*args,**kw);
  
  class AutoFlagger (object):
    def __init__ (self,flagger,load=False):
      self.flagger = flagger;
      self._cmds = [];
      if load:
        if isinstance(load,bool):
          load = 'default.af';
        self.load(load);
      
    def _cmd (self,cmd):
      self._cmds.append(cmd);
      
    def reset (self):
      self._cmds = [];
      
    def setdata (self,chanstart=None,chanend=None,chanstep=None,spwid=None,fieldid=None,msselect=None):
      args = [];
      if chanstart is not None:
        chanstep = chanstep or 1;
        chanend  = chanend or chanstart;
        totchan = chanend-chanstart+1;
        nchan = totchan/chanstep;
        if totchan%chanstep:
          nchan += 1;
        args += [ "mode='channel'","nchan=%d"%nchan,"start=%d"%(start+1),"step=%d"%step ];
      if spwid is not None:
        args.append("spwid=%d"%(spwid+1));
      if fieldid is not None:
        args.append("fieldid=%d"%(fieldid+1));
      if msselect is not None:
        args.append("msselect='%s'"%msselect);
      self._cmd("af.setdata(%s);"%(','.join(args))); 
    
    _settimemed_dict    = dict(thr="%g",hw="%d",rowthr="%g",rowhw="%d",norow=_format_bool,
                                column="'%s'",expr="'%s'",fignore=_format_bool);
    _setnewtimemed_dict = dict(thr="%g",
                                column="'%s'",expr="'%s'",fignore=_format_bool);
    _setfreqmed_dict    = dict(thr="%g",hw="%d",rowthr="%g",rowhw="%d",norow=_format_bool,
                                column="'%s'",expr="'%s'",fignore=_format_bool);
    _setuvbin_dict      = dict(thr="%g",minpop="%d",nbins=_format_nbins,
                                plotchan=_format_plotchan,econoplot=_format_bool,
                                column="'%s'",expr="'%s'",fignore=_format_bool);
    _setsprej_dict      = dict(ndeg="%d",rowthr="%g",rowhw="%d",norow=_format_bool,
                                spwid=_format_list,fq=_format_2N,chan=_format_2N,
                                column="'%s'",expr="'%s'",fignore=_format_bool);
    _setselect_dict     = dict(spwid=_format_ilist,field=_format_ilist,
                                fq=_format_2N,chan=_format_2N,corr=_format_list,
                                ant=_format_ilist,baseline=_format_ilist,timerng=_format_list,
                                autocorr=_format_bool,timeslot=_format_list,dtime="%g",
                                quack=_format_bool,unflag=_format_bool,clip=_format_clip);
    _run_dict           = dict(plotscr=_format_list,plotdev=_format_list,devfile="'%s'",
                                reset=_format_bool,trial=_format_bool);
    
    def _setmethod (self,methodname,kwargs):
      argdict = getattr(self,'_%s_dict'%methodname);
      args = [];
      for kw,value in kwargs.iteritems():
        format = argdict.get(kw,None);
        if format is None:
          raise TypeError,"Autoflagger: invalid keyword '%s' passed to method %s()"%(kw,methodname);
        elif callable(format):
          args.append("%s=%s"%(kw,format(value,kw)));
        else:
          args.append("%s=%s"%(kw,format%value));
      return "af.%s(%s);"%(methodname,','.join(args)); 
      
    def settimemed (self,**kw):
      self._cmd(self._setmethod('settimemed',kw));
    def setfreqmed (self,**kw):
      self._cmd(self._setmethod('setfreqmed',kw));
    def setnewtimemed (self,**kw):
      self._cmd(self._setmethod('setnewtimemed',kw));
    def setsprej (self,**kw):
      self._cmd(self._setmethod('setsprej',kw));
    def setuvbin (self,**kw):
      self._cmd(self._setmethod('setuvbin',kw));
    def setselect (self,**kw):
      self._cmd(self._setmethod('setselect',kw));
      
    def run (self,wait=True,**kw):
      runcmd = self._setmethod('run',kw);
      # init list of command strings
      cmds = [ "include 'autoflag.g'","af:=autoflag('%s');"%self.flagger.msname ];
      # add default setdata() if not specified
      if not filter(lambda x:x.startswith('af.setdata'),self._cmds):
        cmds.append("af.setdata();");
      # add specified command set
      cmds += self._cmds;
      # add the run command
      cmds += [ runcmd ];
      self.flagger.dprint(2,"running autoflag with the following command set:")
      for cmd in cmds:
        self.flagger.dprint(2,cmd);
      if _GLISH is None:
        raise RuntimeError,"glish not found, so cannot run autoflagger";
      # tell flagger to detach from MS
      self.flagger.close();
      # write commands to temporary file and run glish
      fh,cmdfile = tempfile.mkstemp(prefix="autoflag",suffix=".g");
      cmds += [ "shell('rm -f %s')"%cmdfile,"exit" ];
      os.fdopen(fh,"wt").writelines([line+"\n" for line in cmds]);
      self.flagger.dprintf(3,"temp glish command file is %s\n"%cmdfile);
      waitcode = (wait and os.P_WAIT) or os.P_NOWAIT;
      return os.spawnvp(waitcode,_GLISH,['glish','-l',cmdfile]);
    
    def save (self,filename='default.af'):
      file(filename,"w").writelines([line+"\n" for line in self._cmds]);
      self.flagger.dprintf(2,"saved autoflag command sequence to file %s\n",filename);
      
    def load (self,filename='default.af'):
      self._cmds = file(filename).readlines();
      self.flagger.dprintf(2,"loaded autoflag command sequence from file %s\n",filename);
      self.flagger.dprint(2,"sequence is:");
      for cmd in self._cmds:
        self.flagger.dprint(3,cmd);
      