gnu3.compiler.conf: CXX=ccache\ /usr/local0/gcc-3.4.3/bin/g++ --with-cppflags="-m32 -msse2 -Wno-deprecated -Wa,--32" --with-threads --with-ldflags="--enable-new-dtags"
gnu3.compiler.aipspp.var: --with-aipspp=/aips++/prod/linux_gnu

optimize.var:	--with-optimize='-O4'
debugopt.var:	--with-optimize='-ggdb -O4'
profiler.var: 	--with-optimize='-ggdb -pg'
profopt.var: 	--with-optimize='-O4 -pg'

debugopt.variant.conf: 	$(standard) $(debugopt)
profopt.variant.conf: 	$(standard) $(profopt)
prof.variant.conf: 	$(standard) $(profiler)

debug-std.variant.conf: $(standard) --with-optimize='-ggdb -DDMI_USE_STD_ALLOC'

