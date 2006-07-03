#!/usr/bin/env python

# file: ../doc/JEN/transients/transient_plots.py


from pylab import *


#-------------------------------------------------------------------------------

def sine_plot():
    a1 = 1.0
    a2 = 0.5
    P1 = 1.0
    P2 = 4.0
    xx = arange(-2, 10, 0.1)
    plot(xx, a1*sin(xx/P1), color='red')
    plot(xx, a2*sin(xx/P2), color='blue')
    kk = arange(45, 80, 8)
    for k in kk:
        plot([xx[k]], [a1*sin(xx[k]/P1)], 'o', color='red')
        plot([xx[k]], [a2*sin(xx[k]/P2)], 'o', color='blue')
        if k==kk[0]: text(xx[k], a1*sin(xx[k]/P1), '.  i-1')
        if k==kk[1]: text(xx[k], a1*sin(xx[k]/P1), '.  i')
        if k==kk[2]: text(xx[k], a1*sin(xx[k]/P1), '.  i+1')
    text(xx[0], a1*sin(xx[0]/P1), ' source far from field centre', color='red')
    text(xx[0], a2*sin(xx[0]/P2), ' source close to field centre', color='blue')
    axis([min(xx), max(xx), -1.1, 1.2])
    xlabel('v-coordinate')
    ylabel('source contribution (corrugation)')
    title('sampling for successive subtraction')
    savefig('sine_plot.png')
    show()
    return True


#-------------------------------------------------------------------------------

def delta (M_arcmin=1.0, T=1.0, b=2000, wvl=2.0, sinDEC=1.0, trace=False):
    d = 2*pi*(b/wvl)*(T/1000.0)*sinDEC*(M_arcmin/3600.0)
    return d

def M_arcmin (delta=pi/10, T=1.0, b=2000, wvl=2.0, sinDEC=1.0, trace=False):
    M = delta*(wvl/b)*(1000.0/T)*3600/(2*pi*sinDEC)
    return M


#-------------------------------------------------------------------------------

def cos_plot(T=1.0):
    b = 2000.0
    wvl = 2.0
    delta_max = pi/10
    M_max = M_arcmin(delta=delta_max, T=T, wvl=wvl, b=b)
    MM = arange(0.01,M_max*4,M_max/10)
    yy = 1 - cos(delta(M_arcmin=MM, T=T, wvl=wvl, b=b))
    yy[yy>1] = 1.0
    plot(MM, yy, color='red')
    plot([MM[0],max(MM)], [0,0], color='gray')          # x-axis
    plot([M_max,M_max], [0,0.5], color='blue')       # vertical
    text(M_max, -0.1, 'M_max()', color='blue')
    MMsinc = pi*MM/(1.5*M_max)
    sinc = sin(MMsinc)/MMsinc
    plot(MM, sinc, color='blue')
    plot(MM, yy*sinc, color='green')
    axis([0.0, max(MM), -0.3, 1.3])
    xlabel('M-coordinate (arcmin)')
    ylabel('subtraction error factor')
    title('source subtraction error (worst case)')
    text(M_max*3, 0.5, '1-cos(delta)', color='red')
    text(1, 1.0, ' sinc', color='blue')
    figtext(0.3, 0.85, 'subtract interval T = '+str(T)+' s')
    figtext(0.3, 0.8, 'delta_max = '+str(delta_max))
    figtext(0.3, 0.75, 'b = '+str(b)+' m')
    figtext(0.3, 0.7, 'lambda = '+str(wvl)+' m')
    figtext(0.3, 0.65, 'FOV: fractional bandwidth = '+str(2/M_max))
    figtext(0.3, 0.6, 'FOV: integration interval = '+str(2000/M_max)+' s')
    savefig('cos_plot_T'+str(int(T))+'s.png')
    show()
    return True


#-------------------------------------------------------------------------------
# Execute:
# sine_plot()
cos_plot()
