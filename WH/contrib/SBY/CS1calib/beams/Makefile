default: slib
slib:beam.o
	ld  -shared  beam.o -o beam.so
beam.o:beam.c
	gcc -Wall -c  -fpic beam.c
slib2:beam2.o
	ld  -shared  beam2.o -o beam2.so
beam2.o:beam2.c
	gcc -c  -fpic beam2.c
