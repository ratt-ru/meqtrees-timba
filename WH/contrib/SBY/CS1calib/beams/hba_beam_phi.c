#include <math.h>
#include <complex.h>
/* Note: formulas have been optimized! */
#define palpha1  1.13446401379631
#define palpha2  0.55850536063819
#define sin_alpha1 0.90630778703665
#define sin_alpha2 0.52991926423320
#define cos_alpha1 0.42261826174070
#define cos_alpha2 0.84804809615643
#define tan_alpha1 2.14450692050956
#define tan_alpha2 0.62486935190933
#define pH 0.450
#define pL 0.366
#define pL1 0.2562
#define pC 2.998e8 /* speed of light */
#define TOL 1e-9

/* see writeup for the exact formula */
inline complex double 
Phiplus(double A, double B, double k, double L, double L1, double alpha) 
{
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=k*A*L1;
  double ang1=k*(L-L1)*salpha;
  double ang2=k*L*salpha;
  complex double part1=_Complex_I*(A*(cos(tmp)*sin(ang1)-sin(ang2))+salpha*sin(tmp)*cos(ang1))+(-A*sin(tmp)*sin(ang1)+salpha*(cos(tmp)*cos(ang1)-cos(ang2)));

  return z*part1;
}
inline complex double 
Phiminus(double A, double B, double k, double L, double L1, double alpha) 
{
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=-k*A*L1;
  double ang1=k*(L-L1)*salpha;
  double ang2=k*L*salpha;
  complex double part1=_Complex_I*(-A*(cos(tmp)*sin(ang1)-sin(ang2))+salpha*sin(tmp)*cos(ang1))+(A*sin(tmp)*sin(ang1)+salpha*(cos(tmp)*cos(ang1)-cos(ang2)));

  return z*part1;
}
inline complex double
Psiplus(double A, double B, double k, double L, double L1, double alpha)
{
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=k*A*L1;
  double tmp1=k*A*L;
  double ang1=k*(L-L1)*salpha;
  complex double part1=_Complex_I*(salpha*(sin(tmp1)-sin(tmp)*cos(ang1))-A*cos(tmp)*sin(ang1))+salpha*(cos(tmp1)-cos(tmp)*cos(ang1))+A*sin(tmp)*sin(ang1);
  
  return z*part1;
}
inline complex double
Psiminus(double A, double B, double k, double L, double L1, double alpha)
{
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=-k*A*L1;
  double tmp1=-k*A*L;
  double ang1=k*(L-L1)*salpha;
  complex double part1=_Complex_I*(salpha*(sin(tmp1)-sin(tmp)*cos(ang1))+A*cos(tmp)*sin(ang1))+salpha*(cos(tmp1)-cos(tmp)*cos(ang1))-A*sin(tmp)*sin(ang1);
  
  return z*part1;
}

/* 
 * equation - droopy dipole
 * equation: see writeup
 * c: speed of light, f : frequency
 * th: pi/2-elevation
 * phi: phi_0+azimuth, phi_0: dipole orientation
 * parameters: h,L,alpha,phi_0
 * h: height of center from ground, L: projected arm length
 * alpha: droop angle
 * axes: time,freq, az, el
 */
double test_double(const double *par,const double *x){
  return (0);
}

complex double test_complex(const complex *par,const complex *x){
  const double x1=creal(x[1]);
  const double x2=creal(x[2]);
  const double x3=creal(x[3]);
  //const double p0=creal(par[0]);
  //const double p1=creal(par[1]);
  //const double p2=creal(par[2]);
  const double p3=creal(par[3]);

  if (x3<=0.0) return (0+0*_Complex_I); /* below horizon */
  const double theta=M_PI_2-x3;
  const double phi=p3+x2; /* take orientation into account */

  /* some essential constants */
  double k=2*M_PI*x1/pC;

  /* calculate needed trig functions */
  double sin_theta=sin(theta);
  double cos_theta=cos(theta);
  double sin_phi=sin(phi);
  double cos_phi=cos(phi);

  /* mu/4PI=10e-7  x omega*/
  const double mop=(1e-7)*2*M_PI*x1;

  complex double Phi11=Phiplus(sin_theta*cos_phi-cos_theta/tan_alpha1,pH*cos_theta,k,pL1+(pL-pL1)*sin_alpha1/sin_alpha2,pL1,palpha1);
  complex double Psi11=Psiplus(sin_theta*cos_phi-cos_theta/tan_alpha2,(pH-pL1*(1/tan_alpha1-1/tan_alpha2))*cos_theta,k,pL,pL1,palpha2);

  complex double Eth=(sin_phi)*(Phi11+Psi11);

  Phi11=Phiminus(-sin_theta*cos_phi-cos_theta/tan_alpha1,pH*cos_theta,k,pL1+(pL-pL1)*sin_alpha1/sin_alpha2,pL1,palpha1);
  Psi11=Psiminus(-sin_theta*cos_phi-cos_theta/tan_alpha2,(pH-pL1*(1/tan_alpha1-1/tan_alpha2))*cos_theta,k,pL,pL1,palpha2);
  Eth+=(sin_phi)*(Phi11+Psi11);


  Phi11=Phiminus(-sin_theta*cos_phi+cos_theta/tan_alpha1,-pH*cos_theta,k,pL1+(pL-pL1)*sin_alpha1/sin_alpha2,pL1,palpha1);
  Psi11=Psiminus(-sin_theta*cos_phi+cos_theta/tan_alpha2,-(pH-pL1*(1/tan_alpha1-1/tan_alpha2))*cos_theta,k,pL,pL1,palpha2);
  Eth+=(-sin_phi)*(Phi11+Psi11);

  Phi11=Phiplus(sin_theta*cos_phi+cos_theta/tan_alpha1,-pH*cos_theta,k,pL1+(pL-pL1)*sin_alpha1/sin_alpha2,pL1,palpha1);
  Psi11=Psiplus(sin_theta*cos_phi+cos_theta/tan_alpha2,-(pH-pL1*(1/tan_alpha1-1/tan_alpha2))*cos_theta,k,pL,pL1,palpha2);
  Eth+=(-sin_phi)*(Phi11+Psi11);

  return (Eth*mop);
}
int Npar_test=4;
int Nx_test=4;
