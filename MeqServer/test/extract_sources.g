include 'image.g';

img := image('343mfsclean.img');
sourcelist := img.findsources(40,cutoff=0.05);
img.done();
sourcelist.rename('catII-343.tab');
sourcelist.done();
