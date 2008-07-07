#!/usr/bin/env python

from numpy import *
from sys import stdout

NUM_ANTENNAS = 16

class data:
    def __init__(self, idx, times, data):
        self.idx  = idx
        self.time = times
        self.data = data
        assert(len(times) == len(data[0]) == len(data[1]))

    def copy(self):
        nd = [self.data[0].copy(), self.data[1].copy()]
        return data(self.idx, self.time.copy(), nd)

    def __iadd__(self, other):
        assert(self.idx == other.idx)
        assert(all(self.time == other.time))
        self.data[0] += other.data[0]
        self.data[1] += other.data[1]

    def get_names(self):
        if self.__class__.complex_plot:
            return ['Jabs%s' % self.idx,
                    'Jphi%s' % self.idx]
        else:
            return ['Jreal%s' % self.idx,
                    'Jimag%s' % self.idx]

    def get_times(self):
        return self.time

    def get_data(self):
        if self.__class__.complex_plot:
            return [sqrt(self.data[0]**2 + self.data[1]**2),
                    arctan2(self.data[0], self.data[1])]
        else:
            return self.data


def read_data(Jidx, table):
    """Read data from MS table
    
       Retrns a list of (at most) NUM_ANTENNAS data objects
    """
    res = []

    for Aidx in range(1, 1+NUM_ANTENNAS):
        stdout.write("  Processing antenna #%d  ...  " % Aidx)
        idx = '%s:%d' % (Jidx, Aidx)
        query = [ table.query('NAME=="' + kind + idx + '"') for kind in ["Jreal", "Jimag"]]
        if query[0].nrows() == 0:
            stdout.write("SKIPPED, no data\n")
        else:
            values= map((lambda x: array(squeeze(x.getcol('VALUES')))), query)
            times = array(squeeze(query[0].getcol('TIME0')))
            res.append(data(idx, times, values))
            stdout.write("DONE, %d values read\n" % len(times))

    return res


def collapse_data(data_list):
    """Collapse data from mutiple data files.

    data_list is a list of data sets, where each dataset originates
    from a separate data file. See read_data for the format of the
    dataset.
    """
    if len(data_list) == 1:
        return data_list[0]

    res = []
    for i,d in enumerate(data_list[0]):
        n = d.copy()
        for t in data_list[1:]:
            n += t[i]
        res.append(n)
    
    return res

def make_image(img_prefix, data_list,
               zeromean=True, rescale=True, 
               percent=.9, landscape=False):
    """ Produce plot of data and save it as img_prefix.

        For the format of data refer to read_data and unfold_for_plots.
        Parameters:
          zeromean = True : remove mean values before plotting
          rescale  = True : rescale data to fit the bin
          percent  = .9   : percentage of rescale
          landscape= False: image shape
    """

    import time

    ## some plotting options
    import matplotlib
    matplotlib.use("Agg")
    import pylab as P
    P.rc('lines', lw=0.4)
    P.rc('font', size=10)
    P.rc('axes', titlesize=6)
    P.rc('axes', labelsize=7)
    P.rc('axes', labelcolor='black')
    P.rc('xtick', labelsize=7)
    P.rc('ytick', labelsize=7)
    P.clf() ## clear figure
    ax = P.axes([.1, .05, .85, .9])


    ## convert time into hours
    ## here we silently assume that all time axes agree.
    times = data_list[0].get_times() / 3600.
    time_offset = int(times[0] / 24.)
    times -= time_offset * 24.
    print ("Time 0: %f" % times[0])


    ## now the plotting itself
    step = (1 if rescale else .003)
    styles = [
        dict(c='blue', lw=.6, ls='-'),
        dict(c='red',  lw=.6, ls='-')
        ]

    ticks = []
    labels = []
    text_xpos = times[0] #.1 * len(times)
    for idx, d in enumerate(data_list):
        ticks.append(idx*step)
        labels.append('\n'.join(d.get_names()))
        comment = ''
        ## plot data
        for j, z in enumerate(d.get_data()):
            ## normalize data
            min = z.min(); max = z.max(); mean = z.mean();
            scale = abs(max-min)/percent
            if zeromean:
                z = z - mean
            if rescale & (scale != 0):
                z = z/scale
            ## plot
            P.plot(times, z + idx*step, **styles[j])
            comment += "%s : min=%10.3e max=%10.3e mean=%10.3e      " % \
                (d.get_names()[j], min, max, mean)
        ## print stats
        #P.text(text_xpos, step * (idx + .5), comment, verticalalignment='bottom')

    ax.set_yticks(ticks)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Time (MJD +%d)" % time_offset)
    ax.set_title("IMAGE: %s      DATE: %s       (zeromean: %d  rescale: %d)" % 
                 (img_prefix, time.asctime(), zeromean, rescale))
    ax.set_ylim(-step, step * len(data_list))
    ax.xaxis.grid(1)
    P.savefig(img_prefix + ".eps", dpi=300, papertype='a4')


#####################
## main program
#####################
import sys
import pyrap_tables as ct

complex = False
if len(sys.argv) > 1 and sys.argv[1] == '-c':
    complex = True
    del sys.argv[1]
data.complex_plot = complex


if len(sys.argv) < 3:
    print "%s [-c] img_prefix <filename>.mep ..." % sys.argv[0]
    sys.exit(1)


img_prefix = sys.argv[1]
mep_names = sys.argv[2:]


tables = [ct.table(name) for name in mep_names]

## now read in data and plot it
for Jidx in ['11', '12', '21', '22']:
    print "Processing Jones index " + Jidx
    d = [read_data(Jidx, table) for table in tables]
    d = collapse_data(d)
    make_image(img_prefix + "_" + Jidx, d)
