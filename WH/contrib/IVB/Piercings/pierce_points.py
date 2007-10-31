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
def ecef_2_enu (ns, X, Y, Z, src, s, ref):
    """ Calculate ENU coordinates from ECEF"""
    if src < 0: # convert the array
        ns.dX(s) << X - ns.x_station(ref)
        ns.dY(s) << Y - ns.y_station(ref)
        ns.dZ(s) << Z - ns.z_station(ref)
        # Hardcoded coordinates for VLA origin (to test results)
        lamb = -1.8782943
        phi = 0.59478397
        # Rotate
        ns.x_trans(s) << -ns.dX(s)*Meq.Sin(ns.lamb(ref)) + ns.dY(s)*Meq.Cos(ns.lamb(ref))
        ns.y_trans(s) << -ns.dX(s)*Meq.Sin(ns.phi(ref))*Meq.Cos(ns.lamb(ref)) - ns.dY(s)*Meq.Sin(ns.phi(ref))*Meq.Sin(ns.lamb(ref)) + ns.dZ(s)*Meq.Cos(ns.phi(ref));
        ns.z_trans(s) << ns.dX(s)*Meq.Cos(ns.phi(ref))*Meq.Cos(ns.lamb(ref)) + ns.dY(s)*Meq.Cos(ns.phi(ref))*Meq.Sin(ns.lamb(ref)) + ns.dZ(s)*Meq.Sin(ns.phi(ref));

        #ns.x1_trans(s) << -ns.dX(s)*math.sin(lamb) + ns.dY(s)*math.cos(lamb)
        #ns.y1_trans(s) << -ns.dX(s)*math.sin(phi)*math.cos(lamb) - ns.dY(s)*math.sin(phi)*math.sin(lamb) + ns.dZ(s)*math.cos(phi)
        #ns.z1_trans(s) << ns.dX(s)*math.cos(phi)*math.cos(lamb) + ns.dY(s)*math.cos(phi)*math.sin(lamb) + ns.dZ(s)*math.sin(phi);
    if src >= 0: # convert the pierce points
        ns.dX(src,s) << X - ns.x_station(ref)
        ns.dY(src,s) << Y - ns.y_station(ref)
        ns.dZ(src,s) << Z - ns.z_station(ref)
        # Hardcoded coordinates for VLA origin
        lamb = -1.8782943
        phi = 0.59478397
        ns.x_trans(src,s) << -ns.dX(src,s)*math.sin(lamb) + ns.dY(src,s)*math.cos(lamb)
        ns.y_trans(src,s) << -ns.dX(src,s)*math.sin(phi)*math.cos(lamb) - ns.dY(src,s)*math.sin(phi)*math.sin(lamb) + ns.dZ(src,s)*math.cos(phi)
        ns.z_trans(src,s) << ns.dX(src,s)*math.cos(phi)*math.cos(lamb) + ns.dY(src,s)*math.cos(phi)*math.sin(lamb) + ns.dZ(src,s)*math.sin(phi);


def ecef_2_llh (ns, X, Y, Z, src, s):
    """ Calculate longitude and latitude for each pierce point"""
    # This routine uses the non-iterative method from Kaplan (see wikipedia)
    # It works OK for the VLA conversion in IDL.
    # non-nodes (use Python math
    if src >= 0: # convert pierce points
        bigE = sqrt(WGS_a**2. - WGS_b**2.)
        # nodes (use MeqTree math)
        r = ns.r(src,s) << Meq.Sqrt(Meq.Sqr(X) + Meq.Sqr(Y));
        F = ns.F(src,s) << 54.0*WGS_b**2*Meq.Sqr(Z)
        G = ns.G(src,s) << Meq.Sqr(r) + (1-WGS_e**2)*Meq.Sqr(Z)- (WGS_e*bigE)**2
        C = ns.C(src,s) << WGS_e**4*F*Meq.Sqr(r)/Meq.Pow(G,3)
        S = ns.S(src,s) << Meq.Pow(1+C+Meq.Sqrt(Meq.Sqr(C)+2*C),1/3)
        P = ns.P(src,s) << F/(3*Meq.Sqr(S+1/S+1)*Meq.Sqr(G))
        Q = ns.Q(src,s) << Meq.Sqrt(1+2*WGS_e**4*P)
        r_0=ns.r0(src,s) << -P*WGS_e**2*r/(1+Q) + Meq.Sqrt(
            WGS_a**2*(1+1/Q)/2 - (P*(1-WGS_e**2)*Meq.Sqr(Z))/(Q*(1+Q)) - P*Meq.Sqr(r)/2
            )
        #U = ns.U(src,s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + Meq.Sqr(Z))
        V = ns.V(src,s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + (1-WGS_e**2)*Meq.Sqr(Z))
        Z_0 = ns.Z_0(src,s) << WGS_b**2*Z/(WGS_a*V)
        ns.phi(src,s) << (Meq.Atan((Z+WGS_ep**2*Z_0)/r))
        ns.lamb(src,s) << (Meq.Atan(Y/X) - math.pi)
        # ns.height(src,s) << U*(1-WGS_b*WGS_b/(WGS_a*V))
        # ns.pp(src,s) << Meq.Composer(ns.lamb(src,s),ns.phi(src,s))
    if src < 0 : # convert array
        bigE = sqrt(WGS_a**2. - WGS_b**2.)
        # nodes (use MeqTree math)
        r = ns.r(s) << Meq.Sqrt(Meq.Sqr(X) + Meq.Sqr(Y));
        F = ns.F(s) << 54.0*WGS_b**2*Meq.Sqr(Z)
        G = ns.G(s) << Meq.Sqr(r) + (1-WGS_e**2)*Meq.Sqr(Z)- (WGS_e*bigE)**2
        C = ns.C(s) << WGS_e**4*F*Meq.Sqr(r)/Meq.Pow(G,3)
        S = ns.S(s) << Meq.Pow(1+C+Meq.Sqrt(Meq.Sqr(C)+2*C),1/3)
        P = ns.P(s) << F/(3*Meq.Sqr(S+1/S+1)*Meq.Sqr(G))
        Q = ns.Q(s) << Meq.Sqrt(1+2*WGS_e**4*P)
        r_0=ns.r0(s) << -P*WGS_e**2*r/(1+Q) + Meq.Sqrt(
            WGS_a**2*(1+1/Q)/2 - (P*(1-WGS_e**2)*Meq.Sqr(Z))/(Q*(1+Q)) - P*Meq.Sqr(r)/2
            )
        #U = ns.U(s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + Meq.Sqr(Z))
        V = ns.V(s) << Meq.Sqrt(Meq.Sqr(r-WGS_e**2*r_0) + (1-WGS_e**2)*Meq.Sqr(Z))
        Z_0 = ns.Z_0(s) << WGS_b**2*Z/(WGS_a*V)
        ns.phi(s) << (Meq.Atan((Z+WGS_ep**2*Z_0)/r))
        ns.lamb(s) << (Meq.Atan(Y/X) - math.pi)
        # ns.height(s) << U*(1-WGS_b*WGS_b/(WGS_a*V))
            
#**************************Rotation matrix and other helper routines************************
def make_rot_matrix (ns):
    """ Construct the rotation matrix to convert ENU to ECEF coordinates for a all stations"""
    # longitude is RH around Z, latitude is positive from equator to north-pole
    # Could it be faster to do this in a single reference frame for a core station in case of LOFAR?
    # Then we would only have to de one rotation, rather than 77, but the pierce-points need to be
    # calculated in another reference frame as well.
    stations = Context.array.stations();
    xyz = Context.array.xyz(); # station coordinates in ECEF
    # Define first antenna of the array as reference antenna
    for s in stations:
        ns.x_station(s) << Meq.Selector(xyz(s),index=0)
        ns.y_station(s) << Meq.Selector(xyz(s),index=1)
        ns.z_station(s) << Meq.Selector(xyz(s),index=2)
        # longitude and latitude of the station (geocentric)
        array_llh = ecef_2_llh(ns, ns.x_station(s), ns.y_station(s), ns.z_station(s), -1, s)
        # for the stations use a negative source number
        # rotation matrix ENU to ECEF, this is done PER STATION!
        ns.rot_matrix_station(s) << Meq.Composer(
            -Meq.Sin(ns.lamb(s)), -Meq.Sin(ns.phi(s))*Meq.Cos(ns.lamb(s)), Meq.Cos(ns.phi(s))*Meq.Cos(ns.lamb(s)),
            Meq.Cos(ns.lamb(s)), -Meq.Sin(ns.phi(s))*Meq.Sin(ns.lamb(s)), Meq.Cos(ns.phi(s))*Meq.Sin(ns.lamb(s)),
            0, Meq.Cos(ns.phi(s)), Meq.Sin(ns.phi(s)), dims=[3,3])
        # Get the enu coordinates for the array
        array_enu = ecef_2_enu(ns,ns.x_station(s),ns.y_station(s),ns.z_station(s), -1, s, 1)
    ns.rot_matrix << Meq.Composer(*[ns.rot_matrix_station(s) for s in stations])

def get_radius (ns, lat):
    """Calculate the earth radius at a given latitude, assuming the WGS84 ellipsoid"""
    # Latitude is POSITIVE from equator towards north-pole, in radians
    earth_radius = WGS_b / Meq.Sqrt(1-WGS_e*WGS_e*Meq.Sqr(Meq.Cos(lat)))
    return earth_radius

#*******************Main routine to calculate pp coordinates**********************************
def get_pp (ns, source_list):
    """Solve for the length of the vector from station to pierce point assuming a spherical
    earth and calculate the pierce point coordinates in ENU per station"""
    # Get basic info from Meow
    stations = Context.array.stations();
    xyz = Context.array.xyz();
    matrix = make_rot_matrix(ns);
    for src in source_list:
        # get radec for each source
        radec = src.direction.radec()
        for s in stations:
            # get AzEl for each source and for each station, do these have to be nodes?
            ns.azel(src.name,s) << Meq.AzEl(radec,xyz(s));
            ns.az(src.name,s) << Meq.Selector(ns.azel(src.name,s), index=0)
            ns.el(src.name,s) << Meq.Selector(ns.azel(src.name,s), index=1)
            #
            # Put the elevation and earth radius in the solution for the length
            # NB the solution assumes a spherical earth with radius = radius at station latitude!
            # R_s = get_radius(ns, ns.lat(s))
            R_s=get_radius(ns,ns.phi(s))
            #
            # ERROR: I make an assumption here which gives rise to an error in ns.length
            # I assume that the earth radius in the direction of the pierce point is
            # approximately the same as the earth radius towards the station. 
            ns.length(src.name,s) << -1.0*R_s*Meq.Sin(ns.el(src.name,s)) + Meq.Sqrt(
                R_s*R_s*Meq.Sqr(Meq.Sin(ns.el(src.name,s)))+2*R_s*HH+HH*HH
                );
            #now that we have az, el and length, we can transform this to ENU wrt observing antenna
            # NB: the ENU system here has the origin at the antenna which the pp relates to
            ns.z_enu(src.name,s) << ns.length(src.name,s) * Meq.Sin(ns.el(src.name,s))
            ns.xy_length(src.name,s) << Meq.Sqrt(Meq.Sqr(ns.length(src.name,s)) - Meq.Sqr(ns.z_enu(src.name,s)))
            ns.x_enu(src.name,s) << Meq.Sin(ns.az(src.name,s))*ns.xy_length(src.name,s)
            ns.y_enu(src.name,s) << Meq.Cos(ns.az(src.name,s))*ns.xy_length(src.name,s)
            #ns.x_enu(src.name,s) << ns.length(src.name,s)*Meq.Cos(ns.el(src.name,s))*Meq.Sin(ns.az(src.name,s))
            #ns.y_enu(src.name,s) << ns.length(src.name,s)*Meq.Cos(ns.el(src.name,s))*Meq.Cos(ns.az(src.name,s))
            #ns.z_enu(src.name,s) << ns.length(src.name,s)*Meq.Sin(ns.az(src.name,s))
            ns.pp_enu(src.name,s) << Meq.Composer(ns.x_enu(src.name,s),ns.y_enu(src.name,s),ns.z_enu(src.name,s))
            #multiply ns.enu with rot_matrix to get ECEF coordinates of pierce point
            ns.pp_ecef(src.name,s) << Meq.MatrixMultiply(ns.rot_matrix_station(s),ns.pp_enu(src.name,s))+xyz(s)
            # To do this properly I now have to calculate the pierce-point latitude and
            # correct for the different curvature of the earth. This would still have an error,
            # since ns.length is calculated with R_s per station
            #
            # Now get long and lat for the pierce points
            # First isolate XYZ (ECEF values)
            pp_X = ns.pp_X(src.name,s) << Meq.Selector(ns.pp_ecef(src.name,s), index=0)
            pp_Y = ns.pp_Y(src.name,s) << Meq.Selector(ns.pp_ecef(src.name,s), index=1)
            pp_Z = ns.pp_Z(src.name,s) << Meq.Selector(ns.pp_ecef(src.name,s), index=2)
            llh = ecef_2_llh(ns,pp_X,pp_Y,pp_Z,src.name,s)
            # NB: the ENU system here has the origin at the reference antenna (VLA = 1)
            enu = ecef_2_enu(ns,pp_X,pp_Y,pp_Z,src.name,s,1)
            ns.pp(src,s) << Meq.Composer(ns.x_trans(src,s),ns.y_trans(src,s))
            # redefine the output from enu_2_llh
            # ns.pp(src.name,s) ** ns.pp_llh(src.name,s) # this doesn't work
            #
            # This should be the correction, for speed I'll leave it obsolete for now. If changed
            # the ns.pp node above needs to be renamed ns.pp_prime
            #
            #ns.x_pp(src.name,s) << Meq.Selector(ns.pp_prime(src.name,s), index=0)
            #ns.y_pp(src.name,s) << Meq.Selector(ns.pp_prime(src.name,s), index=1)
            #ns.lat_pp(src.name,s) << Meq.Atan(ns.y_pp(src.name,s)/ns.x_pp(src.name,s))
            #R_p = get_radius(ns,ns.lat_pp(src.name,s))
            #ns.length_pp(src.name,s) << 0.5*R_p*Meq.Sin(ns.el(src.name,s)) + 0.5*Meq.Sqrt(
            #    R_p*R_p*Meq.Sqr(Meq.Sin(ns.el(src.name,s)))+8*R_p*HH+4*HH*HH);
            #ns.x_enupp(src.name,s) << ns.length_pp(src.name,s)*Meq.Cos(ns.el(src.name,s))*Meq.Sin(ns.az(src.name,s))
            #ns.y_enupp(src.name,s) << ns.length_pp(src.name,s)*Meq.Cos(ns.el(src.name,s))*Meq.Cos(ns.az(src.name,s))
            #ns.z_enupp(src.name,s) << ns.length_pp(src.name,s)*Meq.Sin(ns.az(src.name,s))
            #ns.pp_enu_final(src.name,s) << Meq.Composer(ns.x_enupp(src.name,s),ns.y_enupp(src.name,s),ns.z_enupp(src.name,s))
            #ns.pp(src.name,s) << Meq.MatrixMultiply(ns.rot_matrix(s),ns.pp_enu_final(src.name,s))+xyz(s)
    compress_nodes(ns,source_list)
    return ns.pp

def compress_nodes(ns,source_list):
    """Combine the nodes for the pierce points and array into nodelists for plotting"""
    # For the pp first combine per source
    stations = Context.array.stations();
    for s in stations:
        ns.pp_long_stat(s) << Meq.Composer(dims=[0], *[ns.lamb(src.name,s)*180.0/math.pi for src in source_list])
        ns.pp_lat_stat(s) << Meq.Composer(dims=[0], *[ns.phi(src.name,s)*180.0/math.pi for src in source_list])
        #ns.pp_hei_stat(s) << Meq.Composer(dims=[0], *[ns.height(src.name,s) for src in source_list])

        ns.pp_X_ecef_stat(s) << Meq.Composer(dims=[0], *[ns.pp_X(src.name,s) for src in source_list])
        ns.pp_Y_ecef_stat(s) << Meq.Composer(dims=[0], *[ns.pp_Y(src.name,s) for src in source_list])
        ns.pp_Z_ecef_stat(s) << Meq.Composer(dims=[0], *[ns.pp_Z(src.name,s) for src in source_list])

        ns.az_stat(s) << Meq.Composer(dims=[0], *[ns.az(src.name,s)*180.E0/math.pi for src in source_list])
        ns.el_stat(s) << Meq.Composer(dims=[0], *[ns.el(src.name,s)*180.E0/math.pi for src in source_list])

        ns.pp_east_stat(s) << Meq.Composer(dims=[0], *[ns.x_trans(src.name,s) for src in source_list])
        ns.pp_north_stat(s) << Meq.Composer(dims=[0], *[ns.y_trans(src.name,s) for src in source_list])
        ns.pp_up_stat(s) << Meq.Composer(dims=[0], *[ns.z_trans(src.name,s) for src in source_list])
    # Combine everything for all stations
    # First the pierce points
    ns.pp_long << Meq.Composer(dims=[0], *[ns.pp_long_stat(s) for s in stations]) 
    ns.pp_lat << Meq.Composer(dims=[0], *[ns.pp_lat_stat(s) for s in stations])
    #ns.pp_hei << Meq.Composer(dims=[0], *[ns.pp_hei_stat(s) for s in stations])

    ns.pp_X_ecef << Meq.Composer(dims=[0], *[ns.pp_X_ecef_stat(s) for s in stations])
    ns.pp_Y_ecef << Meq.Composer(dims=[0], *[ns.pp_Y_ecef_stat(s) for s in stations])
    ns.pp_Z_ecef << Meq.Composer(dims=[0], *[ns.pp_Z_ecef_stat(s) for s in stations])

    ns.pp_az << Meq.Composer(dims=[0], *[ns.az_stat(s) for s in stations])
    ns.pp_el << Meq.Composer(dims=[0], *[ns.el_stat(s) for s in stations])

    ns.pp_east << Meq.Composer(dims=[0], *[ns.pp_east_stat(s) for s in stations])
    ns.pp_north << Meq.Composer(dims=[0], *[ns.pp_north_stat(s) for s in stations])
    ns.pp_up << Meq.Composer(dims=[0], *[ns.pp_up_stat(s) for s in stations])

    # Then the array
    ns.long_all << Meq.Composer(dims=[0],*[ns.lamb(s)*180.0/math.pi for s in stations])
    ns.lat_all << Meq.Composer(dims=0,*[ns.phi(s)*180.0/math.pi for s in stations])

    ns.arr_X_ecef << Meq.Composer(dims=[0], *[ns.x_station(s)/1E6 for s in stations])
    ns.arr_Y_ecef << Meq.Composer(dims=[0], *[ns.y_station(s)/1E6 for s in stations])
    ns.arr_Z_ecef << Meq.Composer(dims=[0], *[ns.z_station(s)/1E6 for s in stations])

    ns.arr_east << Meq.Composer(dims=[0], *[ns.x_trans(s) for s in stations])
    ns.arr_north << Meq.Composer(dims=[0], *[ns.y_trans(s) for s in stations])
    ns.arr_up << Meq.Composer(dims=[0], *[ns.z_trans(s) for s in stations])


    
