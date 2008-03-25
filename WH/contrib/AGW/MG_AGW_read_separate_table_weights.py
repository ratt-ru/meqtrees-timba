#!/usr/bin/python

#
# Copyright (C) 2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# utility function to load FPA beam weights from an aips++ table


try:
  from pyrap_tables import *
except:
  try:
    from pycasatable import *
  except:
    has_table_interface = False
    import sys
    sys.exit()

def read_separate_table_weights(l_beam, m_beam, use_gauss=True):
  # first load weights data from aips++ 'mep' table
  # we read the values directly from the
  # table because the MG_AGW_store_beam_weights.py
  # script will store two sets of values if
  # gaussian fitting is done.
  # The weights are stored in a list for further processing

  # input table with beam weights 
  mep_beam_weights = 'beam_weights_' + str(l_beam) + '_' + str(m_beam) + '.mep'
  print 'reading weights from table ', mep_beam_weights
  t = table(mep_beam_weights)
# Note that im_x_max_fit and im_y_max_fit are merely used as delimiters
  row_number = -1
  weight_re = {}
  weight_im = {}
  status = True
  I_parm_max_x = 1.0
  I_parm_max_y = 1.0

  if use_gauss:
    print ' using weights from gauss fit'
    add_weight = False
    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
      except:
        status = False
      if name.find('gauss_x_max_fit') > -1:
        I_parm_max_x  = t.getcell('VALUES',row_number)[0][0]
      if name.find('gauss_y_max_fit') > -1:
        I_parm_max_y  = t.getcell('VALUES',row_number)[0][0]
        status = False
        add_weight = False
      if not add_weight:
        if name.find('im_y_max_fit') > -1:
          add_weight = True
      else:
        try:
          if name.find('re') > -1:
            weight_re[name] = t.getcell('VALUES',row_number)[0][0]
          if name.find('im') > -1:
            weight_im[name] = t.getcell('VALUES',row_number)[0][0]
        except:
          status = False
  else:
    add_weight = True
    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
      except:
        status = False
      if add_weight:
        if name.find('im_x_max_fit') > -1:
          I_parm_max_x = t.getcell('VALUES',row_number)[0][0]
        if name.find('im_y_max_fit') > -1:
          I_parm_max_y = t.getcell('VALUES',row_number)[0][0]
          add_weight = False
          status = False
        else:
          try:
            if name.find('re') > -1:
              weight_re[name] = t.getcell('VALUES',row_number)[0][0]
            if name.find('im') > -1:
              weight_im[name] = t.getcell('VALUES',row_number)[0][0]
          except:
            status = False
  t.close()
  return (I_parm_max_x, I_parm_max_y, weight_re, weight_im)
