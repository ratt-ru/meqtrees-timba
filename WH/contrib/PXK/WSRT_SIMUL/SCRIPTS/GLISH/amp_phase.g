#! /bin/bash -f
# glish/aips++ script to check the data
# CREATION: 2006.10.06
# system.output.log := "./lala.txt"

pragma include once


function sub_table(ms='', type='NAME', grep='', pattern=0){
    c1      := paste(' SELECT FROM ', ms , sep='')

    # select by 'type' and search for pattern
    if (pattern == 1){
	grep:= paste('', grep, '', sep='"')   # grep -> "grep"
	c2  := paste(c1, ' WHERE ', type, ' == PATTERN(', sep='')
	c3  := paste(c2, grep, ')', sep='')
    } else {
    # select by 'type' and search for integer
	c3  := paste(c1, ' WHERE ', type, ' == ', as_integer(grep), sep='')
    }
    t       := tablecommand(c3)
    print "Shape of subtable: ", shape(t)
    return t
}





function show_amp_phase(MS, BL1=0, BL2=2, chan=1, stokes="I"){
    include 'table.g'
    include 'pgplotter.g'

    # Get the data
    t       := table(MS)                   #t.browse()
    data    := t.getcol('CORRECTED_DATA')
    print "pols, chans, rows:",shape(data) # pols, chans, rows=t-slots*bl
    ant1    := t.getcol('ANTENNA1')        # zero-based!
    ant2    := t.getcol('ANTENNA2')
    thetime := t.getcol('TIME')
    thetime := thetime - thetime[1]        # subtracted offset


    # get size of arrays (number of timesteps)
    t_steps := 0
    for (i in 1:shape(data)[3])
	{if (ant1[i]==BL1 & ant2[i]==BL2) {t_steps := t_steps + 1}}
    print ""
    print "t_steps..........: ", t_steps

    # fill STOKES / TIME
    STOKES   := array(0.0, t_steps)
    AMP      := array(0.0, t_steps)
    PHI      := array(0.0, t_steps)
    REAL     := array(0.0, t_steps)
    IMAG     := array(0.0, t_steps)
    TIME     := array(0.0, t_steps)
    t        := 1
    for (bl in 1:shape(data)[3]){
	if (ant1[bl]==BL1 & ant2[bl]==BL2){       # take right baseline
	    if (stokes=="I") 
		STOKES[t] := (data[1,chan,bl] + data[4,chan,bl]) / 2.0
	    if (stokes=="Q") 
		STOKES[t] := (data[1,chan,bl] - data[4,chan,bl]) / 2.0
	    if (stokes=="U") 
		STOKES[t] := (data[2,chan,bl] + data[3,chan,bl]) / 2.0
	    if (stokes=="V") 
		STOKES[t] := (data[2,chan,bl] - data[3,chan,bl]) / 2.0
	    fi
	    AMP     [t] := abs (STOKES[t])
	    PHI     [t] := arg (STOKES[t])
	    REAL    [t] := real(STOKES[t])
	    IMAG    [t] := imag(STOKES[t])
	    TIME    [t] := thetime[bl]
	    if (imag(STOKES[t])==0) {PHI[t] := 0} # check for absent phase
	    t           := t + 1
	}
    }

    # Plot the data
    Title := paste(MS, " BL:", BL1, "-", BL2, " chan:", chan, 
		    " Stokes: ", stokes, sep=' ')
    plot_amp_phase(TIME, AMP, PHI, REAL, IMAG, Title)
}


func plot_amp_phase(TIME, AMP, PHI, REAL, IMAG, Title){

    print "TIME.[1,2,3].....: ", TIME[1], TIME[2], TIME[3]
    print "AMP..[1,2,3].....: ",  AMP[1],  AMP[2],  AMP[3]
    print "PHASE[1,2,3].....: ",  PHI[1],  PHI[2],  PHI[3]
    print "REAL.[1,2,3].....: ", REAL[1], REAL[2], REAL[3]
    print "IMAG.[1,2,3].....: ", IMAG[1], IMAG[2], IMAG[3]

    # check 'empty' arrays (all zeroes)
    plot_tolerance := 0.0001
    if (max(AMP)-min(AMP)<plot_tolerance) 
	    {min_amp := min(AMP)-1; max_amp := max(AMP)+1;}
    else    {min_amp := min(AMP);   max_amp := max(AMP);  }
    if (max(PHI)-min(PHI)<plot_tolerance) 
	    {min_phi := min(PHI)-1; max_phi := max(PHI)+1;}
    else    {min_phi := min(PHI);   max_phi := max(PHI);  }
    if (max(REAL)-min(REAL)<plot_tolerance) 
	    {min_rea := min(REAL)-1; max_rea := max(REAL)+1;}
    else    {min_rea := min(REAL);   max_rea := max(REAL);  }
    if (max(IMAG)-min(IMAG)<plot_tolerance) 
	    {min_ima := min(IMAG)-1; max_ima := max(IMAG)+1;}
    else    {min_ima := min(IMAG);   max_ima := max(IMAG);  }

    print "AMP [min,max]....:", min_amp, max_amp
    print "PHI [min,max]....:", min_phi, max_phi
    print "REAL[min,max]....:", min_rea, max_rea
    print "IMAG[min,max]....:", min_ima, max_ima
    print ""

    pg := pgplotter(size=[60,700])

    pg.subp(2,2)

    # Plot AMP vs TIME                # square, axis [-2 -> 2, 20, 20, 30]
    pg.sci(1); pg.env(min(TIME),max(TIME),min_amp,max_amp,0,0) 
    pg.sci(2); pg.line(TIME,AMP)      # [2=red, 3=green, 4=blue]
    # pg.setyscale(min(AMP), max(AMP))
    pg.lab('TIME (sec)','AMP (Jy)',Title)


    # Plot PHASE vs TIME
    pg.sci(1); pg.env(min(TIME),max(TIME),min_phi,max_phi,0,0) 
    pg.sci(3); pg.line(TIME,PHI)
    pg.lab('TIME (sec)','PHASE (rad)','')

    # Plot REAL vs TIME
    pg.sci(1); pg.env(min(TIME),max(TIME),min_rea,max_rea,0,0) 
    pg.sci(7); pg.line(TIME,REAL)
    pg.lab('TIME (sec)','REAL (Jy)','')

    # Plot IMAG vs TIME
    pg.sci(1); pg.env(min(TIME),max(TIME),min_ima,max_ima,0,0) 
    pg.sci(5); pg.line(TIME,IMAG)
    pg.lab('TIME (sec)','IMAG (Jy)','')
    #pg.ptxt(500,0.5,0,0,'Runaway sinusoid 3^4 \delta')
}









## MAIN PROGRAM ###################################################
if (len(argv)<=2){
    print "";
    print "glish amp_phase.g file"
    print "...... bl1=0, bl2=2, chan=1, stokes=I";
    print ""
    exit
} else {

    # Get Input
    MS := argv[3]
    L  := len(argv)
    if (L>=4) {BL1      := as_integer(argv[4]) } else {BL1      := 0}
    if (L>=5) {BL2      := as_integer(argv[5]) } else {BL2      := 2}
    if (L>=6) {chan     := as_integer(argv[6]) } else {chan     := 1}
    if (L>=7) {stokes   :=            argv[7]  } else {stokes   := "I"}
    
    print ""
    print "#########################################################"
    print "# MS:.....: ", MS
    print "# BL1.....: ", BL1
    print "# BL2.....: ", BL2
    print "# chan....: ", chan
    print "# Stokes..: ", stokes
    print "#########################################################"
    print ""
    
    # Show AMP / PHASE
    show_amp_phase(MS, BL1, BL2, chan, stokes);
}

