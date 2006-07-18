#!/usr/bin/env python

# file: ../doc/JEN/transients/transient_plots.py


import pylab
# from pylab import *


#-------------------------------------------------------------------------------

def sine_plot(**pp):
    funcname = on_entry(pp, 'sine_plot')
    a1 = 1.0
    a2 = 0.5
    P1 = 1.0
    P2 = 4.0
    xx = pylab.arange(-2, 10, 0.1)
    pylab.plot(xx, a1*pylab.sin(xx/P1), color='red')
    pylab.plot(xx, a2*pylab.sin(xx/P2), color='blue')
    kk = pylab.arange(45, 80, 8)
    for k in kk:
        pylab.plot([xx[k]], [a1*pylab.sin(xx[k]/P1)], 'o', color='red')
        pylab.plot([xx[k]], [a2*pylab.sin(xx[k]/P2)], 'o', color='blue')
        if k==kk[0]: pylab.text(xx[k], a1*pylab.sin(xx[k]/P1), '.  t-dt')
        if k==kk[1]: pylab.text(xx[k], a1*pylab.sin(xx[k]/P1), '.  t')
        if k==kk[2]: pylab.text(xx[k], a1*pylab.sin(xx[k]/P1), '.  t+dt')
    pylab.text(xx[0], a1*pylab.sin(xx[0]/P1), ' source far from field centre', color='red')
    pylab.text(xx[0], a2*pylab.sin(xx[0]/P2), ' source close to field centre', color='blue')
    pylab.axis([min(xx), max(xx), -1.1, 1.2])
    pylab.xlabel('v-coordinate')
    pylab.ylabel('source contribution (corrugation)')
    pylab.title('sampling the visibility function for successive subtraction')
    return on_exit(pp, savefile=funcname+'.png')


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def errfac (R_deg=1.0, dt=1.0, b=2000, wvl=2.0, sinDEC=1.0, trace=False):
    """Helper function to calculate the subtraction error factor"""
    epsilon = 2*pylab.pi*(b/wvl)*(dt/(240.0*57.0))*sinDEC*(R_deg/57.0)
    return 1-pylab.cos(epsilon)

#-------------------------------------------------------------------------------

def err_vs_RR_dt(**pp):
    """Plot the subtraction error factor vs source position,
    as a function of subtraction interval dt"""
    funcname = on_entry(pp, 'err_vs_RR_dt')
    b = 1000.0
    wvl = 2.0
    RR = pylab.arange(0.01,10,1)
    n = len(RR)-1
    emax = 0.01
    emax2 = 2*emax
    dt = pylab.arange(1.0,11,1)
    for dt1 in dt:
        ee = errfac (R_deg=RR, dt=dt1, b=b, wvl=wvl, sinDEC=1.0)
        pylab.plot(RR, ee, color='red')
        pylab.text(RR[n],ee[n],'dt = '+str(dt1)+' s')
    pylab.plot([0.0,max(RR)], [emax,emax], color='blue')
    pylab.axis([0, 1.2*max(RR), 0.0, emax2])
    pylab.xlabel('distance from field centre (deg)')
    pylab.ylabel('error factor:  1-cos(e)')
    pylab.title('source subtraction error (worst case)')
    auxinfo(xmin=RR[1], ymax=emax2, subplot=pp['subplot'],
            ss=['baseline = '+str(b)+' m',
                'lambda = '+str(wvl)+' m',
                'dt = '+str(dt)+' s'])
    return on_exit(pp, savefile=funcname+'.png')




#--------------------------------------------------------------------------

def uv_corrug(lm=[1.25,2], color='yellow', domain=True, **pp):
    """Plot the sinusoidal corrugation of a source of given position"""
    funcname = on_entry(pp, 'uv_corrug')
    rr = dict()
    umax = 200
    vmax = umax
    if domain:
        uv_track(umin=umax/2, sinDEC=0.5, frab=0.1, dt=1.0, show=False)
        uv_domain(umin=umax/2, sinDEC=0.5, frab=0.1, HA=1.0, dt=1.0, show=False)
    kk = range(-20,20)
    slope = -float(lm[0])/float(lm[1])         # -l/m
    for k in kk:
        u1 = -umax
        u2 = umax
        v1 = u1*slope + k*2*pylab.pi
        v2 = u2*slope + k*2*pylab.pi
        pylab.plot([u1,u2], [v1,v2], color=color)
    pylab.plot([0.0,0.0], [-vmax,vmax], color='blue')
    pylab.plot([-umax,umax], [0.0,0.0], color='blue')
    pylab.axis([-umax, umax, -vmax, vmax])
    pylab.xlabel('u-coordinate (wavelengths)')
    pylab.ylabel('v-coordinate (wavelengths)')
    pylab.title('uv-plane corrugation')
    auxinfo(xmin=-umax, ymax=vmax, ymin=-vmax, xmax=umax,
            subplot=pp['subplot'],
            ss=['(l,m) = '+str(lm)+' deg'])
    return on_exit(pp, savefile=funcname+'.png', result=rr)


#--------------------------------------------------------------------------

def uv_domain(umin=100, sinDEC=0.5, frab=0.1, HA=1.0, dt=1.0, color='blue', **pp):
    """Draw a request domain with the required characteristics"""
    funcname = on_entry(pp, 'uv_domain')
    vmin = umin*sinDEC
    frab_factor = 1.0 + frab
    draw_ellipse(0,0, a=[umin,umin*frab_factor],
                 b=[vmin,vmin*frab_factor],
                 pmin=HA, pmax=HA+dt/(240*57),
                 color=color)
    return on_exit(pp, savefile=funcname+'.png')

#--------------------------------------------------------------------------

def uv_track(umin=100, sinDEC=0.5, frab=0.1, **pp):
    """Draw a uv-track with the required characteristics"""
    funcname = on_entry(pp, 'uv_track')
    vmin = umin*sinDEC
    frab_factor = 1.0 + frab
    draw_ellipse(0,0, a=[umin,umin*frab_factor],
                 b=[vmin,vmin*frab_factor])
    return on_exit(pp, savefile=funcname+'.png')

#-------------------------------------------------------------------------------
# Plotting helper functions
#-------------------------------------------------------------------------------

def on_entry(pp=dict(), funcname='funcname'):
    """Helper function called at the start of plot-routines"""
    pp.setdefault('trace', True)
    pp.setdefault('save', True)
    pp.setdefault('savefile', funcname+'.png')
    pp.setdefault('rider', dict())
    pp.setdefault('auxinfo', [])
    pp.setdefault('show', True)
    pp.setdefault('color', 'red')
    pp.setdefault('label', None)
    pp.setdefault('marker', 'o')
    pp.setdefault('markersize', None)
    pp.setdefault('markeredgewidth', None)
    pp.setdefault('markeredgecolor', None)
    pp.setdefault('markerfacecolor', None)
    pp.setdefault('linestyle', '-')      # solid
    pp.setdefault('linewidth', None) 
    pp.setdefault('subplot', None)       # integer: nrow*100+ncol*10+iplot (all 1-relative)
    if pp['subplot']:
        pylab.subplot(pp['subplot'])
        pp['save'] = False
        pp['show'] = False
    if pp['trace']: print '\n** on_entry(',funcname,'):',pp
    return funcname

#-------------------------------------------------------------------------------

def rider(pp=dict(), item=None, append=None, trace=True):
    """Interaction with rider record in pp"""
    pp.setdefault('rider', dict())
    if not isinstance(pp['rider'], dict): pp['rider'] = dict()
    if not isinstance(item, str): return pp['rider']
    pp['rider'].setdefault(item, [])
    if not append==None:
        pp['rider'][item].append(append)
    return pp['rider'][item]
        
#-------------------------------------------------------------------------------

def on_exit(pp=dict(), savefile='savefile', result=True):
    """Helper function called at the end of plot-routines"""
    if pp['trace']: print '\n** on_exit(',savefile,') ->',result
    if pp['save']:
        pylab.savefig(savefile)
        print '\n** saved plot in file:',savefile,'\n'
    if pp['show']: pylab.show()
    return result

#-------------------------------------------------------------------------------

def auxinfo(xmin=0.0, ymax=1.0, xmax=1.0, ymin=0,
            color='green', subplot=None,
            ss=[], trace=False):
    """Helper function to put some lines (ss) of auxiliary information
    into the top left corner of the current plot"""
    y = ymax*0.9
    dy = (ymax-ymin)/20
    dx = (xmax-xmin)/20
    if subplot:
        pylab.subplot(subplot)                             # e.g. 211,212,...?
        if str(subplot)[0]=='2': dy = (ymax-ymin)/15       # two rows
        if str(subplot)[0]=='3': dy = (ymax-ymin)/10       # three rows
    for s in ss:
        pylab.text(xmin+dx,y,str(s), color=color)
        if trace: print '-',xmin,y,':',s
        y -= dy
    return True

#-----------------------------------------------------------------------------

def draw_ellipse(x=0, y=0, a=1, b=None, pmin=0, pmax=None, dp=None, color='red'):
    """Draw an ellipse"""
    x = float(x)
    y = float(y)

    # Determine the number of radial spokes:
    closed = False
    if pmax==None:
        pmax = 2*pylab.pi
        closed = True
    pmax = float(pmax)
    pmin = float(pmin)
    if dp==None:
        dp = (pmax-pmin)/16
        if dp>0.1: dp = 0.1
    if closed:
        pp = pylab.arange(pmin,pmax+dp,dp)
    else:
        pp = pylab.arange(pmin,pmax,dp)

    # Draw two or more concentric ellipses:
    if not isinstance(a, (list,tuple)): a = [0.0,a]
    if b==None: b = a
    if not isinstance(b, (list,tuple)): b = [0.0,b]
    for i in range(len(a)):
        xx = []
        yy = []
        for p in pp:
            xx.append(x+a[i]*pylab.cos(p))
            yy.append(y+b[i]*pylab.sin(p))
            pylab.plot(xx, yy, color=color)
        xx2 = xx
        yy2 = yy
        if i==0:
            xx1 = xx
            yy1 = yy
    if not closed:
        n = len(xx)-1
        pylab.plot([xx1[0],xx2[0]], [yy1[0],yy2[0]], color=color, linestyle='-')
        pylab.plot([xx1[n],xx2[n]], [yy1[n],yy2[n]], color=color, linestyle='-')
    return True

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def cos_plot(T=1.0):
    """Obsolete"""
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

# err_vs_RR_dt()
# sine_plot()

uv_corrug(lm=[1,2], domain=False, show=False)
uv_corrug(lm=[-1,0.5])

# sine_plot(subplot=211)
# err_vs_RR_dt(subplot=212)
# pylab.show()
