#$Prog$
#
#  $Id: 
#
#  $Purpose: Infor function for OLT
#
#  $Usage:  - is loaded by OLT.g
#          
#  $Log$
#  Revision 1.2  2005/10/12 11:57:05  assendorp
#  Changed IFFreq format
#
#  Revision 1.1  2005/06/08 12:14:19  assendorp
#  Added to CVS
#
#
#
#$/Prog$
#

include 'table.g'
include 'quanta.g'

#
# Definitions
#
RAD2DEG := 180.0/pi;
JD200510 := 2453370.5;            # Julian day number at 00JAN2005
ST0 := 6.6505333333333336;        # ST at greenwich for the above date
UT2ST := 1.0027379094;            # convertion of UT to ST
WSRTlon := 6.605/15.0;            # longitude of WSRT in hours
TESTlon := -80.382163888888883;   # longitude of test in pract.astr.w.y.calc.

sgn := function(x)
{
    if (x < 0){
      return -1;
    } else {
      return 1;
    }
}

#
# convert gregorian date to julian day
#
Greg2Jul := function(y, m, d, hr, mt, sc)
{
    UT := hr + mt/60.0 + sc/3600.0;
    A := 367*y;
    B := as_integer((7*(y+as_integer((m+9)/12)))/4);
    C := as_integer(275*m/9);
    c1 := 1721013.5;
    c2 := 0.5;
    D := UT/24.0;
    E := 0.5*sgn(100*y+m-190002.5);

    JD := A - B + C + d + c1 + D - E + c2;

    if (JD < 2436934.5){
      print 'ERROR - date before 1960.';
      JD := 2436934.5
    }


    return JD;
}

#
# Greenwich SidTime for a julian day
#
GWSidTime := function(JD)
{
  nd := JD-JD200510;
  GWst := nd*24.0*UT2ST + ST0;
  while (GWst > 24){
    GWst := GWst-24.0;
  }
  while (GWst < 0){
    GWst := GWst + 24;
  }
  while (GWst > 24){
    GWst := GWst - 24;
  }
  
  return GWst;
}

#
# WSRT SidTime for a julian day
#
WSRTSidTime := function(JD)
{
  t := GWSidTime(JD) + WSRTlon;
  while (t > 24){
    t := t-24.0;
  }
  while (t < 0){
    t := t-24.0;
  }
  
  return t;
}

#
# WSRT HA for a given data/time and RA, in dec. degree
#
WSRTHA := function(y, m, d, hr, mt, sc, RA)
{
  JD := Greg2Jul(y, m, d, hr, mt, sc);
  ST := WSRTSidTime(JD);
  HA := ST*15.0 - RA;
  while (HA > 360) HA := HA - 360;
  while (HA < 0) HA := HA + 360;
  if (HA > 180) HA := HA - 360;


  return HA;
}

dms2deg := function(dg, mt, sc)
{
  s := dg + mt/60.0 + sc/3600.0;
  return s;
}

deg2dms := function(d)
{
  pm := 1;
  if (d < 0){
    pm := -1;
    d := -d;
  }
  dd := as_integer(d);
  m := (d-dd)*60.0;
  mm := as_integer(m);
  s := (m-mm)*60.0;

  if (pm == 1){
    q := spaste('+', dd, ':', mm, ':', s);
  } else {
    q := spaste('-', dd, ':', mm, ':', s);
  }

  print q
  return T;
}

closetables := function(OLTr)
{
  if (!is_record(OLTr.tabRec)) return F;

  OLTr.tabRec.main.done();
  OLTr.tabRec.ant.done();
  OLTr.tabRec.dd.done();
  OLTr.tabRec.feed.done();
  OLTr.tabRec.flag.done();
  OLTr.tabRec.fld.done();
  OLTr.tabRec.hist.done();
  OLTr.tabRec.obs.done();
  OLTr.tabRec.pnt.done();
  OLTr.tabRec.pol.done();
  OLTr.tabRec.proc.done();
  OLTr.tabRec.src.done();
  OLTr.tabRec.spw.done();
  OLTr.tabRec.stt.done();
  OLTr.tabRec.sys.done();
  OLTr.tabRec.wth.done();
  OLTr.tabRec.nfra.done();

  OLTr.tabRec := F;

  return OLTr;
}

nfrakwd := function(MS='help', kwd=F)
{
#
# Input may be a cry for help
#
  if (is_string(MS) && (MS == 'help')){
    showhelp(NFRAhelp);
    return T;
  }

#
# Prepare return struct.
#
  rtn := [=];
  rtn._ID := 'nfrakwd';
  rtn._OLT := T;
  rtn.error := 0;
  rtn.errstr := 'No error';
  rtn.value := F;
  rtn.tabRec := F;
  rtn.infRec := F;
  rtn.valRec := F;

#
# Check if second parameter is string
#
  if (! is_string(kwd)){
    rtn.error := 2;
    rtn.errstr := 'Second parameter must be of type string.';
    return rtn;
  }

#
# Locate keyword in table.
# If not found, set error value and return
#
#  print 'DEBUG - nfrakwd - MS.tabRec', type_name(MS.tabRec);
  mask := MS.tabRec.nfra.getcol('NAME') == kwd;

#
# if the keyword is present there will be one T in the mask, the other values
# will be F. So len(unique(mask)) will be 2 if the keyword is present.
#
  if (len(unique(mask)) == 1) {
    rtn.error := 3;
    rtn.errstr := 'Keyword not found in table.';
    return rtn;
  }

#
# get value and return
#
  rtn.value := MS.tabRec.nfra.getcol('VALUE')[mask];
  return rtn;
}

opentables := function(tableName)
{
#  print 'DEBUG - opentables', tableName;
#
# This function does not return a TRUE OLT record.
# If all is OK, the function returns a Table Record,
# else the function returns an error string.
#

  rtn := [=];
  rtn.error := 0;

#
# Input parameter must be a string
#
  if (type_name(tableName) != 'string'){
    rtn.error := 1;
    rtn.errstr := 'MS is not a string.';
    return rtn;
  }

#
# Input parameter must be a directory name
#
  stt := stat(tableName);
  if (len(stt) == 0){
    rtn.error := 2;
    rtn.errstr := spaste('No such file or directory: ', tableName, '.');
    return rtn;
  }

#
# Input parameter must realy be a directory
#
  if (stt.type != 'directory'){
#
# The directory might be a link, try to add a '/' to the name
#
    tableName := spaste(tableName, '/');
    stt := stat(tableName);
    if (len(stt) == 0){
      rtn.error := 3;
      rtn.errstr := spaste('No such file or directory: ', tableName, '.');
      return rtn;
    }
  }

#
# Input parameter must be an aips++ table
#
  if (! tableexists(tableName)){
    rtn.error := 4;
    rtn.errstr := spaste(tableName, ' is not an aips++ table.');
    return rtn;
  }

#
# All seems OK, open the tables
#
  rtn.name := tableName;

#
# Open (all) tables, check if they are open - there are MSs in the
# archive where tables are not valid aips++ tables.
#
  d := table(tableName);
  if (!is_record(d)){
    rtn.error := 5;
    rtn.errstr := 'cannot open MAIN table';
    return rtn;
  }

  rtn.main := d;

  rtn.ant := table(d.getkeyword('ANTENNA'));
  if (!is_record(rtn.ant)){
    rtn.error := 6;
    rtn.errstr := 'cannot open ANTENNA table';
    return rtn;
  }

  rtn.dd   := table(d.getkeyword('DATA_DESCRIPTION'));
  if (!is_record(rtn.dd)){
    rtn.error := 7;
    rtn.errstr := 'cannot open DATA_DESCRIPTION table';
    return rtn;
  }

  rtn.feed := table(d.getkeyword('FEED'));
  if (!is_record(rtn.feed)){
    rtn.error := 8;
    rtn.errstr := 'cannot open FEED table';
    return rtn;
  }

  rtn.flag := table(d.getkeyword('FLAG_CMD'));
  if (!is_record(rtn.flag)){
    rtn.error := 9;
    rtn.errstr := 'cannot open FLAG_CMD table';
    return rtn;
  }

  rtn.fld := table(d.getkeyword('FIELD'));
  if (!is_record(rtn.fld)){
    rtn.error := 10;
    rtn.errstr := 'cannot open FIELD table';
    return rtn;
  }

  rtn.hist := table(d.getkeyword('HISTORY'));
  if (!is_record(rtn.hist)){
    rtn.error := 11;
    rtn.errstr := 'cannot open HISTORY table';
    return rtn;
  }

  rtn.obs := table(d.getkeyword('OBSERVATION'));
  if (!is_record(rtn.obs)){
    rtn.error := 12;
    rtn.errstr := 'cannot open OBSERVATION table';
    return rtn;
  }

  rtn.pnt := table(d.getkeyword('POINTING'));
  if (!is_record(rtn.pnt)){
    rtn.error := 13;
    rtn.errstr := 'cannot open POINTING table';
    return rtn;
  }

  rtn.pol := table(d.getkeyword('POLARIZATION'));
  if (!is_record(rtn.pol)){
    rtn.error := 14;
    rtn.errstr := 'cannot open POLARIZATION table';
    return rtn;
  }

  rtn.proc := table(d.getkeyword('PROCESSOR'));
  if (!is_record(rtn.proc)){
    rtn.error := 15;
    rtn.errstr := 'cannot open PROCESSOR table';
    return rtn;
  }

  rtn.src := table(d.getkeyword('SOURCE'));
  if (!is_record(rtn.src)){
    rtn.error := 16;
    rtn.errstr := 'cannot open SOURCE table';
    return rtn;
  }

  rtn.spw := table(d.getkeyword('SPECTRAL_WINDOW'));
  if (!is_record(rtn.spw)){
    rtn.error := 17;
    rtn.errstr := 'cannot open SPECTRAL_WINDOW table';
    return rtn;
  }

  rtn.stt := table(d.getkeyword('STATE'));
  if (!is_record(rtn.stt)){
    rtn.error := 18;
    rtn.errstr := 'cannot open STATE table';
    return rtn;
  }

  rtn.sys := table(d.getkeyword('SYSCAL'));
  if (!is_record(rtn.sys)){
    rtn.error := 19;
    rtn.errstr := 'cannot open SYSCAL table';
    return rtn;
  }

  rtn.wth := table(d.getkeyword('WEATHER'));
  if (!is_record(rtn.wth)){
    rtn.error := 20;
    rtn.errstr := 'cannot open WEATHER table';
    return rtn;
  }

  rtn.nfra := table(d.getkeyword('NFRA_TMS_PARAMETERS'));
  if (!is_record(rtn.nfra)){
    rtn.error := 21;
    rtn.errstr := 'cannot open NFRA_TMS_PARAMETERS table';
    return rtn;
  }

  return rtn;
}


mkOLTrec := function(MS='help')
{
#  print 'DEBUG - mkOLTrec', MS;
#
# Input may be a string, if so, it can be 'help' or an MS name
#
if (is_string(MS)){
  if (MS == 'help'){
    showhelp(MTRhelp);
    return T;
  }
}

rtn := [=];
rtn._OLT := T;
rtn._ID := 'mkOLTrec';
rtn.error := 0;
rtn.errstr := 'No Error';
rtn.tabRec := F;
rtn.infRec := F;
rtn.value := F;
rtn.valRec := F;

if (is_string(MS)){
#
# input is a string and not 'help' - it must be the name of an MS
#
  tRec := opentables(MS);
#  print 'DEBUG - mkOLTrec - MS', type_name(MS);

  if (tRec.error != 0){
    if ((tRec.error == 2) || (tRec.error == 3)){
      rtn.error := 1;
      rtn.errstr := spaste('No such file or directory: ', MS);
      return rtn;
    }
    if (tRec.error == 4){
      rtn.error := 2;
      rtn.errstr := spaste(MS, ' is not an aips++ table.');
      return rtn;
    }
    rtn.error := 3;
    rtn.errstr := spaste('opentables:', tRec.error, ':', tRec.errstr);
    return rtn;
  }
}
rtn.tabRec := tRec;
return rtn;
}

#
#==============================================================================
# inforec - get infor from MS
#
inforec := function(MS = 'help')
{
#
# check for help
#
  if (is_string(MS)){
    if (MS == 'help'){
      showhelp(InfRhelp);
      return T;
    }
  }

  DeleteTabRec := T;

#
# Create OLTrecord, open tables, check
#
  rtn := mkOLTrec(MS);
#  print 'DEBUG - inforec - rtn.tabRec', type_name(rtn.tabrec);
  if (rtn.error != 0){
    return rtn;
  }

#
# Create output record,
# Create fields that must be filled in outside this function
#
  rtn.infRec := [=];
  rtn.infRec.GLOBAL := '>> --------------------------------------------------';

#
# sequence number
#
#  print 'DEBUG - going for RTSystem.ActSeqNumber';
  p := nfrakwd(rtn, 'RTSystem.ActSeqNumber');
  if (p.error == 0){
    rtn.infRec.SeqNr := p.value;
  } else if (p.error == 3){
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'kwd \'RTSystem.ActSeqNumber\' not found, value set to table name.');
    print msg;
    w := split(rtn.tabRec.name, '.');
    rtn.infRec.SeqNr := w[1];
  } else {
    rtn.error := 6;
    rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }

  rtn.infRec.SubArray := '<ToBeFilledIn>';
  rtn.infRec.NrOfSets := '<ToBeFilledIn>';

#
# object name
#
  p := nfrakwd(rtn, 'PW1.FieldName');
  if (p.error == 0){
    rtn.infRec.ObjName := p.value;
  } else if (p.error == 3){
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'kwd \'PW1.FieldName\' not found, value set to \'Unknwon\'.');
    print msg;
    rtn.infRec.ObjName := 'Unknown';
  } else {
    rtn.error := 7;
    rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }

#
# Find backend (DCB or DZB)
#
  p := rtn.tabRec.obs.getcol('OBSERVER');
  if (is_fail(p)){
    rtn.error := 8;
    rtn.errstr := spaste('Cannot read column: \'OBSERVATION:OBSERVER\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  v := split(p[1])[1];
  if (v == 'ProcessDZB'){
    isDZB := T;
  } else if (v == 'ReadDZB'){
    isDZB := T;
  } else if (v == 'ProcessDCB'){
    isDZB := F;
  } else {
    rtn.error := 9;
    rtn.errstr := spaste('Unknown processor: ', v);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }    

#
# Find semester and project number.
# The column name changed from SHEDULE to OBS_SCHEDULE at some moment in the past.
#
  p := rtn.tabRec.obs.getcol('SCHEDULE');
  if (is_fail(p) || (len(p) == 0)){
    p := rtn.tabRec.obs.getcol('OBS_SCHEDULE');
    if (is_fail(p)){
      rtn.error := 10;
      rtn.errstr := spaste('Cannot read column: \'OBSERVATION:SCHEDULE\' or  \'OBSERVATION:OBS_SCHEDULE\'.');
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  }
  sp := split(p, '/');
  if (len(sp) < 2){
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'Unexpected format for Semester/ProjNr');
    print msg;
    rtn.infRec.Semester := 'Unknown';
    rtn.infRec.PrjNr := 'Unknown';
  } else {
    rtn.infRec.Semester := sp[1];
    rtn.infRec.PrjNr := sp[2];
  }

#
# Find instrument
#
  p := nfrakwd(rtn, 'Instrument');
  if (p.error == 0){
    rtn.infRec.Instrument := p.value;
  } else if (p.error == 3){
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'kwd \'Instrument\' not found, value set to \'Unknown\'.');
    print msg;
    rtn.infRec.Instrument := 'Unknown';
  } else {
    rtn.error := 12;
    rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  
  if (isDZB){
    rtn.infRec.BackEnd := 'DZB';
  } else {
    rtn.infRec.BackEnd := 'DCB';
  }

#
# Find baselines to A, B, C, D
#
  p := rtn.tabRec.ant.getcol('POSITION');
  if (is_fail(p)){
    rtn.error := 13;
    rtn.errstr := spaste('Cannot read column: \'ANTENNA:POSITION\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  if (shape(p)[2] <= 10){
    rtn.infRec.Baselines := 0;
  } else {
    nt := rtn.tabRec.ant.nrows()
    x := p[1,10:nt];
    y := p[2,10:nt];
    x := x - x[1];
    y := y - y[1];
    pv := as_integer(sqrt(x*x + y*y)+0.5);
    rtn.infRec.Baselines := pv[2:len(pv)];
  }

#
# Find Taper
#
  if (isDZB){
    p := nfrakwd(rtn, 'DZBReadout.Taper');
    if (p.error == 0){
      rtn.infRec.IFTaper := p.value;
    } else if (p.error == 3){
      msg := 'WARNING - ';
      msg := spaste(msg, rtn.tabRec.name, ' ');
      msg := spaste(msg, 'kwd \'DZBReadout.Taper\' not found, value set to \'Unknown\'.');
      print msg;
      rtn.infRec.IFTaper := 'Unknown';
    } else {
      rtn.error := 14;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.IFTaper := 'off';
  }

#
# Find multibeam info
#
  if (isDZB){
    p := nfrakwd(rtn, 'PW1.MultiBeam');
    if (p.error == 0){
      rtn.infRec.MultiBeamFlag := as_integer(p.value) > 0;
    } else if (p.error == 3){
      rtn.infRec.MultiBeamFlag := F;
    } else {
      rtn.error := 15;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.MultiBeamFlag := F;
  }

#
# Find phase switch mode
#
  if (isDZB){
    p := nfrakwd(rtn, 'DZB20-COR.PhaseSwitchPattern');
    if (p.error == 0){
      rtn.infRec.PhaseSwitchMode := p.value;
    } else if (p.error == 3){
      msg := 'WARNING - ';
      msg := spaste(msg, rtn.tabRec.name, ' ');
      msg := spaste(msg, 'kwd \'DZB20-COR.PhaseSwitchPattern\' not found, value set to \'unknown\'.');
      print msg;
      rtn.infRec.PhaseSwitchMode := 'Unknown';
    } else {
      rtn.error := 16;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.PhaseSwitchMode := 'NO';
  }

#
# Find number of rows in MAIN table
#
  rtn.infRec.NRows := rtn.tabRec.main.nrows();

#
# Get Time info
#
  rtn.infRec.TIME := '>> ------------------------------------------------------';

#
# Interval is used only to calculate real start/stop time and duration.
#
  p := rtn.tabRec.main.getcol('INTERVAL');
  if (is_fail(p)){
    rtn.error := 17;
    rtn.errstr := spaste('Cannot read column: \'MAIN.INTERVAL\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  tmpInt := max(p);

#
# Find start/stop date/time
#
  p := rtn.tabRec.main.getcol('TIME_CENTROID');
  if (is_fail(p)){
    rtn.error := 18;
    rtn.errstr := spaste('Cannot read column: \'MAIN.TIME_CENTROID\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  ps := sort(p);
  if (len(p) != len(ps)){
    rtn.error := 33;
    rtn.errstr := spaste('Cannot sort column: \'MAIN.TIME_CENTROID\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  l := shape(ps);

  rtn.infRec.DateStart := dq.time(dq.quantity(ps[1]-tmpInt/2, 's'), prec = 6, form="ymd no_time")
  rtn.infRec.TimeStart := dq.time(dq.quantity(ps[1]-tmpInt/2, 's'), prec = 6, form='hms')
  rtn.infRec.DateEnd := dq.time(dq.quantity(ps[l]+tmpInt/2, 's'), prec = 6, form="ymd no_time")
  rtn.infRec.TimeEnd := dq.time(dq.quantity(ps[l]+tmpInt/2, 's'), prec = 6, form='hms')

#
# Find total duration of rtn
#
  rtn.infRec.Duration := ps[l] - ps[1] + tmpInt;

#
# Find exposure time
#
  p := rtn.tabRec.main.getcol('EXPOSURE');
  if (is_fail(p)){
    rtn.error := 19;
    rtn.errstr := spaste('Cannot read column: \'MAIN.EXPOSURE\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  rtn.infRec.ExpTime := max(p);

#
# Get frequency information
#
  rtn.infRec.FREQ := '>> ------------------------------------------------------';

#
# Find number of Freq bands
#
  rtn.infRec.IFBands := rtn.tabRec.spw.nrows();

#
# Find ref. frequencies in MHz
#
  p := rtn.tabRec.spw.getcol('REF_FREQUENCY');
  if (is_fail(p)){
    rtn.error := 20;
    rtn.errstr := spaste('Cannot read column: \'SPECTRAL_WINDOW.REF_FREQUENCY\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  rtn.infRec.IFFreqs := p/1000000.0;

#
# Find number of channels
#
  p := rtn.tabRec.spw.getcol('NUM_CHAN');
  if (is_fail(p)){
    rtn.error := 21;
    rtn.errstr := spaste('Cannot read column: \'SPECTRAL_WINDOW.NUM_CHAN\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  rtn.infRec.IFNChan := unique(p);

#
# Find channel widths
#
  p := rtn.tabRec.spw.getcol('CHAN_WIDTH');
  if (is_fail(p)){
    rtn.error := 22;
    rtn.errstr := spaste('Cannot read column: \'SPECTRAL_WINDOW.CHAN_WIDTH\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  up := unique(p);
  rtn.infRec.IFChanWidth := up/1000.0;

#
# Get info on freq. mosaicing
#
  if (isDZB){
    p := nfrakwd(rtn, 'FW1.Positions');
    if (p.error == 0){
      rtn.infRec.FreqMosFlag := as_integer(p.value) > 1;
      v := as_integer(p.value);
      if (v == 0){
#
# Some line measurements has FW1.position == 0.
# This is an error, HvSG has repaired it.
# Here, we force the value to 1.
#
	v := 1;
      }
      rtn.infRec.FreqMosPoints := v;
    } else if (p.error == 3){
      rtn.infRec.FreqMosFlag := F;
      rtn.infRec.FreqMosPoints := 1;
    } else {
      rtn.error := 23;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.FreqMosFlag := F;
    rtn.infRec.FreqMosPoints := 1;
  }

#
# Find info on Freq. dwell time
#
  if (rtn.infRec.FreqMosFlag){
    p := nfrakwd(rtn, 'FW1.DwellTime');
    if (p.error == 0){
      p1 := split(p.value)[1];
      rtn.infRec.FreqMosDwellTime := as_integer(p1);
    } else if (p.error == 3){
      rtn.infRec.FreqMosDwellTime := 0;
    } else {
      rtn.error := 24;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.FreqMosDwellTime := 0;
  }

#
# Find info on MFFE band
#
  p := nfrakwd(rtn, 'WSRT-IF.MFFEBand');
  if (p.error == 0){
    rtn.infRec.MFFEBand := p.value;
  } else if (p.error == 3){
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'kwd \'WSRT-IF.MFFEBand\' not found, value set to \'Unknown\'.');
    print msg;
    rtn.infRec.MFFEBand := 'Unknown';
  } else {
    rtn.error := 25;
    rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }

#
# Find total bandwidth
#
  p := rtn.tabRec.spw.getcol('TOTAL_BANDWIDTH');
  if (is_fail(p)){
    rtn.error := 26;
    rtn.errstr := spaste('Cannot read column: \'SPECTRAL_WINDOW.TOTAL_BANDWIDTH\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  up := unique(p);
  rtn.infRec.IFBandWidth := up/1000000.0

#
# polarization information
#
  rtn.infRec.POL := '>> -------------------------------------------------------'

  p := rtn.tabRec.main.getcell('DATA', 1);
  if (is_fail(p)){
    rtn.error := 27;
    rtn.errstr := spaste('Cannot read cell: \'MAIN.DATA[1]\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  rtn.infRec.NPols := shape(p)[1];

  poltmp := ['XX', 'XY', 'YX', 'YY'];
  p := rtn.tabRec.pol.getcol('CORR_TYPE');
  if (is_fail(p)){
    rtn.error := 28;
    rtn.errstr := spaste('Cannot read column: \'POLARIZATION.CORR_TYPE\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  
  if (len(shape(p)) == 2){
    rtn.infRec.PolsUsed := poltmp[p[,1]-8];
  } else {
    msg := 'WARNING - ';
    msg := spaste(msg, rtn.tabRec.name, ' ');
    msg := spaste(msg, 'len(shape(PolColumn)) != 2.');
    print msg;
    rtn.infRec.PolsUsed := poltmp[p-8];
  }

#
# Field information
#
  rtn.infRec.FIELD := '>> -----------------------------------------------------'

#
# Find RA, DEC
#
  p := rtn.tabRec.fld.getcol('REFERENCE_DIR');
  if (is_fail(p)){
    rtn.error := 29;
    rtn.errstr := spaste('Cannot read column: \'REFERENCE_DIR\'.');
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }
  pra := p[1,,] * RAD2DEG;
  pdec := p[2,,] * RAD2DEG;
#
# If mosaicing - take the centroid
#
  sp := shape(p);
  PosMos := sp[3] != 1;
  if (PosMos){
    pma := max(pra);
    pmi := min(pra);
    if ((pmi - pma) > 180){
      pav := (pmi+pma)/2 - 180.0;
      if (pav < 0) pav := pav + 360.0;
    } else {
      pav := (pmi+pma)/2;
    }
    rtn.infRec.RaRef := pav;
    rtn.infRec.DecRef := (max(pdec) + min(pdec)) / 2.0;
  } else {
    rtn.infRec.RaRef := pra;
    rtn.infRec.DecRef := pdec;
  }
  if (rtn.infRec.RaRef < 0) rtn.infRec.RaRef := rtn.infRec.RaRef + 360;

#
# Find epoch
# Use either PW1.Reference or PW1.Epoch
#
  p := nfrakwd(rtn, 'PW1.Reference');
  if (p.error == 0){
    rtn.infRec.EpochRef := p.value;
  } else if (p.error == 3){
    p := nfrakwd(rtn, 'PW1.Epoch');
    if (p.error == 0){
      rtn.infRec.EpochRef := p.value;
    } else if (p.error == 3){
      msg := 'WARNING - ';
      msg := spaste(msg, rtn.tabRec.name, ' ');
      msg := spaste(msg, 'kwd \'PW1.Reference\' or \'PW1.Epoch\' not found, value set to \'Unknown\'.');
      print msg;
      rtn.infRec.EpochRef := 'Unknown';
    } else {
      rtn.error := 30;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.error := 31;
    rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
    rtn.infRec := [=];
    if (DeleteTabRec) rtn := closetables(rtn);
    return rtn;
  }

#
# Position mosaicing
#
  rtn.infRec.PosMosFlag := PosMos;
  rtn.infRec.NPosMosPoints := rtn.tabRec.fld.nrows();

#
# Find Position mosaic dwell time
#
  if (PosMos){
    p := nfrakwd(rtn, 'PW1.DwellTime');
    if (p.error == 0){
      p1 := split(p.value)[1];
      p2 := split(p1, ',');
      p3 := sort(unique(p2));
      rtn.infRec.PosMosDwellTime := as_integer(p3);
    } else if (p.error == 3){
      msg := 'WARNING - ';
      msg := spaste(msg, rtn.tabRec.name, ' ');
      msg := spaste(msg, 'kwd \'PW1.DwellTime\' not found, value set to \'Unknown\'.');
      print msg;
      rtn.infRec.PosMosDwellTime := 'Unknown';
    } else {
      rtn.error := 32;
      rtn.errstr := spaste(p._ID, ':', p.error, ':', p.errstr);
      rtn.infRec := [=];
      if (DeleteTabRec) rtn := closetables(rtn);
      return rtn;
    }
  } else {
    rtn.infRec.PosMosDwellTime := 0;
  }

  wdate := split(rtn.infRec.DateStart, '/');
  y := as_integer(wdate[1]);
  m := as_integer(wdate[2]);
  d := as_integer(wdate[3]);
  wtime := split(rtn.infRec.TimeStart, ':');
  hr := as_integer(wtime[1]);
  mt := as_integer(wtime[2]);
  sc := as_double(wtime[3]);
  ra := rtn.infRec.RaRef;
  rtn.infRec.HAStart := WSRTHA(y, m, d, hr, mt, sc, ra);

  wdate := split(rtn.infRec.DateEnd, '/');
  y := as_integer(wdate[1]);
  m := as_integer(wdate[2]);
  d := as_integer(wdate[3]);
  wtime := split(rtn.infRec.TimeEnd, ':');
  hr := as_integer(wtime[1]);
  mt := as_integer(wtime[2]);
  sc := as_double(wtime[3]);
  rtn.infRec.HAEnd := WSRTHA(y, m, d, hr, mt, sc, ra);

  if (DeleteTabRec) rtn := closetables(rtn);

  return rtn;
}


#
#==============================================================================
# showinfoRec - put info on MS to standard output
#
_mustShow := function(kwd)
{
  if (kwd == 'DName') return F;
  else if (kwd == 'SubArray') return F;
  else if (kwd == 'NrOfSets') return F;
  return T;
}
showinforec := function(MS = 'help')
{
#
# check for help
#
  if (is_string(MS)){
    if (MS == 'help'){
      showhelp(MSihelp);
      return T;
    }
  }

  r := inforec(MS);
  if (r.error != 0){
    msg := spaste('ERROR - ', r._ID, ' - ', r.error, ' - ', r.errstr);
    print msg;
    return F;
  }

  print '----------------------------------------------------------------------';
  if (is_string(MS)) print 'INFO on MS=', MS;
  
  nl := ' ';
  names := field_names(r.infRec);
  for (i in [1:len(r.infRec)]){
    if (_mustShow(names[i])){
      if (split(r.infRec[i])[1] != '>>'){
        v := r.infRec[i];
        if (len(v) > 1){
          msg0 := as_string(v[1]);
          for (j in [2:len(v)]){
            msg0 := spaste(msg0, nl, as_string(v[j]));
          }
          msg := sprintf("%17s = %s\n",  names[i], msg0);
        } else {
          msg := sprintf("%17s = %s\n",  names[i], as_string(r.infRec[i]));
        }
        print msg;
      }
    }
  }


  return T;
}

if (len(argv) > 1){
#  print 'DEBUG - start', argv[2];
  showinforec(argv[2]);
} else {
  print 'Need MS name';
}
exit(0);
