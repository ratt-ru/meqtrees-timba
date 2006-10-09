#!/usr/bin/python

# Updates various nodes in the tree based on the visibility
# header. Uses the naming convetion from Contrib.OMS

from Timba.meqkernel import set_state

def process_vis_header (hdr):
    """handler for the visheader""";
    # phase center
    (ra0,dec0) = hdr.phase_ref;
    print '[ReadVisHeader] phase centre: ',ra0,dec0;
    try:
      set_state('ra',value=ra0);
      set_state('dec',value=dec0);
    except: pass;
    # antenna positions
    pos = hdr.antenna_pos;
    if pos.rank != 2 or pos.shape[0] != 3:
        raise ValueError,'incorrectly shaped antenna_pos';
    nant = pos.shape[1];
    coords = ('x','y','z');
    for iant in range(nant):
        sn = str(iant+1);
        # since some antennas may be missing from the tree,
        # ignore errors
        try:
            for (j,label) in enumerate(coords):
                print '[ReadVisHeader] ',label+':'+sn, 'value = ',pos[j,iant]
                set_state(label+':'+sn,value=pos[j,iant]);
        except: pass;
    # array reference position
    try:
      for (j,label) in enumerate(coords):
        set_state(label+'0',value=pos[j,0]);
    except: pass;
    # time extent
    (t0,t1) = hdr.time_extent;
    print '[ReadVisHeader] time extent: ',t0,t1;
    try:
      set_state('time0',value=t0);
      set_state('time1',value=t1);
    except: pass;
    # freq range
    f0,f1 = hdr.channel_freq[0],hdr.channel_freq[-1];
    print '[ReadVisHeader] freq range: ',f0,f1;
    try:
      set_state('freq0',value=f0);
      set_state('freq1',value=f1);
    except: pass;
    
