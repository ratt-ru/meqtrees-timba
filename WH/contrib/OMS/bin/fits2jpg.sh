#!/bin/bash

for t in $*; do
  fits2karma $t tmp.1.kf
  # NB: MUST use a tmp file, because if you base the karma file name on the FITS file,
  # it mysteriously decides to delete the fits file! Argh!
  # NB: must supply a colormap file, however, the damn thing crashes when I try
  # to write one out! Until I find a file, this script is doomed to languish...
  karma2ppm -converter ppmtojpf -extension jpg -cmapfile MISSING tmp.1.kf ${t%.fits}.jpg
  # rm -f $t.ppm $t.kf
done
