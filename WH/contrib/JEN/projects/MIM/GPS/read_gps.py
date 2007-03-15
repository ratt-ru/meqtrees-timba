from Timba.TDL import *
from numarray import *
from numarray import NumArray
from numarray import memmap
from math import *

SECONDS_PER_DAY=3600*24;
NUM_TIMES = int(SECONDS_PER_DAY/30.0);
MAX_POSSIBLE_MEQTREE_SATELLITES =150;
STATION_STEC_SIZE = NUM_TIMES * MAX_POSSIBLE_MEQTREE_SATELLITES * 2 * 4;
STATION_TOTAL_SIZE = STATION_STEC_SIZE + 3 * 8;
SATELLITE_SIZE = NUM_TIMES * MAX_POSSIBLE_MEQTREE_SATELLITES * 3 * 8
gps_data_path = '/home/mevius/data/MIM/GPS_data/';
gps_data_extension = '.54072.dat';

def read_tec(filename='fxhs',time = [0],sat_nr=None,flags=None):
    filename = gps_data_path +filename+gps_data_extension;
    m_fp = memmap.open(filename, "r");
    slice1 = m_fp[0:STATION_STEC_SIZE];
    tec = NumArray(buffer=slice1,
                   shape=(NUM_TIMES,
                          MAX_POSSIBLE_MEQTREE_SATELLITES,
                          2),
                   type='Float32');
    if  sat_nr is not None:
        out=zeros((len(time)),Float32);
    else:
        out=zeros((len(time)),MAX_POSSIBLE_MEQTREE_SATELLITES,Float32);
    for tm in time : # time in seconds
        tm =int(tm/30);
        if sat_nr is not None:
            tec_value = tec[tm,sat_nr,0];
            if flags is not None:
                if tec_value <0 :
                    flags[tm]=1;
            out[tm]=tec_value;
        else:
            # all satelites
            out[tm]=tec[[tm],:,0]; 
    
    return out;
    
def read_sta_pos(filename='fxhs'):
    filename = gps_data_path +filename+gps_data_extension;
    m_fp = memmap.open(filename, "r");
    slice2 = m_fp[STATION_STEC_SIZE:STATION_TOTAL_SIZE];
    sta_pos = NumArray(buffer=slice2,
                       shape=(3),
                       type='Float64')
    x=[];
    for i in range(3):
        x.append(sta_pos[i]);
    return x;
    
def read_sat_pos(filename='sat',time = [0],sat_nr=None):
    filename = gps_data_path +filename+gps_data_extension;
    m_fp = memmap.open(filename, "r");
    slice1 = m_fp[0:SATELLITE_SIZE]
    sat_out = NumArray(buffer=slice1,
                       shape=(NUM_TIMES,
                              MAX_POSSIBLE_MEQTREE_SATELLITES,
                              3),
                       type='Float64');
    if sat_nr is not None:
        num_sat=1;
    else:
        num_sat=MAX_POSSIBLE_MEQTREE_SATELLITES; 
    out=zeros((len(time),num_sat,3),Float64);
    for tm in time : # time in seconds
        tm =int(tm/30);
        if sat_nr is not None:
            out[tm,0] = sat_out[[tm],[sat_nr]][0];
        else:
            # all satelites
            out[tm,:,:] = sat_out[tm,:,:];
        
    return out;


def create_ref_stat_pos(ns,stat_list,ref_stat ='cit1'):
    #creates stations positions with respect to reference x,y,z, create rotation matrix
    xref = read_sta_pos(ref_stat); # use station position as reference ('oxyc' is a good choice for the LA set)
    alpha = atan(-1*xref[0]/xref[1]); #rotation around z-axis
    beta = -1*asin(xref[2]/sqrt(xref[0]*xref[0]+xref[1]*xref[1]+xref[2]*xref[2]));
    rot_matrix = ns.rot_matrix << Meq.Composer(cos(alpha),sin(alpha),0,
                                               -1*cos(beta)*sin(alpha),cos(beta)*cos(alpha),sin(beta),
                                               -sin(beta)*-sin(alpha),-sin(beta)*cos(alpha),cos(beta),
                                               dims=[3,3])
    for sta in stat_list:
        
        xyz = read_sta_pos(sta);
        x=ns.x(sta) << xyz[0];
        y=ns.y(sta) << xyz[1];
        z=ns.z(sta) << xyz[2];
        pos = ns.pos(sta) << Meq.MatrixMultiply(rot_matrix,Meq.Composer(x,y,z));
        ns.pos('norm',sta) << Meq.Sqrt(create_inproduct(ns,pos,pos));
    return rot_matrix;

def create_stat_pos(ns,stat_list):
    for sta in stat_list:
        
        xyz = read_sta_pos(sta);
        x=ns.x(sta) << xyz[0];
        y=ns.y(sta) << xyz[1];
        z=ns.z(sta) << xyz[2];
        pos = ns.pos(sta) << Meq.Composer(x,y,z);
        ns.pos('norm',sta) << Meq.Sqrt(create_inproduct(ns,pos,pos,pos.name,pos.name));

def create_long_lat(ns,stat_list,sat_list,pos,h):
    #longitude latitude of ionosphere crossing point
    for sat in sat_list:
        for stat in stat_list:
            diff = ns.diff(sat,stat)  << pos(sat) - pos(stat);
            length_diff = ns.length(sat,stat)<< Meq.Sqrt(create_inproduct(ns,diff,diff,diff.name,diff.name));
            x_in_xdiff =  ns.x_in_xdiff(sat,stat)<< create_inproduct(ns,pos(stat),diff,pos(stat).name,diff.name);
            length_x = pos('norm',stat);
            
            cos_alpha = ns.cos_alpha(sat,stat) << x_in_xdiff/(length_x*length_diff);
            
            scale = ns.scale(sat,stat) << h/(cos_alpha*length_diff); 

            xyz_mim = ns.xyz_mim(sat,stat) << pos(stat) + scale * diff;
            x_mim = xyz_mim('x')<< Meq.Selector(xyz_mim,index = [0]);
            y_mim = xyz_mim('y')<< Meq.Selector(xyz_mim,index = [1]);
            z_mim = xyz_mim('z')<< Meq.Selector(xyz_mim,index = [2]);
            

            lon = ns.lon(sat,stat) << Meq.Atan(x_mim/y_mim); 
            norm_mim = ns.xyz_mim('norm',sat,stat) << Meq.Sqrt(x_mim*x_mim +y_mim*y_mim+z_mim*z_mim);
            lat = ns.lat(sat,stat) << Meq.Asin(z_mim/norm_mim); 
            

def create_inproduct(ns,x1,x2,name1=None,name2=None):
    if name1 is None:
        name1=x1.name;
    if name2 is None:
        name2=x2.name;
    multiply = ns.vector_multiply(name1,name2)<< x1 * x2;
    
    s0 = ns.select(0,multiply.name)<< Meq.Selector(multiply,index=0);
    s1 = ns.select(1,multiply.name)<<Meq.Selector(multiply,index=1); 
    s2 = ns.select(2,multiply.name)<<Meq.Selector(multiply,index=2);
    sums = Meq.Sum(s0+s1+s2);
    return sums;
