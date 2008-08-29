gnu3.compiler.conf: CXX=ccache\ g++-3.4 --enable-shared --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -fPIC -DAIPS_64B" --with-ldflags="-rpath /lib64"--with-threads --with-sse --with-ldflags="--enable-new-dtags"
gnu3.compiler.aipspp.var: --with-casacore=/aips++/casacore --with-wcs=/aips++/casacore

gnu4.compiler.conf: CXX=ccache\ g++-4.1 --enable-shared --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -fPIC -DAIPS_64B" --with-ldflags="-rpath /lib64"--with-threads --with-sse --with-ldflags="--enable-new-dtags"
gnu4.compiler.aipspp.var: --with-casacore=/aips++/casacore --with-wcs=/aips++/casacore

mpi.compiler.conf: CXX=ccache\ mpicxx --with-mpich=/usr/lib/mpich --enable-shared --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -fPIC -DAIPS_64B" --with-threads --with-sse --with-ldflags="--enable-new-dtags"
mpi.compiler.aipspp.var: --with-casacore=/aips++/casacore --with-wcs=/aips++/casacore

mpist.compiler.conf: CXX=ccache\ mpicxx --with-mpich=/usr/lib/mpich --disable-shared --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -fPIC -DAIPS_64B" --with-threads --with-sse --with-ldflags="-static --enable-new-dtags"
mpist.compiler.aipspp.var: --with-casacore=/aips++/casacore --with-wcs=/aips++/casacore

sse.var: --with-sse

python.var:  --with-python-version=2.4 --with-python=/usr/include/+pkg+vers --with-python-libdir=/usr/lib

optimize.var:	--with-optimize='-O4'
debugopt.var:	--with-debug='-ggdb -O4'
profiler.var: 	--with-debug='-ggdb -pg'
profopt.var: 	--with-optimize='-O4 -pg'

debugopt.variant.conf: 	$(standard) $(debugopt)
profopt.variant.conf: 	$(standard) $(profopt)
prof.variant.conf: 	$(standard) $(profiler)

# debug.variant.conf: $(standard) --with-optimize='-ggdb -DDMI_USE_MALLOC_ALLOC'

