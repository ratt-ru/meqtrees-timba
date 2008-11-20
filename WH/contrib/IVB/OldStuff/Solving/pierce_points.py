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

#***************Conversion routines*******************************
def ecef_2_enu (ppscope, X, Y, Z, src, s, ref):
    """ Calculate ENU coordinates from ECEF"""
    x_station = Context.array.x_station(); # station coordinates in ECEF
    y_station = Context.array.y_station(); # station coordinates in ECEF
    z_station = Context.array.z_station(); # station coordinates in ECEF
    if src < 0: # convert the array
        ppscope.dX(s) << X - x_station(ref)
        ppscope.dY(s) << Y - y_station(ref)
        ppscope.dZ(s) << Z - z_station(ref)
        # Hardcoded coordinates for VLA origin (to test results)
        lamb = -1.8782943
        phi = 0.59478397
        # Rotate
        ppscope.x_trans(s) << -ppscope.dX(s)*Meq.Sin(ppscope.lamb(ref)) + ppscope.dY(s)*Meq.Cos(ppscope.lamb(ref))
        ppscope.y_trans(s) << -ppscope.dX(s)*Meq.Sin(ppscope.phi(ref))*Meq.Cos(ppscope.lamb(ref)) - ppscope.dY(s)*Meq.Sin(ppscope.phi(ref))*Meq.Sin(ppscope.lamb(ref)) + ppscope.dZ(s)*Meq.Cos(ppscope.phi(ref));
        ppscope.z_trans(s) << ppscope.dX(s)*Meq.Cos(ppscope.phi(ref))*Meq.Cos(ppscope.lamb(ref)) + ppscope.dY(s)*Meq.Cos(ppscope.phi(ref))*Meq.Sin(ppscope.lamb(ref)) + ppscope.dZ(s)*Meq.Sin(ppscope.phi(ref));

    if src >= 0: # convert the pierce points
        ppscope.dX(src,s) << X - x_station(ref)
        ppscope.dY(src,s) << Y - y_station(ref)
        ppscope.dZ(src,s) << Z - z_station(ref)
        # Hardcoded coordinates for VLA origin
        lamb = -1.8782943
        phi = 0.59478397
        ppscope.x_trans(src,s) << -ppscope.dX(src,s)*math.sin(lamb) + ppscope.dY(src,s)*math.cos(lamb)
        ppscope.y_trans(src,s) << -ppscope.dX(src,s)*math.sin(phi)*math.cos(lamb) - ppscope.dY(src,s)*math.sin(phi)*math.sin(lamb) + ppscope.dZ(src,s)*math.cos(phi)
        ppscope.z_trans(src,s) << ppscope.dX(src,s)*math.cos(phi)*math.cos(lamb) + ppscope.dY(src,s)*math.cos(phi)*math.sin(lamb) + ppscope.dZ(src,s)*math.sin(phi);


def ecef_2_llh (ppscope, X, Y, Z, src, s):
    """ Calculate longitude and latitude for each pierce point"""
    # This routine uses the non-iterative method from Kaplan (see wikipedia)
    # It works OK for the VLA conversion in IDL.
    if src >= 0: # convert pierce points
        bigE = sqrt(WGS_a**2. - WGS_b**2.)
        # nodes (use MeqTree math)
        r = ppscope.r(src,s) << Meq.Sqrt(Meq.Sqr(X) + Meq.Sqr(Y));
        F = ppscope.F(src,s) << 54.0*WGS_b**2*Meq.Sqr(Z)
        G = ppscope.G(src,s) << Meq.Sqr(r) + (1-WGS_e**2)*Meq.Sqr(Z)- (WGS_e*bigE)**2
        C = ppscope.C(src,s) << WGS_e**4*F*Meq.Sqr(r)/Meq.Pow(G,3)
        S = ppscope.S(src,s) << Meq.Pow(1+C+Meq.Sqrt(Meq.Sqr(C)+2*C),1/3)
        P = ppscope.P(src,s) << F/(3*Meq.Sqr(S+1/S+1)*Meq.Sqr(G))
        Q = ppscope.Q(src,s) << Meq.Sqrt(1+2*WGS_e**4*P)
        r_0=ppscope.r0(src,s) << -P*WGS_e**2*r/(1+Q) + Meq.Sqrt(
            WGS_a**2*(1+1/Q)/2 - (P*(1-WGS_e**2)*Meq.Sqr(Z))/(Q*(1+Q)) - P*Meq.Sqr(r)/2
            )
        #U = ppscope.U(src,s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + Meq.Sqr(Z))
        V = ppscope.V(src,s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + (1-WGS_e**2)*Meq.Sqr(Z))
        Z_0 = ppscope.Z_0(src,s) << WGS_b**2*Z/(WGS_a*V)
        ppscope.phi(src,s) << (Meq.Atan((Z+WGS_ep**2*Z_0)/r))
        ppscope.lamb(src,s) << (Meq.Atan(Y/X) - math.pi)
        # ppscope.height(src,s) << U*(1-WGS_b*WGS_b/(WGS_a*V))
        # ppscope.pp(src,s) << Meq.Composer(ppscope.lamb(src,s),ppscope.phi(src,s))
    if src < 0 : # convert array
        bigE = sqrt(WGS_a**2. - WGS_b**2.)
        # nodes (use MeqTree math)
        r = ppscope.r(s) << Meq.Sqrt(Meq.Sqr(X) + Meq.Sqr(Y));
        F = ppscope.F(s) << 54.0*WGS_b**2*Meq.Sqr(Z)
        G = ppscope.G(s) << Meq.Sqr(r) + (1-WGS_e**2)*Meq.Sqr(Z)- (WGS_e*bigE)**2
        C = ppscope.C(s) << WGS_e**4*F*Meq.Sqr(r)/Meq.Pow(G,3)
        S = ppscope.S(s) << Meq.Pow(1+C+Meq.Sqrt(Meq.Sqr(C)+2*C),1/3)
        P = ppscope.P(s) << F/(3*Meq.Sqr(S+1/S+1)*Meq.Sqr(G))
        Q = ppscope.Q(s) << Meq.Sqrt(1+2*WGS_e**4*P)
        r_0=ppscope.r0(s) << -P*WGS_e**2*r/(1+Q) + Meq.Sqrt(
            WGS_a**2*(1+1/Q)/2 - (P*(1-WGS_e**2)*Meq.Sqr(Z))/(Q*(1+Q)) - P*Meq.Sqr(r)/2
            )
        #U = ppscope.U(s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + Meq.Sqr(Z))
        V = ppscope.V(s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + (1-WGS_e**2)*Meq.Sqr(Z))
        Z_0 = ppscope.Z_0(s) << WGS_b**2*Z/(WGS_a*V)
        ppscope.phi(s) << (Meq.Atan((Z+WGS_ep**2*Z_0)/r))
        ppscope.lamb(s) << (Meq.Atan(Y/X) - math.pi)
        # ppscope.height(s) << U*(1-WGS_b*WGS_b/(WGS_a*V))
            
#**************************Rotation matrix and other helper routines************************
def make_rot_matrix (ppscope):
    """ Construct the rotation matrix to convert ENU to ECEF coordinates for a all stations"""
    # longitude is RH around Z, latitude is positive from equator to north-pole
    # Could it be faster to do this in a single reference frame for a core station in case of LOFAR?
    # Then we would only have to de one rotation, rather than 77, but the pierce-points need to be
    # calculated in another reference frame as well.
    stations = Context.array.stations();
    x_station = Context.array.x_station(); # station coordinates in ECEF
    y_station = Context.array.y_station(); # station coordinates in ECEF
    z_station = Context.array.z_station(); # station coordinates in ECEF
    # Define first antenna of the array as reference antenna
    for s in stations:
        # longitude and latitude of the station (geocentric)
        array_llh = ecef_2_llh(ppscope, x_station(s), y_station(s), z_station(s), -1, s)
        # for the stations use a negative source number
        # rotation matrix ENU to ECEF, this is done PER STATION!
        ppscope.rot_matrix_station(s) << Meq.Composer(
            -Meq.Sin(ppscope.lamb(s)), -Meq.Sin(ppscope.phi(s))*Meq.Cos(ppscope.lamb(s)), Meq.Cos(ppscope.phi(s))*Meq.Cos(ppscope.lamb(s)),
            Meq.Cos(ppscope.lamb(s)), -Meq.Sin(ppscope.phi(s))*Meq.Sin(ppscope.lamb(s)), Meq.Cos(ppscope.phi(s))*Meq.Sin(ppscope.lamb(s)),
            0, Meq.Cos(ppscope.phi(s)), Meq.Sin(ppscope.phi(s)), dims=[3,3])
        # Get the enu coordinates for the array
        array_enu = ecef_2_enu(ppscope,x_station(s),y_station(s),z_station(s), -1, s, 1)
    ppscope.rot_matrix << Meq.Composer(*[ppscope.rot_matrix_station(s) for s in stations])

def get_radius (ppscope, lat):
    """Calculate the earth radius at a given latitude, assuming the WGS84 ellipsoid"""
    # Latitude is POSITIVE from equator towards north-pole, in radians
    earth_radius = WGS_b / Meq.Sqrt(1-WGS_e*WGS_e*Meq.Sqr(Meq.Cos(lat)))
    return earth_radius

#*******************Main routine to calculate pp coordinates**********************************
def compute_pierce_points (nodes, source_list):
    """Solve for the length of the vector from station to pierce point assuming a spherical
    earth and calculate the pierce point coordinates in ENU per station"""
    # Get basic info from Meow
    stations = Context.array.stations();
    xyz = Context.array.xyz();
    # maken eigen subscope met variabele ppscope en naam nodes('pp')
    ppscope = nodes('pp').Subscope();
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
            # Put the elevation and earth radius in the solution for the length
            # ERROR: I make an assumption here which gives rise to an error in ppscope.length
            # I assume that the earth radius in the direction of the pierce point is
            # approximately the same as the earth radius towards the station. 
            R_s=get_radius(ppscope,ppscope.phi(s))
            #
            ppscope.length(src.name,s) << -1.0*R_s*Meq.Sin(ppscope.el(src.name,s)) + Meq.Sqrt(
                R_s*R_s*Meq.Sqr(Meq.Sin(ppscope.el(src.name,s)))+2*R_s*HH+HH*HH
                );
            #now that we have az, el and length, we can transform this to ENU wrt observing antenna
            # NB: the ENU system here has the origin at the antenna which the pp relates to
            ppscope.z_enu(src.name,s) << ppscope.length(src.name,s) * Meq.Sin(ppscope.el(src.name,s))
            ppscope.xy_length(src.name,s) << Meq.Sqrt(Meq.Sqr(ppscope.length(src.name,s)) - Meq.Sqr(ppscope.z_enu(src.name,s)))
            ppscope.x_enu(src.name,s) << Meq.Sin(ppscope.az(src.name,s))*ppscope.xy_length(src.name,s)
            ppscope.y_enu(src.name,s) << Meq.Cos(ppscope.az(src.name,s))*ppscope.xy_length(src.name,s)
            ppscope.pp_enu(src.name,s) << Meq.Composer(ppscope.x_enu(src.name,s),ppscope.y_enu(src.name,s),ppscope.z_enu(src.name,s))
            #multiply ppscope.enu with rot_matrix to get ECEF coordinates of pierce point
            # To do this properly I now have to calculate the pierce-point latitude and
            # correct for the different curvature of the earth. This would still have an error,
            # since ppscope.length is calculated with R_s per station
            ppscope.pp_ecef(src.name,s) << Meq.MatrixMultiply(ppscope.rot_matrix_station(s),ppscope.pp_enu(src.name,s))+xyz(s)
            #
            # Now get long and lat for the pierce points
            # First isolate XYZ (ECEF values)
            pp_X = ppscope.X(src.name,s) << Meq.Selector(ppscope.pp_ecef(src.name,s), index=0)
            pp_Y = ppscope.Y(src.name,s) << Meq.Selector(ppscope.pp_ecef(src.name,s), index=1)
            pp_Z = ppscope.Z(src.name,s) << Meq.Selector(ppscope.pp_ecef(src.name,s), index=2)
            llh = ecef_2_llh(ppscope,pp_X,pp_Y,pp_Z,src.name,s)
            # NB: the ENU system here has the origin at the reference antenna (VLA = 1)
            enu = ecef_2_enu(ppscope,pp_X,pp_Y,pp_Z,src.name,s,1)
            # ppscope.pp(src,s) << Meq.Composer(ppscope.x_trans(src,s),ppscope.y_trans(src,s))
    combine_nodes(ppscope,source_list)
    return ppscope

def combine_nodes(ppscope,source_list):
    """Combine the nodes for the pierce points and array into nodelists for plotting"""
    # For the pp first combine per source
    stations = Context.array.stations();
    x_station = Context.array.x_station();
    y_station = Context.array.y_station();
    z_station = Context.array.z_station();
    for s in stations:
        ppscope.pp_long_stat(s) << Meq.Composer(dims=[0], *[ppscope.lamb(src.name,s)*180.0/math.pi for src in source_list])
        ppscope.pp_lat_stat(s) << Meq.Composer(dims=[0], *[ppscope.phi(src.name,s)*180.0/math.pi for src in source_list])

        ppscope.pp_X_ecef_stat(s) << Meq.Composer(dims=[0], *[ppscope.X(src.name,s) for src in source_list])
        ppscope.pp_Y_ecef_stat(s) << Meq.Composer(dims=[0], *[ppscope.Y(src.name,s) for src in source_list])
        ppscope.pp_Z_ecef_stat(s) << Meq.Composer(dims=[0], *[ppscope.Z(src.name,s) for src in source_list])

        ppscope.az_stat(s) << Meq.Composer(dims=[0], *[ppscope.az(src.name,s)*180.E0/math.pi for src in source_list])
        ppscope.el_stat(s) << Meq.Composer(dims=[0], *[ppscope.el(src.name,s)*180.E0/math.pi for src in source_list])

        ppscope.pp_east_stat(s) << Meq.Composer(dims=[0], *[ppscope.x_trans(src.name,s) for src in source_list])
        ppscope.pp_north_stat(s) << Meq.Composer(dims=[0], *[ppscope.y_trans(src.name,s) for src in source_list])
        ppscope.pp_up_stat(s) << Meq.Composer(dims=[0], *[ppscope.z_trans(src.name,s) for src in source_list])
    # Combine everything for all stations
    # First the pierce points
    ppscope.pp_long << Meq.Composer(dims=[0], *[ppscope.pp_long_stat(s) for s in stations]) 
    ppscope.pp_lat << Meq.Composer(dims=[0], *[ppscope.pp_lat_stat(s) for s in stations])

    ppscope.pp_X_ecef << Meq.Composer(dims=[0], *[ppscope.pp_X_ecef_stat(s) for s in stations])
    ppscope.pp_Y_ecef << Meq.Composer(dims=[0], *[ppscope.pp_Y_ecef_stat(s) for s in stations])
    ppscope.pp_Z_ecef << Meq.Composer(dims=[0], *[ppscope.pp_Z_ecef_stat(s) for s in stations])

    ppscope.pp_az << Meq.Composer(dims=[0], *[ppscope.az_stat(s) for s in stations])
    ppscope.pp_el << Meq.Composer(dims=[0], *[ppscope.el_stat(s) for s in stations])

    ppscope.pp_east << Meq.Composer(dims=[0], *[ppscope.pp_east_stat(s) for s in stations])
    ppscope.pp_north << Meq.Composer(dims=[0], *[ppscope.pp_north_stat(s) for s in stations])
    ppscope.pp_up << Meq.Composer(dims=[0], *[ppscope.pp_up_stat(s) for s in stations])

    # Then the array
    ppscope.long_all << Meq.Composer(dims=[0],*[ppscope.lamb(s)*180.0/math.pi for s in stations])
    ppscope.lat_all << Meq.Composer(dims=0,*[ppscope.phi(s)*180.0/math.pi for s in stations])

    ppscope.arr_X_ecef << Meq.Composer(dims=[0], *[x_station(s)/1E6 for s in stations])
    ppscope.arr_Y_ecef << Meq.Composer(dims=[0], *[y_station(s)/1E6 for s in stations])
    ppscope.arr_Z_ecef << Meq.Composer(dims=[0], *[z_station(s)/1E6 for s in stations])

    ppscope.arr_east << Meq.Composer(dims=[0], *[ppscope.x_trans(s) for s in stations])
    ppscope.arr_north << Meq.Composer(dims=[0], *[ppscope.y_trans(s) for s in stations])
    ppscope.arr_up << Meq.Composer(dims=[0], *[ppscope.z_trans(s) for s in stations])


    
