#include <math.h>
#include <complex.h>

/* Note: formulas have been optimized! */

#define pL 0.9758 /* length */
#define pC 2.998e8 /* speed of light */
#define pH 1.706 /* height */
#define Sin_al M_SQRT1_2 /* alpha=45 */
#define invSin_al M_SQRT2 /* alpha=45 */
#define Cos_al M_SQRT1_2 /* alpha=45 */
#define Tan_al 1.0 /* alpha=45 */


/* see writeup for the exact formula */
inline complex double 
Gamma1(double sin_th, double cos_th,
   double cos_ph, double k) {

   double A=sin_th*cos_ph-cos_th;
   double tmp=k*A*pL;
   double Re1=cos(tmp)*invSin_al;
   double Im1=sin(tmp)*invSin_al;

   Re1 =Re1-invSin_al*cos(k*pL*invSin_al);
   Im1 =Im1-A*sin(k*pL*invSin_al);

   complex double C1=Re1+Im1*_Complex_I;

   complex double C2=cos(k*pH*cos_th)+sin(k*pH*cos_th)*_Complex_I;
   
   C1=-C1*C2/(A*A-2.0);
   return (C1);
}

/* see writeup for the exact formula */
inline complex double 
Gamma2(double sin_th, double cos_th,
   double cos_ph, double k) {

   double A=-sin_th*cos_ph-cos_th;
   double tmp=k*A*pL;
   double Re1=cos(tmp)*invSin_al;
   double Im1=-sin(tmp)*invSin_al;

   Re1 =Re1-invSin_al*cos(k*pL*invSin_al);
   Im1 =Im1+A*sin(k*pL*invSin_al);

   complex double C1=Re1+Im1*_Complex_I;

   complex double C2=cos(k*pH*cos_th)+sin(k*pH*cos_th)*_Complex_I;
   
   C1=-C1*C2/(A*A-2.0);
   return (C1);
}

/* see writeup for the exact formula */
inline complex double 
Gamma3(double sin_th, double cos_th,
   double cos_ph, double k) {

   double A=-sin_th*cos_ph+cos_th;
   double tmp=k*A*pL;
   double Re1=cos(tmp)*invSin_al;
   double Im1=-sin(tmp)*invSin_al;

   Re1 =Re1-invSin_al*cos(k*pL*invSin_al);
   Im1 =Im1+A*sin(k*pL*invSin_al);

   complex double C1=Re1+Im1*_Complex_I;

   complex double C2=cos(k*pH*cos_th)-sin(k*pH*cos_th)*_Complex_I;
   
   C1=-C1*C2/(A*A-2.0);
   return (C1);
}

/* see writeup for the exact formula */
inline complex double 
Gamma4(double sin_th, double cos_th,
   double cos_ph, double k) {

   double A=sin_th*cos_ph+cos_th;
   double tmp=k*A*pL;
   double Re1=cos(tmp)*invSin_al;
   double Im1=sin(tmp)*invSin_al;

   Re1 =Re1-invSin_al*cos(k*pL*invSin_al);
   Im1 =Im1-A*sin(k*pL*invSin_al);

   complex double C1=Re1+Im1*_Complex_I;

   complex double C2=cos(k*pH*cos_th)-sin(k*pH*cos_th)*_Complex_I;
   
   C1=-C1*C2/(A*A-2.0);
   return (C1);
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
  if (x[3]<=0.0) return 0; /* below horizon */
  const double theta=M_PI_2-x[3];
  const double phi=par[3]+x[2];

  /* some essential constants */
  double k=2*M_PI*x[1]/pC;

  /* calculate needed trig functions */
  double sin_th=sin(theta);
  double cos_th=cos(theta);
  double sin_ph=sin(phi);
  double cos_ph=cos(phi);

  /* mu/4PI=10e-7  x omega/sin(alpha)*/
  const double A=(1e-7)*2*M_PI*x[1]/Sin_al;

  complex double tmp=Gamma1(sin_th,cos_th,cos_ph,k);
  complex double Eph=A*tmp*(Sin_al*sin_ph);

  tmp=Gamma2(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(Sin_al*sin_ph);

  tmp=Gamma3(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(-Sin_al*sin_ph);

  tmp=Gamma4(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(-Sin_al*sin_ph);

  return(creal(Eph));
}

complex double test_complex(const complex *par,const complex *x){
  const double x1=creal(x[1]);
  const double x2=creal(x[2]);
  const double x3=creal(x[3]);
  const double p0=creal(par[0]);
  const double p1=creal(par[1]);
  const double p2=creal(par[2]);
  const double p3=creal(par[3]);
  if (x3<=0.0) return (0+0*_Complex_I); /* below horizon */
  const double theta=M_PI_2-x3;
  const double phi=p3+x2;

  /* some essential constants */
  double k=2*M_PI*x1/pC;

  /* calculate needed trig functions */
  double sin_th=sin(theta);
  double cos_th=cos(theta);
  double sin_ph=sin(phi);
  double cos_ph=cos(phi);

  /* mu/4PI=10e-7  x omega/sin(alpha)*/
  const double A=(1e-7)*2*M_PI*x1/Sin_al;

  complex double tmp=Gamma1(sin_th,cos_th,cos_ph,k);
  complex double Eph=A*tmp*(Sin_al*sin_ph);

  tmp=Gamma2(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(Sin_al*sin_ph);

  tmp=Gamma3(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(-Sin_al*sin_ph);

  tmp=Gamma4(sin_th,cos_th,cos_ph,k);
  Eph+=A*tmp*(-Sin_al*sin_ph);

  return(Eph);

}
int Npar_test=4;
int Nx_test=4;
