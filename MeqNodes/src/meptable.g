### meptable.g: Glish script to add parameters to the MEP table
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

include 'table.g'
include 'meq/meqtypes.g'

# -----------------------------------------------------------------------
# class meptable
#    This represents a table of MEPs
#
# -----------------------------------------------------------------------

#------ meptable constructor
# Opens table specified by name.
# If create=T, creates a new table
const meq.meptable := function (name,create=F)
{
    self:=[=];
    public:=[=];

    if (create) {
        # Create the main table.
        d1 := tablecreatescalarcoldesc ('NAME', '');
        d4 := tablecreatescalarcoldesc ('STARTFREQ', as_double(0));
        d5 := tablecreatescalarcoldesc ('ENDFREQ', as_double(0));
        d6 := tablecreatescalarcoldesc ('STARTTIME', as_double(0));
        d7 := tablecreatescalarcoldesc ('ENDTIME', as_double(0));
        d8 := tablecreatearraycoldesc  ('VALUES', as_double(0));
        d11:= tablecreatescalarcoldesc ('FREQ0', as_double(0));
        d12:= tablecreatescalarcoldesc ('TIME0', as_double(0));
        d13:= tablecreatescalarcoldesc ('FREQSCALE', as_double(0));
        d14:= tablecreatescalarcoldesc ('TIMESCALE', as_double(0));
        d15:= tablecreatescalarcoldesc ('PERT', as_double(0));
        d16:= tablecreatescalarcoldesc ('WEIGHT', as_double(0));
        td := tablecreatedesc (d1, d4, d5, d6, d7, d8,
                               d11, d12, d13, d14, d15, d16);
        self.tab := table (name, td);
        if (is_fail(self.tab)) {
            fail;
        }
        info := self.tab.info();
        info.type := 'MEP';
        self.tab.putinfo (info);
        self.tab.addreadmeline ('PSS ME parameter values');
        
        # Create the table with default values.
        dtabname := spaste(name,'/DEFAULTVALUES');
        td := tablecreatedesc (d1, d8, d11, d12, d13, d14, d15);
        self.dtab := table (dtabname, td);
        if (is_fail(self.dtab)) {
            fail;
        }
        info := self.dtab.info();
        info.type := 'MEPdef';
        self.dtab.putinfo (info);
        self.dtab.addreadmeline ('Default PSS ME parameter values');
        
        # Make it a subtable of the main table.
        self.tab.putkeyword ('DEFAULTVALUES', spaste('Table: ',dtabname));
    } else {
        self.tab := table (name, readonly=F);
        if (is_fail(self.tab)) {
            fail;
        }
        kws := self.tab.getkeywords();
        if (has_field (kws, 'DEFAULTVALUES')) {
            self.dtab := table (kws.DEFAULTVALUES, readonly=F);
            if (is_fail(self.dtab)) {
                fail;
            }
        } else {
            self.dtab := F;
        }
    }

#------ done()
# closes table
    const public.done := function()
    {
        wider self, public;
        self.tab.close();
        if( is_record(self.dtab) ) 
          self.dtab.close();
        val self := F;
        val public := F;
        return T;
    }

#------ putdef1()
# inserts a default entry for parameter parmname, with the polc order
# explicitly specified as nfreq,ntime.
# The c00 coeff is set to 'value', and the rest to 0.
# A scale and a default perturbation may also be specified.
    const public.putdef1 := function (parmname,
                                value, nfreq, ntime, perturbation=1e-6, 
                                freq0=0., time0=4.56e9, 
                                freqscale=1e6, timescale=1., 
                                trace=T)
    {
        vals := array(as_double(0), nfreq, ntime);
        vals[1,1] := value;
        public.putdef (parmname, vals, perturbation, freq0, time0,
                       freqscale, timescale, trace);
    }

#------ putdef()
# inserts a default entry for parameter parmname, with the polc order
# determined by the shape of the 'values' argument.
# 'values' is a complete set of coeffs.
# A scale and a default perturbation may also be specified.
    const public.putdef := function (parmname,
                               values=1, perturbation=1e-6, 
                               freq0=0., time0=4.56e9, 
                               freqscale=1e6, timescale=1., 
                               trace=T)
    {
        #----------------------------------------------------------------
        funcname := paste('** meptable.putdef(',parmname,'):');
        input := [parmname=parmname, values=values, perturbation=perturbation, 
                  freq0=freq0, time0=time0, 
                  freqscale=freqscale, timescale=timescale];
        if (trace) print funcname,' input=',input;
        #----------------------------------------------------------------

        if (!is_record(self.dtab)) {
            fail "No DEFAULTVALUES subtable";
        }
        t1 := self.dtab.query (spaste('NAME=="',parmname,'"'));
        nr := t1.nrows();
        t1.close();
        if (nr != 0) {
            fail paste('Parameter',parmname,'already has a default value');
        }
        # Turn a scalar into a matrix.
        if (length(shape(values)) == 1  &&  length(values) == 1) {
            values := array (values, 1, 1);
        }
        if (length(shape(values)) != 2  ||  !is_numeric(values)) {
            fail paste('values should be a 2-dim numerical array');
        }
        self.dtab.addrows(1);
        rownr := self.dtab.nrows();
        self.dtab.putcell ('NAME', rownr, parmname);
        self.dtab.putcell ('FREQ0', rownr, freq0)
        self.dtab.putcell ('TIME0', rownr, time0)
        self.dtab.putcell ('FREQSCALE', rownr, freqscale)
        self.dtab.putcell ('TIMESCALE', rownr, timescale)
        self.dtab.putcell ('VALUES', rownr, as_double(values));
        self.dtab.putcell ('PERT', rownr, perturbation);
        return T;
    }

#------ put()
# Writes out a polc for parameter parmname. The components of the polc
# are specified via the arguments.
# If rownr is set, overwrites the polc at the specified row. If rownr<0,
# adds a row to the table (and returns its number via rownr).
# If uniq=T, ensures that the polc is unique for this parm and domain:
#   - checks if a polc for the specified domain already exists;
#   - if it does, checks that row number matches;
#   - on match, allows an overwrite. No match (incl. rownr<0) -- fails.
    const public.put := function (parmname,
                            freqrange=[0,1e20], timerange=[0,1e20], 
                            values=1, perturbation=1e-6, weight=1,
                            freq0=0., time0=4.56e9, 
                            freqscale=1e6, timescale=1,
                            ref rownr=-1,uniq=T,trace=T)
    {
        #----------------------------------------------------------------
        funcname := paste('** meptable.put(',parmname,'):');
        input := [parmname=parmname, values=values, solvable=solvable,
                  freqrange=freqrange, timerange=timerange, 
                  perturbation=perturbation,weight=weight,
                  freq0=freq0, time0=time0,
                  freqscale=freqscale, timescale=timescale];
        if (trace) print funcname,' input=',input;
        #----------------------------------------------------------------

        if (length(freqrange) != 2) {
            fail 'freqrange should be a vector of 2 elements (start,end)';
        }
        if (length(timerange) != 2) {
            fail 'timerange should be a vector of 2 elements (start,end)';
        }
        if( uniq )
        {
          t1 := self.tab.query( spaste('NAME=="',parmname,'" ',
                                       '&& near(STARTFREQ,', freqrange[1],') ',
                                       '&& near(ENDFREQ,'  , freqrange[2],') ',
                                       '&& near(STARTTIME,', timerange[1],') ',
                                       '&& near(ENDTIME,'  , timerange[2],') '));
          rownrs := t1.rownumbers(self.tab);
          t1.close();
          # disallow overwrites, unless the row argument explicitly matches
          # the row number
          if( len(rownrs) && rownrs[1] != rownr ) {
              fail paste('Parameter',parmname,'already defined for given domain');
          }
        }
        # Turn a scalar into a matrix.
        if (length(shape(values)) == 1  &&  length(values) == 1) {
            values := array (values, 1, 1);
        }
        if (length(shape(values)) != 2  ||  !is_numeric(values)) {
            fail paste('values should be a 2-dim numerical array');
        }
        if( rownr <= 0 )
        {
          self.tab.addrows(1);
          val rownr := self.tab.nrows();
        }
        self.tab.putcell ('NAME', rownr, parmname);
        self.tab.putcell ('STARTFREQ', rownr, freqrange[1]);
        self.tab.putcell ('ENDFREQ', rownr, freqrange[2]);
        self.tab.putcell ('STARTTIME', rownr, timerange[1]);
        self.tab.putcell ('ENDTIME', rownr, timerange[2]);
        self.tab.putcell ('FREQ0', rownr, freq0)
        self.tab.putcell ('TIME0', rownr, time0)
        self.tab.putcell ('FREQSCALE', rownr, freqscale)
        self.tab.putcell ('TIMESCALE', rownr, timescale)
        self.tab.putcell ('VALUES', rownr, as_double(values));
        self.tab.putcell ('PERT', rownr, perturbation);
        self.tab.putcell ('WEIGHT', rownr, weight);
        return T;
    }
    
#------ putpolc()
# Writes out a polc for parameter parmname. The polc is specified as
# a meq.polc object.
# If set, the polc's dbid_index field is interpreted just like the rownr 
# argument to put(). If a new row is assigned, it is written into
# polc.dbid_index (this is why polc is passed by ref).
# uniq is interpreted same as for put().
    const public.putpolc := function (parmname,ref polc,uniq=T)
    {
      wider self,public;
      if( !is_dmi_type(polc,'MeqPolc') )
        fail 'polc argument must be a meq.polc object';
      if( has_field(polc,'domain') )
        dom := polc.domain;
      else
        dom := meq.domain(0,1,0,1);
      return public.put(parmname,
                  freqrange=dom.freq,timerange=dom.time,
                  values=polc.coeff, perturbation=polc.pert,
                  weight=polc.weight,
                  freq0=polc.freq_0,time0=polc.time_0,
                  freqscale=polc.freq_scale,timescale=polc.time_scale,
                  rownr=polc.dbid_index,uniq=uniq);
    }
    
#------ getpolcs()
# Retrieves all the polcs for the specified parameter.
# Returns a record (used as a vector) of meq.polc objects.
    const public.getpolcs := function (parmname)
    {
      wider self,public;
      t1 := self.tab.query(spaste('NAME=="',parmname,'" '));
      if( !t1.nrows() )
        return [=];
      polcs := [=];
      df0c := t1.getcol('STARTFREQ');
      df1c := t1.getcol('ENDFREQ');
      dt0c := t1.getcol('STARTTIME');
      dt1c := t1.getcol('ENDTIME');
      fq0c := t1.getcol('FREQ0');
      tm0c := t1.getcol('TIME0');
      fqsc := t1.getcol('FREQSCALE');
      tmsc := t1.getcol('TIMESCALE');
      pertc := t1.getcol('PERT');
      weightc := t1.getcol('WEIGHT');
      rownums := t1.rownumbers(self.tab);
      for( i in 1:t1.nrows() )
      {
        polcs[spaste('#',i)] := 
            meq.polc(t1.getcell('VALUES',i),
                     domain=meq.domain(df0c[i],df1c[i],dt0c[i],dt1c[i]),
                     freq0=fq0c[i],time0=tm0c[i],
                     freqsc=fqsc[i],timesc=tmsc[i],pert=pertc[i],
                     weight=weightc[i],dbid=rownums[i]);
      }
      polcs::dmi_datafield_content_type := 'MeqPolc';
      return polcs;
    }

#------ summary()
# Returns a string summary of MEP table contents.
# If called with no arguments, provides an overall summary.
# If called with parmnames as arguments, summarizes the parms.
# By default, returns a multi-line string with embedded newlines
# (i.e. suitable for printing). If one of the arguments is a bool T, 
# then returns a vector of strings (one line per string) with no newlines.
    const public.summary := function (...)
    {
      wider self,public;
      names := self.tab.getcol("NAME");
      dnames := self.dtab.getcol("NAME");
      out := paste('MEP table:',self.tab.name());
      parms := "";
      return_string_vector := F;    # true by default
      # scan arguments
      if( num_args(...) )
        for( i in 1:num_args(...) )
        {
          arg := nth_arg(i,...);
          if( is_boolean(arg) )    # boolean arg is the return_string flag
            return_string_vector := arg;
          else if( is_string(arg) ) # string arg is a parm name
            parms := [parms,arg];
          else
            fail paste('illegal argument',arg);
        }
      # if no polc names have been given, produce an overall summary
      if( !len(parms) )
      {
        # self.tab.summary();
        # if( is_record(self.tab) )
        #   self.dtab.summary();
        out[len(out)+1] := paste('Main table:',self.tab.nrows(),'rows');
        if( is_record(self.dtab) )
          out[len(out)+1] := paste('Defaults subtable:',self.dtab.nrows(),'rows');
        else
          out[len(out)+1] := 'No defaults subtable';
        if( is_string(names) )
          out[len(out)+1] := paste('MEP names:',unique(sort(names)));
        if( is_string(dnames) )
          out[len(out)+1] := paste('Defaults available for:',unique(sort(dnames)));
      }
      else # else produce a per-parm summary
      {
        for( p in parms )
        {
          polcs := public.getpolcs(p);
          t1 := self.dtab.query(spaste('NAME=="',p,'"'));
          out[len(out)+1] := paste(spaste('MEP "',p,'":'),len(polcs),'polcs,',t1.nrows(),'default(s)');
          t1.close();
        }
      }
      if( return_string_vector )
        return out;
      else
        return paste(out,sep='\n');
    }

#------ table()
# Returns a ref to the internal main table object
    const public.table := function()
    {
        return ref self.tab;
    }

#------ deftable()
# Returns a ref to the internal defaultvalues subtable object
    const public.deftable := function()
    {
        return ref self.dtab;
    }

    return ref public;
}
