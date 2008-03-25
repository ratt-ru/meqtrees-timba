from pylab import *
#from pyrap_tables import *
from pycasatable import *
from numarray import *

# This script uses matplotlib (pylab) to plot beam weights that have been
# stored in a 'mep' table by the script MG_AGW_store_beam_weights.py. 
# We use the casacore pyrap python wrappers to get data from the aips++ 
# formatted mep table.
# We normalize relative to the mean value of the max absolute value
# of each individual sub_plot

# The following function to plot an arrow with amplitude and
# direction was adapted from a plotting script of Walter Brisken
def arrow(x, y, u, v,rotate_angle=False):
  """ calculate vertices of a filled arrow shape as a function of 
      amplitude and phase """

  X = zeros(shape=(4,),type=Float32)
  Y = zeros(shape=(4,),type=Float32)
  if rotate_angle:
    t = -1.0 * math.atan2(v, u)
  else:
    t = math.atan2(v, u)
  a = 0.5*math.sqrt(u*u + v*v)
  X[0] = x+a*math.sin(t)
  Y[0] = y+a*math.cos(t)
  X[1] = x+a*math.sin(t+2.9)
  Y[1] = y+a*math.cos(t+2.9)
  X[2] = x+a*math.sin(t-2.9)
  Y[2] = y+a*math.cos(t-2.9)
  X[3] = x+a*math.sin(t)
  Y[3] = y+a*math.cos(t)
  return (X,Y)

def plot_weights(i, j, weight_re, weight_im, flip_weight, rotate_angle):
    """ determine a colour for the arrow plot and then plot the weights """

    abs_value = math.sqrt(weight_re * weight_re + weight_im * weight_im)
    if abs_value < 0.3:
      colour = 'b'
    if abs_value >= 0.3 and abs_value < 0.6:
      colour = 'g'
    if abs_value >= 0.6:
      colour = 'r'
    if flip_weight:
      p, q = arrow(i, j+0.5, weight_im, weight_re, rotate_angle)
    else:
      p, q = arrow(i+0.5, j, weight_re, weight_im, rotate_angle)
    # use the supplied matplotlib 'fill' function
    fill(p,q, colour)

def usage( prog ):
  print 'usage : %s <mep imput file>' % prog
  return 1

def main( argv ):
  print 'processing mep file ', argv[1]
# first load data from table
  t = table(argv[1])
  L = ""
  M = ""
  if len(argv) > 2:
    L = str(argv[2])
    M = str(argv[3])

  if len(argv) > 4:
    plot_conj = True
  else:
    plot_conj = False

# Read in and store weights in a list
# Note that im_x_max_fit and im_y_max_fit are merely used as delimiters
  row_number = -1
  weight_re = []
  weight_im = []
  status = True
  if plot_conj:
    add_weight = True
    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
      except:
        status = False
      if add_weight:
        if name.find('im_x_max_fit') > -1:
          add_weight = False
          status = False
        else:
          try: 
            weight_re.append(t.getcell('VALUES',row_number)[0][0])
            row_number = row_number + 1
            name = t.getcell('NAME', row_number)
            weight_im.append(t.getcell('VALUES',row_number)[0][0])
          except:
            status = False
  else:
    add_weight = False
    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
      except:
        status = False
      if not add_weight:
        if name.find('im_y_max_fit') > -1:
          add_weight = True
      else:
        try:
          weight_re.append(t.getcell('VALUES',row_number)[0][0])
          row_number = row_number + 1
          name = t.getcell('NAME', row_number)
          weight_im.append(t.getcell('VALUES',row_number)[0][0])
        except:
          status = False
  t.close()

# find weight with maximum amplitude
  max_abs = 0.0
  for k in range(len(weight_re)):
    abs_value = math.sqrt(weight_re[k] * weight_re[k] + weight_im[k] * weight_im[k])
    if abs_value > max_abs:
      max_abs = abs_value
  print 'max_abs is ', max_abs

# do first group of weights
  counter = 0
  i = 8
  j = -1
  for k in range(len(weight_re)):
    j = j + 1
    if j > 9:
      i = i - 1
      j = 0
      if i < 0:
        break
    plot_weights(i, j, weight_re[counter]/max_abs, weight_im[counter]/max_abs,flip_weight=False,rotate_angle=True)
    counter = counter + 1

# do second group of weights
  start = counter
  i = 9
  j = -1
  for k in range(start,len(weight_re)):
    j = j + 1
    if j > 8:
      i = i - 1
      j = 0
      if i < 0:
        break
    plot_weights(i, j, weight_re[counter]/max_abs, weight_im[counter]/max_abs, flip_weight=True,rotate_angle=False)
    counter = counter + 1

# plot an arrow with normalized amplitude of 1 as a reference
  plot_weights(-1.5, 0.5, 1.0, 0.0,False,False)

  xlabel('X/I location of feed')
  ylabel('Y/J location of feed')
  grid(True)
  if plot_conj:
    title_string = 'A/P of Beam Weights (Phase Conjugate) '
  else:
    title_string = 'A/P of Beam Weights (Gaussian Fit) '
  if len(L) > 0:
   title_string = title_string + 'L = ' + L + ' M = ' + M
  title(title_string)
  if plot_conj:
    savefig(argv[1] + '_plot_conj.png')
  else:
    savefig(argv[1] + '_plot.png')
#   savefig(argv[1] + '_plot.svg')
# show()

if __name__ == "__main__":
  """ We need at least one argument: the name of the mep table to plot """
  if len(sys.argv) < 2:
    usage(sys.argv[0])
  else:
    main(sys.argv)

