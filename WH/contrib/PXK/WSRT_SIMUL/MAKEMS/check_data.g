# glish/aips++ script to check the data
# Last Edit: 2006.04.06

pragma include once

include 'imager.g'
include 'table.g'
include 'msplot.g'


imager := imager(argv[3])
t      := table(argv[3])
t.browse()
MS     := msplot(argv[3])




