include 'image.g';

img := image('343msfclean.img');
sourcelist := img.findsources(40,cutoff=0.05);
img.done();

for(i in 1:sourcelist.length()){
    rastring  := sourcelist.getrefdirra(i,'time',8);
    decstring := sourcelist.getrefdirdec(i,'angle',8);
    StokesI   := sourcelist.getfluxvalue(i);
}
