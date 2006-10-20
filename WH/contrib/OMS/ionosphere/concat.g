include 'image.g'

imlist := [];

for( i in (0:95))
{
  imlist[i] := sprintf("demo-slice%03d.img",i);
  
  # convert to FITS
  im := image(imgfile);
  fitsname := spaste(imgname,'.fits');
