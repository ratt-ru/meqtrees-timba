
#% $Id$ 

#
# Copyright (C) 2002-2007
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

from UVPAxis import *
from ComplexColorMap import *
# find the absolute minimum and maximum of the complex array

    itsValueAxis =  UVPAxis()
    itsComplexColormap = ComplexColorMap(256)
    absmin = abs(itsComplexArray.min())
    itsMaxAbs = abs(itsComplexArray.max())
    if (absmin > itsMaxAbs):
      itsMaxAbs = absmin
    itsValueAxis.calcTransferFunction(-itsMaxAbs, itsMaxAbs, 0, itsComplexColormap.getNumberOfColors()-1)

                                                                                
  if itsComplexSpectrum.min() != itsComplexSpectrum.max()):
# get real and imaginary arrays
    real_image = itsComplexSpectrum.getreal()
    imag_image = itsComplexSpectrum.getimag()
    for i in range(N):
      for j in range(N):
          // SOMETIMES colre > Ncol ?!?!?!
          unsigned int colre = int(itsValueAxis.worldToAxis(real_image[i,j])
          unsigned int colim = int(itsValueAxis.worldToAxis(imag_image[i,j])
          if(colre < Ncol && colim < Ncol) {
            value = itsComplexColormap[itsRealIndex[colre]+itsImagIndex[colim]]);
          } else {
            /*            std::cout << "*************************************" << std::endl;
            std::cout << __FILE__ << ":" << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            std::cout << "colre: " << colre << std::endl;
            std::cout << "colim: " << colim << std::endl;
            std::cout << "real : " << spectrum->real() << std::endl;
            std::cout << "imag : " << spectrum->imag() << std::endl;
            std::cout << "Ncol: " << Ncol << std::endl;
            std::cout << "*************************************" << std::endl;*/          }
