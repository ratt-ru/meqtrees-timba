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
