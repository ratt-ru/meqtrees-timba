# various compile-time options for the fringe_fit.py script.
# To change, import this *before* fringe_fit.py, then change the values


# number of antennas to include in menu
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

num_stations = 10;

# range of Field IDs
field_list = range(4);

# range of Data Description IDs (usually spectral windows)
ddid_list = range(4);

# available channel selections (for fitting a subset)
channel_selections = [[4,12]];

# to include additional source models in the menu, give list here
extra_source_models = [];

# max polc degrees for phase fitting
max_phase_deg_time = 4;
max_phase_deg_freq = 4;

# set to True to enable options for gain solutions
gain_fitting = False;

# source reference frequency, for models inlcuding a spectral index
source_ref_frequency = 4e+9;


# available tiling options for phase fits and flux fits
# First number in each tiling is the number of segments in a tile
# Second number is maximum tilesize, in timeslots
local_solution_tilings = [(1,45)];
global_solution_tilings = [(100,None)];


# To add options for additional data selections, supply a list of
# TaQL strings here
data_selection_strings = [];


# initial "guesses" for phase polc of each antenna
# If none are supplied, 0 is used
fringe_guesses = {};


# subtilings for phases of individual antennas
# If none are supplied, the global value is used
phase_subtiling = {};

# polynomial degrees (time,freq) of phase polcs
# If not specifed, global default may be used.
# Override may be set in the menu to use the global default even if specified.
phase_polc_degrees = {};
