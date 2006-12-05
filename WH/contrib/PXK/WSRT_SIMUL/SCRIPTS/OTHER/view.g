# http://aips2.nrao.edu/docs/notes/195/195.html


include 'image.g'
include 'skycatfromcomponentlist.g'
include 'table.g'

# Make image tool
im := image('mosaic')


# Find strongest sources to 0.2
cl := im.findsources(nmax=100, cutoff=0.2)


# Make skycatalog overlay
ok := skycatfromcomponentlist ('overlay.tbl', cl)
if (is_fail(ok)) {
  print ok::message
}


# Browse catalog
t := table('overlay.tbl')
t.browse()


# Use viewer to display
dv.gui()
