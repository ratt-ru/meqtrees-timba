# simple glish script to remove a column from an aips++ table
include 'tables.g'
t:=table("TEST_CLAR.MS",readonly=F)
t.removecols("DATA")
t.flush()
t.close()


