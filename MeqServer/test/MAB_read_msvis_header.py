#!/usr/bin/python

from Timba.meqkernel import set_state


def process_vis_header (hdr):
    """handler for the visheader""";
    # phase center
    (ra0,dec0) = hdr.phase_ref;
    set_state('ra0',value=ra0);
    set_state('dec0',value=dec0);
    # antenna positions
    pos = hdr.antenna_pos;
    if pos.rank != 2 or pos.shape[0] != 3:
        raise ValueError,'incorrectly shaped antenna_pos';
    nant = pos.shape[1];
    coords = ('x','y','z');
    for iant in range(14):  # range(nant), temporary hack
        sn = str(iant+1);
        # since some antennas may be missing from the tree,
        # ignore errors
        try:
            for (j,label) in enumerate(coords):
                print label+':'+sn, 'value = ',pos[j,iant]
                set_state(label+':'+sn,value=pos[j,iant]);
        except: pass;
    # array reference position
    #for (j,label) in enumerate(coords):
    #  set_state(label+'0',value=pos[j,0]);
    print 'END OF READ_MSVIS_HEADER'
