# standard preamble
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

from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,60,120,240]);
Meow.Utils.include_imaging_options();

ANTENNAS   = range(1,14+1)   # define antenna list


# GUI options
TDLCompileOption('arcmin', "FOV (arcmin)",[1,10,30,60,90,120], default=3);





########################################################################
def Book_Mark(Node, page='BookMark'):
  from   Timba.Trees import JEN_bookmarks
  JEN_bookmarks.create(Node, page=page,viewer='Result Plotter')
  pass

def scaled_freq(ns, self):
  """ get relative frequency dependency """
  f0      = ns.freq0 << 0
  f1      = ns.freq1 << 0
  freq    = (Meq.Freq()-f0)/(f1-f0)
  return f0,f1,freq

def scaled_time(ns, self):
  """ get relative time dependency """
  t0      = ns.time0 << 0
  t1      = ns.time1 << 0
  time    = (Meq.Time()-t0)/(t1-t0)
  return t0,t1,time


class SourceList:
  """ create source_list """
  
  DEG       = math.pi/180.    # useful constant: 1 deg in radians
  ARCMIN    = DEG/60;

  def __init__(self, ns, LM=[(0,0)], I=1, Q=0, U=0, V=0):
    self.sources = []
    self.set_lm(LM)
    for isrc in range(len(self.LM)):
      l,m     = self.LM[isrc];
      src     = 'S'+str(isrc);                   # generate ID
      src_dir = Meow.LMDirection(ns,src,l,m);    # create Direction object

      # create source and append to list
      if isrc!=1:
        source = Meow.PointSource   (ns,src,src_dir,I=I,Q=Q,U=U,V=V);
      else:
        source = Meow.GaussianSource(ns,src,src_dir,I=I*5,Q=Q,U=U,V=V,
                                     size=[6*self.ARCMIN,2*self.ARCMIN],
                                     phi=math.pi/4.0,
                                     spi=float(isrc),
                                     freq0=1400e6);
        pass
      self.sources.append(source)
      pass
    pass

  def set_lm(self, LM=[(0,0)]):
    """ Set LMcoords in arcmin"""
    self.LM   = []
    for isrc in range(len(LM)):
      self.LM.append((LM[isrc][0]*self.ARCMIN,
                      LM[isrc][1]*self.ARCMIN)) 
      pass
    pass

  pass


def corrupt_EJones(ns, patch, source_list):
  """ create EJones (beam gain Jones) for each source """
  
  for isrc in range(len(source_list.sources)):

    # get l,m positions
    src     = source_list.sources[isrc]
    l,m     = source_list.LM     [isrc];
    
    # create beam that's different for X and Y dir
    # exp     = Meq.Exp(Meq.Sqr(r*25/labda) * -1)
    labda   = 3e8/Meq.Freq()
    alpha   = 0.1
    r_X     = math.sqrt(l*l*(1+alpha)**2 + m*m)
    r_Y     = math.sqrt(l*l*(1-alpha)**2 + m*m) # cos(pi/2 * rD/lambda)
    wsrt_X  = Meq.Pow(Meq.Cos((math.pi/2) * r_X*25/labda),3)
    wsrt_Y  = Meq.Pow(Meq.Cos((math.pi/2) * r_Y*25/labda),3)

    ns.E(src.direction.name) << Meq.Matrix22(wsrt_X,0,0,wsrt_Y)
    

    # create corrupted source
    corrupt = Meow.CorruptComponent(\
      ns, src,                       # set the source as input
      'E',                           # set the label
      jones=ns.E(src.direction.name) # this will be fed to MatrixMultiply
      );

    patch.add(corrupt);              # add to patch
    pass
  

  # setup a few bookmarks
  Settings.forest_state = record(bookmarks=[
    record(name='E Jones',page=[
    record(udi="/node/E:S0",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/E:S1",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/E:S2",viewer="Result Plotter",pos=(0,2)),
    record(udi="/node/E:S3",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/E:S4",viewer="Result Plotter",pos=(1,1)),
    record(udi="/node/E:S5",viewer="Result Plotter",pos=(1,2)),
    record(udi="/node/E:S6",viewer="Result Plotter",pos=(2,0)),
    record(udi="/node/E:S7",viewer="Result Plotter",pos=(2,1)),
    record(udi="/node/E:S8",viewer="Result Plotter",pos=(2,2)) \
    ])]);

  return patch


def corrupt_GJones(ns, patch, antennas):
  """ create GJones (electronic gain) for each station """
  # create GJones 
  for p in antennas:
    ns.G(p) << 1;
    if p<10:
      Book_Mark(ns.G(p),   'G Jones')
      pass
    pass

  # and corrupt patch by G term
  corrupt_sky = Meow.CorruptComponent(ns,patch,'G',station_jones=ns.G);
  return corrupt_sky







########################################################################
def _define_forest (ns):
  array = Meow.IfrArray(ns,ANTENNAS);  # create an Array object
  observation = Meow.Observation(ns);  # create an Observation object
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  a  = 13
  source_list = SourceList(ns, I=1,
                           LM=[(-a,-a),(-a,0),(-a,a),
                               ( 0,-a),( 0,0),( 0,a), 
                               ( a,-a),( a,0),( a,a)])

  patch       = corrupt_EJones(ns, allsky, source_list)
  corrupt_sky = corrupt_GJones(ns, patch,  ANTENNAS)
  
  
  # create set of nodes to compute visibilities and attach them to sinks
  predict = corrupt_sky.visibilities(array,observation);

  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(predict(p,q),
                             station_1_index=p-1,
                             station_2_index=q-1,output_col='DATA');
    pass
  
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  pass





  
########################################################################
def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  pass

  
  
def _tdl_job_2_make_image (mqs,parent):
  npix         = 512
  image_radius = arcmin*60;                       # image "radius" in arcsec  
  cellsize     = str(image_radius/npix)+"arcsec"; # cellsize*npix =FOV
  Meow.Utils.make_dirty_image(npix     = npix,
                              cellsize = cellsize,
                              channels = [32,1,1]);
  pass
  


# 'python script.tdl'
if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  print len(ns.AllNodes()),'nodes defined';
  pass
