# glish script to simulate LOFAR with any number of antennae
# at the location of WSRT, locations and diameters from file LOFAR_posn_diam.txt
# the file can generate MS for a range of frequencies
# call the script from the directory where the files should be created

# The main input parameters
# Phase center & observing date
RA0          := '7h0m00.0';
DEC0         := '50d00m00s';
epoch0       := '2000/01/01';

# Frequency and BW
Frequency    := [15, 75, 120, 240] #Central frequency in MHz
Freq_unit    := 'MHz'
BW_fraction  := 15  # BW = Freq/BW_fraction
n_chan       := 32
BW_unit      := Freq_unit

# Number of stations
NN	     := 36

# Time settings for the observations
t_int	     := '20s'# integration time per scan (NB this is a string!)
t_obs        := 2400  # total observing time in seconds

# Goalname for file
goalname    := 'SPAML'

#*********************************************************************************
# Nothing needs to be changed below this line
#*********************************************************************************
# Where the MS goes
dirname := shell('pwd')
holderdir := spaste(dirname,'/')
basename     := 'LO'

# Start and end time
# NB: source goes through the meridian half-way through the obs-time.
# This should be adjusted if low-elevation fields are simulated.
t_start      := -t_obs/2
t_end        := t_obs/2

# Read the LOFAR locations and station diameter factors from file
xx := []
yy := []
zz := []
diam_lba := []
diam_hba := []
nlines := 0

file := open ( "< /data1/bemmel/Timba/MSets/LOFAR_posn_diam.txt")
line := read ( file )

while(nlines < NN) {
	nlines +:= 1
	parts := split(line)
	xx[nlines] := as_double(parts[1])
	yy[nlines] := as_double(parts[2])
	zz[nlines] := as_double(parts[3])
	diam_lba[nlines] := as_double(parts[4])
	diam_hba[nlines] := as_double(parts[5])
	line := read(file)
}

# Derived settings
# Station diameter as per Ronald Nijboers station footprints
# For LBA:
stn_size := [85, 85, 65, 45, 45, 50] # station equivalent diameters for HBA and LBA
if ( Frequency == 15){Diameter := stn_size[1] * diam_lba}
if ( Frequency == 30){Diameter := stn_size[2] * diam_lba}
if ( Frequency == 45){Diameter := stn_size[3] * diam_lba}
if ( Frequency == 60){Diameter := stn_size[4] * diam_lba}
if ( Frequency == 75){Diameter := stn_size[5] * diam_lba}
# For HBA:
if ( Frequency == 120){Diameter := stn_size[6] * diam_hba}
if ( Frequency == 150){Diameter := stn_size[6] * diam_hba}
if ( Frequency == 180){Diameter := stn_size[6] * diam_hba}
if ( Frequency == 210){Diameter := stn_size[6] * diam_hba}
if ( Frequency == 240){Diameter := stn_size[6] * diam_hba}

#-----------------------------------------------------------------------
#

simms:=function(msname,clname,freq=Freq,noise='0.0Jy',dovp=F,setoffsets=F,
		      RA=RA0,Dec=DEC0)
{
    include 'newsimulator.g';

    simclname:= clname;
    simmsname:= spaste(holderdir,msname);
    
    
    note('Create the empty measurementset');
    
    mysim := newsimulator(msname);
    
    mysim.setspwindow(spwname=specname, freq=freq,
		      deltafreq=CW, freqresolution=CW, 
		      nchannels=n_chan, stokes='XX XY YX YY');
    
    note('Simulating LOFAR');
    posvla := dm.observatory('wsrt');

#
# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := NN
    diam := Diameter;
    mysim.setconfig(telescopename='wsrt', 
		    x=xx, y=yy, z=zz,
		    dishdiameter=diam, 
		    mount='alt-az', antname='LOFAR',
		    coordsystem='local', 
		    referencelocation=posvla);

    dir0    := dm.direction('j2000',  RA, Dec);
    mysim.setfield(sourcename='test_image', 
		   sourcedirection=dir0)

    ref_time := dm.epoch('iat', epoch0);
    mysim.settimes(integrationtime=t_int, usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

    starttime:=t_start;
    scanlength:=t_obs
    scan:=1;
    while(starttime<t_end) {
      mysim.observe('test_image', specname,
		    starttime=spaste(starttime, 's'),
		    stoptime=spaste(starttime+scanlength,'s'));
      dm.doframe(ref_time);
      dm.doframe(posvla);
      print "Scan", scan;
      hadec:=dm.direction('hadec', dq.time(spaste(starttime+scanlength/2,'s')),
			  DEC0);
      print 'HADec: ', dm.dirshow(hadec);
      azel:=dm.measure(hadec,'azel');
      print 'AzEl:  ', dm.dirshow(azel);
      mysim.setdata(msselect=spaste('SCAN_NUMBER==',scan-1));
      mysim.predict(complist=simclname);
      starttime+:=scanlength;
      scan+:=1;
    }

    if (noise != '0.0Jy')
    {
 	mysim.setnoise(mode='simplenoise', simplenoise=noise);
 	mysim.corrupt();
    }

    mysim.done();
}

# to do a run ...

nfreq := len(Frequency)
msi := 0

while ( msi < nfreq){
	msi +:= 1
	# Frequency
	ifreq := Frequency[msi]
	BW_digit     := ifreq/BW_fraction
	Freq_digit   := ifreq-BW_digit/2;
	Freq         := spaste(Freq_digit,Freq_unit);
	# Some derived names
	specname     := spaste(basename,NN)
	BW	     := spaste(BW_digit,BW_unit);
	# Per channel frequency width
	CW_digit := BW_digit/n_chan
	CW       := spaste(CW_digit,BW_unit)

	print '****************************************************'
	print 'Starting frequency = ',Freq
	print 'Central frequency = ', ifreq
	print 'Total bandwidth = ',BW
	print 'Channel incremenet = ',CW
	print '****************************************************'

	msoutname    := spaste(specname,"_",goalname,"_",ifreq,"_",BW,"_",t_obs,"_",t_int,".MS")

	# first delete old MS, test images, etc
	print '*** deleting previous stuff ***'
	comm :=spaste('rm -rf ',msoutname)
	shell(comm)
	print '*** calling simms ***'
	simms(msoutname,'/data1/bemmel/Timba/MSets/newmodel.cl');
	print 'Writen new MS named ',msoutname,' in ',holderdir
}

exit

