default: slib
slib:beam.o
	ld  -shared  beam.o -o beam.so
beam.o:beam.c
	gcc -Wall -c  -fpic beam.c
slib_cutoff:beam_cutoff.o
	ld  -shared  beam_cutoff.o -o beam_cutoff.so
beam_cutoff.o:beam_cutoff.c
	gcc -c  -fpic beam_cutoff.c
beam_dr:beam_dr.c
	gcc -c  -fpic beam_dr.c
	ld  -shared -lm beam_dr.o -o beam_dr.so
beam_dr_phi:beam_dr_phi.c
	gcc -O4 -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_dr_theta:beam_dr_theta.c
	gcc -O4 -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_dr_theta_real:beam_dr_theta_real.c
	gcc -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_dr_theta_imag:beam_dr_theta_imag.c
	gcc -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_dr_phi_real:beam_dr_phi_real.c
	gcc -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_dr_phi_imag:beam_dr_phi_imag.c
	gcc -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
beam_station:beam_station.c
	gcc -c  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
hba_beam_phi:hba_beam_phi.c
	gcc -O4 -c -Wall  -fpic $@.c
	ld  -shared -lm $@.o -o $@.so
hba_beam_theta:hba_beam_theta.c
	gcc -O4 -c -Wall -fpic $@.c
	ld  -shared -lm $@.o -o $@.so

