## LAST EDIT: 2005.12.21
## FUNCTIONS ##############################################################
func write_col(FILE, table, col_name, DIM){
    include 'table.g'
    # write column with non-scalar values to FILE
    # ASSUMPTION: column contains 3D data (!)

    write(FILE, "\n\n")
    write(FILE, "NONSCALAR", col_name, DIM[1], DIM[2], DIM[3], sep=' ')
    write(FILE, "\n\n")
    data    := table.getcol(col_name)
    for (index in 1:DIM[3]) {              # loop all non-scalar values
        for (x in 1:DIM[1]) {              # (!) first y then x?
            for (y in 1:DIM[2]) {          
                write(FILE, data[x,y,index], sep=' ')
            }
        }
	write(FILE, sep='\n')
    }

}


function write_table(filename){
    include 'table.g'

    t       := table(filename, readonly=F)
    dat_file:= paste(filename,'.dat', sep='')
    t.toascii(dat_file)                      # save table to ascii
    #t.browse()

    COLS    := t.colnames()
    LEN_X   := COLS::shape
    LEN_Y   := length(t.getcol(COLS[1]))


    # add non-scalar columns
    cmd_str := paste('>> ', dat_file,sep='')
    FILE    := open(cmd_str)                 # Open file for appending


    # print columns ans shapes
    print ""
    for (i in 1:(LEN_X-1)) {
        DIM     := t.getcol(COLS[i])::shape
        printf("%-16s", COLS[i])
        print DIM
        if (length(DIM) > 1){ 
            write_col(FILE, t, COLS[i], DIM) # write non-scaler columns
        }
    }

    # write length of arrays
    write(FILE, "\n\n")
    write(FILE, "COLUMN_LENGTH", LEN_Y, sep=' ')
    write(FILE, "\n")
}




## MAIN PROGRAM ###########################################################
if (len(argv)<=2){
    print ""; print "glish table2text.g TABLE_NAME"; print ""
    exit
} else {
    write_table(argv[3]);
    print ""
    exit
}














## NOTES ##################################################################
# All of the other column names in this table may be listed with
#- table.colnames()
#- rot_vector := data[[5:data::shape,1:4]] # Rotate a vector five places.
#- purged     := data[data < 700000]       # Delete out-of-range values.
#- ptime      := times[data < 700000]      # match the 'purged' vector.
#- flipped    := data[data::shape:1]       # Reverse a vector.
#- spliced    := [v1, v2]                  # Splice two vectors together.

