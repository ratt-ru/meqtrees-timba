include 'note.g';
include 'measures.g';

include 'viewer.g'
dp:=dv.newdisplaypanel(hasgui=T, guihasmenubar=T, isolationmode=T, width=1024, height=1024);
rec:=dp.canvasmanager().getoptions();
rec.colortablesize:=3000;
dp.canvasmanager().setoptions(rec);

imagenames:=shell('ls -d sim*/sim.clean.restored');
print imagenames;

include 'image.g';
global dv;
i:=0;
for (imagename in imagenames) {
  i+:=1;
  ddr:=dv.loaddata(imagename, 'raster');
  dp.register(ddr);
#
  rec:=ddr.getoptions();
  rec.colormap.value:='Greyscale 2';
  rec.resample.value:='bilinear';
  rec.axislabelswitch:=T;
  rec.titletext.value:=imagename
  rec.datamax.value:=0.01
  rec.datamin.value:=-0.001
  ddr.setoptions(rec);

  pname:=spaste(imagename~s!\/sim\.clean\.restored!!g, '.ps');
  dc.delete(pname, confirm=F);
  dp.canvasprintmanager().writeps(pname, dpi=300, landscape=T,
				  eps=T);
  dp.unregister(ddr);
}
