#import sys
#sys.path.insert(0,'')

from Timba.TDL import *
from Timba.Meq import meq
import math
from Meow import Context
from math import *

HH = 400000;           # height of ionospheric layer, in meters
# Earth minor axis
WGS_b = 6356752.314245
# Earth major axix
WGS_a = 6378137
# Earth eccentricity
WGS_e = sqrt(1-WGS_b*WGS_b/(WGS_a*WGS_a))
# Earth secondary eccentricity
WGS_ep = WGS_e*WGS_a/WGS_b
# Hardcoded coordinates for VLA origin
lamb = -1.8782943
phi = 0.59478397
# Reference antenna for the ENU coordinate system
refant = 1

#***************Conversion routines*******************************
def ecef_2_enu (ppscope, src, s, ref):
    """ Calculate ENU coordinates from ECEF"""
    # Rot matrix voor referentie_station
    sinl = ppscope.sinl(ref)
    cosl = ppscope.cosl(ref)
    sinphi = ppscope.sinphi(ref)
    cosphi = ppscope.cosphi(ref)
    if not (ppscope.inv_rot_matrix(ref)).initialized():
        ppscope.inv_rot_matrix(ref) << Meq.Composer(-1*sinl,cosl,0,
                                               -1*sinphi*cosl,-1*sinphi*sinl,cosphi,
                                               cosphi*cosl,cosphi*sinl,sinphi,
                                               dims=[3,3]);

    if src < 0: # convert only the array
        ppscope.array_enu(s) << Meq.MatrixMultiply(ppscope.inv_rot_matrix(ref),
                                                   Context.array.xyz(s) - Context.array.xyz(ref))
        ppscope.array_x_enu(s) << Meq.Selector(ppscope.array_enu(s), index=0)
        ppscope.array_y_enu(s) << Meq.Selector(ppscope.array_enu(s), index=1)

    if src >= 0: # convert the pierce points
        ppscope.pp_enu(src.name,s) << Meq.MatrixMultiply(ppscope.inv_rot_matrix(ref),
                                                    ppscope.pp_ecef(src.name,s) - Context.array.xyz(ref))
        ppscope.pp_x_enu(src.name,s) << Meq.Selector(ppscope.pp_enu(src.name,s), index=0)
        ppscope.pp_y_enu(src.name,s) << Meq.Selector(ppscope.pp_enu(src.name,s), index=1)
            
#**************************Rotation matrix and other helper routines************************
def make_rot_matrix (ppscope):
    """ Construct the rotation matrix to convert ENU to ECEF coordinates"""
    # longitude is RH around Z, latitude is positive from equator to north-pole
    stations = Context.array.stations();
    xyz = Context.array.xyz(); # station coordinates in ECEF

    for s in stations:
        array_llh = ppscope.array_llh(s) << Meq.LongLat(xyz(s), use_w=1)
        lamb = ppscope.lamb(s) << Meq.Selector(array_llh, index=0)
        phi = ppscope.phi(s) << Meq.Selector(array_llh, index=1)
        cosl= ppscope.cosl(s) << Meq.Cos(ppscope.lamb(s));
        sinl= ppscope.sinl(s) << Meq.Sin(ppscope.lamb(s));
        cosphi= ppscope.cosphi(s) << Meq.Cos(ppscope.phi(s));
        sinphi= ppscope.sinphi(s) << Meq.Sin(ppscope.phi(s));
        # rotation matrix ENU to ECEF, this is done PER STATION!
        ppscope.rot_matrix_station(s) << Meq.Composer(
            -sinl, -sinphi*cosl,cosl*cosphi,
            cosl, -sinphi*sinl,cosphi*sinl,
            0,cosphi,sinphi,dims=[3,3])
        # Get the enu coordinates for the array
        array_enu = ecef_2_enu(ppscope, -1, s, ref=refant)

def get_radius (ppscope, lat):
    """Calculate the earth radius at a given latitude, assuming the WGS84 ellipsoid"""
    # Latitude is POSITIVE from equator towards north-pole, in radians
    earth_radius = WGS_b / Meq.Sqrt(1-WGS_e*WGS_e*Meq.Sqr(Meq.Cos(lat)))
    return earth_radius

#*******************Main routine to calculate pp coordinates**********************************
def compute_pierce_points (ppscope, source_list):
    """Solve for the length of the vector from station to pierce point assuming a spherical
    earth and calculate the pierce point coordinates in ENU per station"""
    # Get basic info from Meow
    stations = Context.array.stations();
    xyz = Context.array.xyz();
    matrix = make_rot_matrix(ppscope);
    for src in source_list:
        # get radec for each source
        radec = src.direction.radec()
        for s in stations:
            # get AzEl for each source and for each station, do these have to be nodes?
            ppscope.azel(src.name,s) << Meq.AzEl(radec,xyz(s));
            ppscope.az(src.name,s) << Meq.Selector(ppscope.azel(src.name,s), index=0)
            ppscope.el(src.name,s) << Meq.Selector(ppscope.azel(src.name,s), index=1)
            #
            # Get the radius for WGS84 earth
            R_s=get_radius(ppscope,ppscope.phi(s))
            #
            # Get the length of the vector from antenna to pierce point.
            # ERROR: I make an assumption here which gives rise to an error in ppscope.length
            # I assume that the earth radius in the direction of the pierce point is
            # approximately the same as the earth radius towards the station. 
            ppscope.length(src.name,s) << -1.0*R_s*Meq.Sin(ppscope.el(src.name,s)) + Meq.Sqrt(
                R_s*R_s*Meq.Sqr(Meq.Sin(ppscope.el(src.name,s)))+2*R_s*HH+HH*HH
                );
            #now that we have az, el and length, we can transform this to ENU wrt observing antenna
            # NB: the ENU sub-system here has the origin at the antenna which the pp relates to
            ppscope.z_sub(src.name,s) << ppscope.length(src.name,s) * Meq.Sin(ppscope.el(src.name,s))
            ppscope.xy_length(src.name,s) << Meq.Sqrt(Meq.Sqr(ppscope.length(src.name,s)) - Meq.Sqr(ppscope.z_sub(src.name,s)))
            ppscope.x_sub(src.name,s) << Meq.Sin(ppscope.az(src.name,s))*ppscope.xy_length(src.name,s)
            ppscope.y_sub(src.name,s) << Meq.Cos(ppscope.az(src.name,s))*ppscope.xy_length(src.name,s)
            ppscope.pp_sub(src.name,s) << Meq.Composer(ppscope.x_sub(src.name,s),ppscope.y_sub(src.name,s),ppscope.z_sub(src.name,s))

            #multiply ppscope.enu with rot_matrix to get ECEF coordinates of pierce point
            ppscope.pp_ecef(src.name,s) << Meq.MatrixMultiply(ppscope.rot_matrix_station(s),ppscope.pp_sub(src.name,s))+xyz(s)

            # From here it is basically a bunch of coordinate conversions            
            # Meq.LongLat converts ECEF into longitude latitude, this is only needed for plotting
            # and doesn't work with tilesizes > 1. For speed leave it out.
            #ppscope.pp_ll(src.name,s) << Meq.LongLat(ppscope.pp_ecef(src.name,s), use_w=1)
            #ppscope.pp_long(src.name,s) << Meq.Selector(ppscope.pp_ll(src.name,s), index=0)
            #ppscope.pp_lat(src.name,s) << Meq.Selector(ppscope.pp_ll(src.name,s), index=1)
            # Rotate the long-lat into ENU with respect to reference antenna
            pp_enu = ecef_2_enu(ppscope,src,s,ref=refant)
    compress_nodes(ppscope,source_list)
    return ppscope

def compress_nodes(ppscope,source_list):
    """Combine the nodes for the pierce points and array into nodelists for plotting"""
    # For the pp first combine per source
    stations = Context.array.stations();
    for s in stations:
#        ppscope.pp_long_stat(s) << Meq.Composer(dims=[0], *[ppscope.pp_long(src.name,s)*180/math.pi for src in source_list])
#        ppscope.pp_lat_stat(s) << Meq.Composer(dims=[0], *[ppscope.pp_lat(src.name,s)*180/math.pi for src in source_list])

        ppscope.pp_east_stat(s) << Meq.Composer(dims=[0], *[ppscope.pp_x_enu(src.name,s) for src in source_list])
        ppscope.pp_north_stat(s) << Meq.Composer(dims=[0], *[ppscope.pp_y_enu(src.name,s) for src in source_list])
    # Combine everything for all stations
    # First the pierce points
    #ppscope.pp_long << Meq.Composer(dims=[0], *[ppscope.pp_long_stat(s) for s in stations]) 
    #ppscope.pp_lat << Meq.Composer(dims=[0], *[ppscope.pp_lat_stat(s) for s in stations])

    ppscope.pp_east << Meq.Composer(dims=[0], *[ppscope.pp_east_stat(s) for s in stations])
    ppscope.pp_north << Meq.Composer(dims=[0], *[ppscope.pp_north_stat(s) for s in stations])

    # Then the array
    #ppscope.arr_long << Meq.Composer(dims=[0],*[ppscope.lamb(s)*180/math.pi for s in stations])
    #ppscope.arr_lat << Meq.Composer(dims=0,*[ppscope.phi(s)*180/math.pi for s in stations])

    ppscope.arr_east << Meq.Composer(dims=[0], *[ppscope.array_x_enu(s) for s in stations])
    ppscope.arr_north << Meq.Composer(dims=[0], *[ppscope.array_y_enu(s) for s in stations])


    
