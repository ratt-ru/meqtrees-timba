# simple glish script to find sources in an image
include 'image.g';

img := image('xxxx.img');
sourcelist := img.findsources(40,cutoff=0.05);
img.done();
sourcelist.rename('xxx_sources.tab');
sourcelist.done();
