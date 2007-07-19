#!/usr/bin/python

# This is a script for generating sixpack Trees.

# Standard imports
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Trees import TDL_Sixpack
from Timba.Meq import meq

def make_sixpack (srcname='',RA=0.0,Dec=0.0,ISIF0=0.0,Qpct=0.0,Upct=0.0,Vpct=0.0,ns=0):
    
    RA_root = make_RA(srcname,RA,ns);
    Dec_root = make_Dec(srcname,Dec,ns);
    I_root = make_StokesI(srcname,ISIF0,ns);
    Q_root = make_StokesQ(srcname,Qpct,I_root,ns);
    U_root = make_StokesU(srcname,Upct,I_root,ns);
    V_root = make_StokesV(srcname,Vpct,I_root,ns);

    sixname = 'sixpack[q='+srcname+']';
    #sixroot = ns[sixname] << Meq.Composer(RA_root,Dec_root,I_root,Q_root,U_root,V_root);

    Sixpack = TDL_Sixpack.Sixpack(label=srcname,
                                                                stokesI=I_root,
                                                                stokesQ=Q_root,
                                                                stokesU=U_root,
                                                                stokesV=V_root,
                                                                ra=RA_root,
                                                                dec=Dec_root)

    return Sixpack;


def make_RA(srcname='',RA=0.0,ns=0):
    stringRA = 'RA[q='+srcname+']';
# Creation of Meq Polc
    meq_polc = meq.polc(RA);
# Create leaf node called 'RA[q=xyz]'
    RA_root = ns[stringRA] << Meq.Parm(meq_polc);

    return RA_root;
    
def make_Dec(srcname='',Dec=0.0,ns=0):
    stringDec = 'Dec[q='+srcname+']';
# Creation of Meq Polc
    meq_polc = meq.polc(Dec);
# Create leaf node called 'RA[q=xyz]'
    Dec_root = ns[stringDec] << Meq.Parm(meq_polc);

    return Dec_root;

def make_StokesI(srcname='',ISIF0=0.0,ns=0):

    stringI    = 'StokesI[q=' + srcname + ']';
    stringISIF = 'ISIF[q=' + srcname + ']';

####
# Creation of Meq Polclog
    meq_polclog = meq.polclog(ISIF0);

# Create leaf node called 'ISIF[q=xyz]'
    isif_root = ns[stringISIF] << Meq.Parm(meq_polclog);

# Create a MeqConstant with value 10
    const10_root = ns['const10'] << Meq.Constant(10.0,link_or_create=True);

# Create StokesI node

    I_root = ns[stringI] << Meq.Pow(const10_root,isif_root,link_or_create=True); 
# For now a different definition of StokesI
#    meqpolc = meq.polc(ISIF0);
#    I_root = ns[stringI] << Meq.Parm(meqpolc);

    return I_root;
    
def make_StokesQ(srcname='',Qpct=0.0,I_root=0,ns=0):

    stringQ    = 'StokesQ[q=' + srcname + ']';
    stringQpct = 'Qpct[q=' + srcname + ']';

####
# Creation of Meq Polc -1 < Qpct < 1
    meq_polc = meq.polc(Qpct);

# Qpct root    
    Qpct_root = ns[stringQpct] << Meq.Parm(meq_polc);

# StokesQ root
    Q_root = ns[stringQ] << Meq.Multiply(Qpct_root,I_root);

    return Q_root;

def make_StokesU(srcname='',Upct=0.0,I_root=0,ns=0):

    stringU    = 'StokesU[q=' + srcname + ']';
    stringUpct = 'Upct[q=' + srcname + ']';

####
# Creation of Meq Polc -1 < Upct < 1
    meq_polc = meq.polc(Upct);

# Upct root    
    Upct_root = ns[stringUpct] << Meq.Parm(meq_polc);

# StokesU root
    U_root = ns[stringU] << Meq.Multiply(Upct_root,I_root);
    
    return U_root;

def make_StokesV(srcname='',Vpct=0.0,I_root=0,ns=0):

    stringV    = 'StokesV[q=' + srcname + ']';
    stringVpct = 'Vpct[q=' + srcname + ']';

####
# Creation of Meq Polc
    meq_polc = meq.polc(Vpct);

# Vpct root    
    Vpct_root = ns[stringVpct] << Meq.Parm(meq_polc);

# StokesV root
    V_root = ns[stringV] << Meq.Multiply(Vpct_root,I_root);

    return V_root;
