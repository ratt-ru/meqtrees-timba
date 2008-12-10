# PIL and pyfits are show-stoppers for this plugin
try:
  import PIL.Image
except:
# image.py will complain about this one too, more verbosely
  print """PIL package not found, rendering of FITS files will not be available.
""";
  raise;

try:
  import pyfits
except:
  print """PyFITS package not found, rendering of FITS files will not be available.
PyFITS is available from http://www.stsci.edu/resources/software_hardware/pyfits,
or as Debian package python-pyfits.
""";
  raise

try:
  import numpy
except:
  print """numpy package not found, rendering of FITS files will not be available.
numpy is available from http://numpy.scipy.org/, or as Debian package python-numpy.
""";
  raise

  
# pylab needed for rendering histograms, but we can get on without it
try:
  import pylab
except:
  print """matplotlib (aka pylab) package not found, rendering of FITS histograms will not be available.
matplotlib is available from http://matplotlib.sourceforge.net/, or as Debian package python-matplotlib.
""";
  pylab = None;
  
import os.path
import traceback
import math

import Purr
from Purr.Render import dprint,dprintf
from Purr.CachingRenderer import CachingRenderer
from Timba import dmi

class FITSRenderer (CachingRenderer):
  """This class renders FITS image data products.""";
  def canRender (filename):
    """We can render it if PIL can read it.""";
    if filename.endswith(".fits") or filename.endswith(".FITS"):
      return 10;
    return False;
  canRender = staticmethod(canRender);
    
  # this gives a short ID for the class (used in GUIs and such)
  renderer_id = "fits";
  
  # this gives a documentation string. You can use rich text here
  renderer_doc = """<P>The "fits" plugin provides rendering of FITS images.""";
      
  # maximum thumbnail width & height
  # define renderer options
  CachingRenderer.addOption("image-thumbnail-width",512,dtype=int,doc="Maximum width of thumbnails");
  CachingRenderer.addOption("image-thumbnail-height",256,dtype=int,doc="Maximum height of thumbnails");
  CachingRenderer.addOption("hist-thumbnail-width",256,dtype=int,doc="Maximum width of thumbnails");
  CachingRenderer.addOption("hist-thumbnail-height",128,dtype=int,doc="Maximum height of thumbnails");
  CachingRenderer.addOption("fits-nimage",4,dtype=int,doc="Maximum number of planes to include, when dealing with cubes");
  CachingRenderer.addOption("fits-hist-nbin",1024,dtype=int,doc="Number of bins to use when making histograms""");
  CachingRenderer.addOption("fits-hist-clip",.95,dtype=float,doc="Apply histogram clipping");
  
  def _renderCacheFile (self,cachetype,relpath):
    return ("-cache-%s-rel-%s.html"%(cachetype,bool(relpath))).lower();
  
  def regenerate (self):
    Purr.progressMessage("reading %s"%self.dp.filename,sub=True);
    # read in data array
    fitsfile = pyfits.open(self.dp.fullpath)
    fitsdata = numpy.array(fitsfile[0].data);
    self.cubesize = 'x'.join(map(str,fitsdata.shape));
    
    # write out FITS header
    self.headerfile,path,uptodate = self.subproduct("-fitsheader.html");
    if not uptodate:
      title = "FITS header for %s"%self.dp.filename;
      html = """<HTML><BODY><TITLE>%s</TITLE>
      <H2>%s</H2>
      <PRE>"""%(title,title);
      hdrcard = fitsfile[0].header.ascard;
      for line in hdrcard:
        line = str(line).replace("<","&lt;").replace(">","&gt;");
        html += line+"\n";
      html += """
      </PRE></BODY></HTML>\n""";
      try:
        file(path,"w").write(html);
      except:
        print "Error writing file %s"%path;
        traceback.print_exc();
        self.headerfile = None;
    # close FITS file
    fitsfile = None;
    
    # figure out number of images to include
    if fitsdata.ndim < 2:
      raise TypeError,"can't render one-dimensional FITS files""";
    elif fitsdata.ndim == 2:
      images = [ fitsdata ];
      shape = fitsdata.shape;
    else:
      shape = fitsdata.shape[-2:];
      # figure out number of planes in the cube
      nplanes = fitsdata.size/(shape[0]*shape[1]);
      # reshape to collapse into a 3D cube
      fitsdata = fitsdata.reshape((nplanes,shape[0],shape[1]));
      nplanes = min(self.getOption('fits-nimage'),nplanes);
      # now extract subplanes
      images = [ fitsdata[i,:,:] for i in range(nplanes) ];
      fitsdata = None;
      
    # OK, now cycle over all images
    dprintf(3,"%s: rendering %d planes\n",self.dp.fullpath,len(images));
    
    self.imgrec = [None]*len(images);
    # get number of bins (0 or None means no histogram)
    nbins = self.getOption("fits-hist-nbin");
    # see if histogram clipping is enabled, set hclip to None if not
    self.hclip = hclip = self.getOption("fits-hist-clip");
    if hclip == 1 or not nbins:
      hclip = None;
      
    tsize_img = self.getOption("image-thumbnail-width"),self.getOption("image-thumbnail-height");
    tsize_hist = self.getOption("hist-thumbnail-width"),self.getOption("hist-thumbnail-height");
    
    for num_image,data in enumerate(images):
      title = self.dp.filename;
      if len(images) > 1:
        title += ", plane #%d"%num_image;
      Purr.progressMessage("rendering %s"%title,sub=True);
        
      # build up record of stuff associated with this image
      rec = self.imgrec[num_image] = dmi.record();
      # min/max data values
      datamin,datamax = float(data.min()),float(data.max());
      rec.datamin,rec.datamax = datamin,datamax;
      # mean and sigma
      rec.datamean = float(data.mean());
      rec.datastd = float((data-rec.datamean).std());
      # relative filenames of histogram plots, or None if none are generated
      # thumbnail files will be "" if images are small enough to be inlined.
      rec.histogram_full = rec.histogram_full_thumb = None;
      rec.histogram_zoom = rec.histogram_zoom_thumb  = None;
      # relative filenames of full image and thumbnail in png format
      # None if not generated
      rec.fullimage = rec.thumbnail = None;
      # these will be None if no histogram clipping is applied
      rec.clipmin,rec.clipmax = None,None;
      dprintf(3,"%s plane %d: datamin %g, datamax %g\n",self.dp.fullpath,num_image,rec.datamin,rec.datamax);
      # compute histogram of data only if this is enabled,
      # and either pylab is available (so we can produce plots), or histogram clipping is in effect
      if nbins and (pylab or hclip):
        dprintf(3,"%s plane %d: computing histogram\n",self.dp.fullpath,num_image);
        counts,edges = numpy.histogram(data,nbins);
        # render histogram
        if pylab:
          rec.histogram_full,path,uptodate = self.subproduct("-%d-hist-full.png"%num_image);
          if not uptodate:
            try:
              pylab.close();
              pylab.plot(edges,counts,linestyle='steps',linewidth=2);
              pylab.title("Histogram of %s"%title);
              pylab.savefig(path);
              pylab.close();
            except:
              print "Error rendering histogram %s"%path;
              traceback.print_exc();
              rec.histogram_full = None;
          # if histogram was rendered, make a thumbnail
          if rec.histogram_full:
            rec.histogram_full_thumb = self.makeThumb(path,"-%d-hist-full-thumb.png"%num_image,tsize_hist);
          else:
            rec.histogram_full_thumb = None;
        # now, compute clipped data if needed
        if hclip:
          # find max point in histogram
          ic = counts.argmax();
          # compute number of points that need to be included, given the clip factor
          target_count = int(data.size*hclip);
          ih0 = ih1 = ic;
          totcount = counts[ic];
          # find how many bins to include around ic, stopping when we hit the edge
          while totcount < target_count:
            if ih0 > 0:
              ih0 -= 1;
              totcount += counts[ih0];
            if ih1 < nbins-1:
              ih1 += 1;
              totcount += counts[ih1];
            # just in case
            if ih0 <= 0 and ih1 >= nbins-1:
              break;
          # and these are the clipping limits
          datamin = float(edges[ih0])
          if ih1 >= nbins-1:
            ih1 = nbins-1;  # and datamax is already the clipping limit
          else:
            ih1 += 1;
            datamax = float(edges[ih1]);
          rec.clipmin,rec.clipmax = datamin,datamax;
          dprintf(3,"%s plane %d: clipping to %g,%g\n",self.dp.fullpath,num_image,rec.clipmin,rec.clipmax);
          # render zoomed histogram
          if pylab:
            rec.histogram_zoom,path,uptodate = self.subproduct("-%d-hist-zoom.png"%num_image);
            if not uptodate:
              try:
                pylab.close();
                pylab.plot(edges[ih0:ih1],counts[ih0:ih1],linestyle='steps',linewidth=2);
                pylab.title("Histogram zoom of %s"%title);
                pylab.savefig(path);
                pylab.close();
              except:
                print "Error rendering histogram %s"%path;
                traceback.print_exc();
                rec.histogram_zoom = None;
            # if histogram was rendered, make a thumbnail
            if rec.histogram_zoom:
              rec.histogram_zoom_thumb = self.makeThumb(path,"-%d-hist-zoom-thumb.png"%num_image,tsize_hist);
            else:
              rec.histogram_zoom_thumb = None;
          # clip data
          data = numpy.clip(data,datamin,datamax);
        # end of clipping
      # ok, data has been clipped if need be. Rescale it to 8-bit integers
      datarng = datamax - datamin;
      if datarng:
        data = (data - datamin)*(255/datarng)
        data = data.round().astype('int16');
      else:
        data = zeros(data.shape,dtype='int16');
      dprintf(3,"%s plane %d: rescaled to %d:%d\n",self.dp.fullpath,num_image,data.min(),data.max());
      # generate PNG image
      rec.fullimage,path,uptodate = self.subproduct("-%d-full.png"%num_image);
      img = None;
      if not uptodate:
        try:
          img = PIL.Image.new('L',data.shape);
          img.putdata(data.reshape((data.size,)));
          img.save(path,'PNG');
        except:
          print "Error rendering image %s"%path;
          traceback.print_exc();
          rec.fullimage = img = None;
      # if image was rendered, make a thumbnail
      if rec.fullimage:
        rec.thumbnail = self.makeThumb(path,"-%d-thumb.png"%num_image,tsize_img,img=img);
      else:
        rec.thumbnail = None;
        
  def makeThumb (self,imagepath,extension,tsize,img=None):
    """makes a thumbnail for the given image.
    imagepath refers to an image file
    img can be an open PIL.Image -- if None, then imagepath is opened
    tsize is a width,height tuple giving the max thumbnail size
    extension is the extension of the thumbnail file 
    """
    thumbpath = imagepath;  # in case exception is raised before we assign it
    try:
      # open image if needed
      if not img:
        img = PIL.Image.open(imagepath);
      # do we need a thumbnail at all, or can the image be inlined?
      width,height = img.size;
      factor = max(width/float(tsize[0]),height/float(tsize[1]));
      if factor <= 1:
        return "";
      # see if thumbnail is up-to-date
      thumbfile,thumbpath,uptodate = self.subproduct(extension);
      if uptodate:
        return thumbfile;
      # generate the thumbnail
      img = img.resize((int(width/factor),int(height/factor)),PIL.Image.ANTIALIAS);
      img.save(thumbpath,"PNG");
      return thumbfile;
    except:
      print "Error rendering thumbnail %s"%thumbpath;
      traceback.print_exc();
      return None;
  
  def _renderSingleImage (self,image,thumb,relpath):
    if image is None or thumb is None:
      return "";
    # else thumbnail is same as full image (because image was small enough), insert directly
    elif not thumb:
      fname = relpath+image;
      return """<IMG SRC="%s" ALT="%s"></IMG>"""%(fname,os.path.basename(image));
    # else return thumbnail linking to full image
    else:
      tname = relpath+thumb;
      fname = relpath+image;
      return """<A HREF="%s"><IMG SRC="%s" ALT="%s"></A>"""%(fname,tname,os.path.basename(image));
  
  def _renderImageRec (self,rec,relpath,include_size=False):
    # get HTML code for image and histograms
    html_image = self._renderSingleImage(rec.fullimage,rec.thumbnail,relpath);
    if rec.histogram_full:
      html_hist_full = self._renderSingleImage(rec.histogram_full,rec.histogram_full_thumb,relpath);
    else:
      html_hist_full = "";
    if rec.histogram_zoom:
      html_hist_zoom = self._renderSingleImage(rec.histogram_zoom,rec.histogram_zoom_thumb,relpath);
    else:
      html_hist_zoom = "";
    # arrange images side-by-side
    html_img = "<TABLE><TR><TD ROWSPAN=2>%s</TD><TD>%s</TD></TR><TR><TD>%s</TD></TR></TABLE>"% \
                      (html_image,html_hist_full,html_hist_zoom);
    # form up comments
    html_cmt = """<TABLE><TR><TD>data range:</TD><TD>%g,%g</TD></TR>"""%(rec.datamin,rec.datamax);
    if include_size:
      html_cmt += """
         <TR><TD>size:</TD><TD>%s</TD></TR>\n"""%self.cubesize;
    html_cmt += """
         <TR><TD>mean:</TD><TD>%g</TD></TR>
         <TR><TD>sigma:</TD><TD>%g</TD></TR>"""%(rec.datamean,rec.datastd);
    if rec.clipmin is not None:
      html_cmt += """
         <TR><TD>clipping:</TD><TD>%g%%</TD></TR>
         <TR><TD>clip range:</TD><TD>%g,%g</TD></TR>"""%(self.hclip*100,rec.clipmin,rec.clipmax);
    html_cmt += """\n
       </TABLE>""";
    return html_img,html_cmt;
  
  def renderLink (self,relpath=""):
    """renderLink() is called to render a link to the DP
    """;
    # return from cache if available
    cachekey,html = self.checkCache('Link',relpath);
    if html is not None:
      return html;
    # else regenerate
    html = CachingRenderer.renderLink(self,relpath);
    if self.headerfile is not None:
      html += """ (<A HREF="%s%s">header</A>)"""%(relpath,self.headerfile);
    # save to cache
    return self.writeCache(cachekey,html);
  
  
  def renderInTable (self,relpath=""):
    """renderInTable() is called to render FITS images in a table""";
    # return from cache if available
    cachekey,html = self.checkCache('InTable',relpath);
    if html is not None:
      return html;
    # else regenerate
    # single image: render as standard cells
    if len(self.imgrec) == 1:
      rec = self.imgrec[0];
      # add header
      html = "    <TR><TD COLSPAN=2>";
      html += self.renderLinkComment(relpath) or "";
      html += "</TD></TR>\n";
      html_img,comment = self._renderImageRec(rec,relpath,include_size=True);
      html += "\n".join([
          "    <TR>",
          "      <TD>%s</TD>"%html_img,
          "      <TD>%s</TD>"%comment,
          "    </TR>\n" ]);
    # multiple images: render a single header row, followed by one row per image
    else:
      # add header
      html = "    <TR><TD COLSPAN=2>";
      html += self.renderLinkComment(relpath);
      # append information on image and end the table row
      html += "\n      <DIV ALIGN=right><P>%s FITS cube, %d planes are given below.</P></DIV></TD></TR>\n"%(self.cubesize,len(self.imgrec));
      # now loop over images and generate a table row for each
      for irec,rec in enumerate(self.imgrec):
        html_img,comment = self._renderImageRec(rec,relpath);
        comment = "<P>Image plane #%d.</P>%s"%(irec,comment);
        html += "\n".join([
            "    <TR>" ,
            "      <TD>%s</TD>"%html_img,
            "      <TD>%s</TD>"%comment, 
            "    </TR>\n" ]);
    return self.writeCache(cachekey,html);
  
  def renderThumbnail (self,relpath=""):
    """renderThumbnail() is called to render a thumbnail of the DP.
    We only render the first image (in case of multiple images)
    """;
    # return from cache if available
    cachekey,html = self.checkCache('Thumbnail',relpath);
    if html is not None:
      return html;
    # else regenerate
    rec = self.imgrec[0];
    html = self._renderSingleImage(rec.fullimage,rec.thumbnail,relpath);
    # save to cache
    return self.writeCache(cachekey,html);

# register ourselves with Purr
import Purr.Render
Purr.Render.addRenderer(FITSRenderer,__name__,__file__);