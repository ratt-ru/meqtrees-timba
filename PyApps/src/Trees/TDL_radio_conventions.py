# file: TDL_radio_conventions.py

def station_key(station=0):
    """station key (record field name) used in in Joneset etc"""
    return str(station)                             # NB: key should ALWAYS be string!!

def station_index(station=0):
    """station index used in spigots/sinks"""
    return station

def ifr_key(station1=0, station2=0):
    """ifr key (record field name) used in in Cohset etc"""
    return str(station1)+'_'+str(station2)          # NB: key should ALWAYS be string!!



#----------------------------------------------------------------
# Some 'universal' plot styles:

def plot_color(key=None):
    rr = dict(XX='red', XY='magenta', YX='darkCyan', YY='blue')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False
    
def plot_style(key=None):
    rr = dict(XX='circle', XY='xcross', YX='xcross', YY='circle')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False

def plot_size(key=None):
    rr = dict(XX=8, XY=8, YX=8, YY=8)
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False

def plot_pen(key=None):
    rr = dict(XX=2, XY=2, YX=2, YY=2)
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False


# Plot style information
#	if (type=='color') {
#           ss := 'black';
#	    ss := [ss,"red blue darkGreen magenta"];
#	    ss := [ss,"darkGray darkMagenta darkRed darkYellow"];
#	    ss := [ss,"darkBlue darkCyan gray"];
#	    ss := [ss,"yellow lightGray cyan green"];
#	    # ss := [ss,"none white"];
#	} else if (type=='spectrum_color') {
#	    ss := "hippo grayscale brentjens";
#	} else if (type=='symbol') {
#	    ss := "circle rectangle square ellipse";
#	    ss := [ss, "xcross cross triangle diamond"];
#	    # ss := [ss,"none"];
#	} else if (type=='line_style') {
#	    ss := "dots lines steps stick";
#	    ss := [ss, "SolidLine DashLine DotLine DashDotLine DashDotDotLine"];
#	    ss := [ss, "solidline dashline dotline dashdotline dashdotdotline"];
#	    # ss := [ss,"none"];



#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of TDL_radio_conventions.py :\n'
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    
    if 0:
        # MG_JEN_exec.display_subtree(rr, 'rr', full=True, recurse=3)
        pass

    print '\n*******************\n** End of local test of TDL_radio_conventions.py :\n'

#============================================================================================


