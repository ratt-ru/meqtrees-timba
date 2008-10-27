# A CASA script to extract a list of clean components from a model
# array produced by the CASA 'clean' task

import numpy

# load the image file
image='3C84_I.model'
ia.open(image)

# get raw data
data = ia.getchunk()
num_elements = 1
data_shape = data.shape

# get the number of elements in the array
for i in range(len(data_shape)):
  num_elements = num_elements * data_shape[i]

# flatten the array so we can use the numpy/numarray compress function 
# to find locations of clean components
flattened_data = numpy.reshape(data,(num_elements,))

# we need the following array to find the location of clean components
# in the loop below
index_array = numpy.arange(num_elements)

# get locations of non-zero clean component values in the original array
locations = numpy.compress(flattened_data != 0.0, index_array)

# now extract clean component directions
clean_components = []
for k in range(locations.shape[0]):
  index = locations[k]
  # get i, j indices
  i = index / data_shape[0]
  j = index - i *  data_shape[0] 
  clean_comp = numpy.zeros((3,), numpy.float64)
  clean_comp[0] = data[i,j]
  direction = ia.toworld([i,j],'m')['measure']['direction']
  clean_comp[1] = qa.convert(direction['m0'], 'deg')['value']
  clean_comp[2] = qa.convert(direction['m1'], 'deg')['value']
  clean_components.append(clean_comp)
ia.close()

# write out components to file in LSM format
outf=open("sources.txt", "w")
zero = 0.0
for k in range(len(clean_components)):
  components = clean_components[k]
  print>>outf, "%.20f %.20f %.20f %.20f %.20f %.20f " %(components[1], components[2], components[0], zero, zero, zero)
outf.close()
