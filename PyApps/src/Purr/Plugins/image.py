try:
  import PIL.Image
except:
  print """Please install the Python Imaging Library (PIL)!
Purr will work fine without it, but your logs will be a lot less beautifully rendered.
PIL is available from http://www.pythonware.com/products/pil/. On Debian-based systems
(including Ubuntu and such), it can be as simple as installing the python-imaging package.""";
  raise
  
import os.path
import traceback
import sets

from Purr.Render import DefaultRenderer

class ImageRenderer (DefaultRenderer):
  """This class renders PIL-compatible image data products.""";
  _extensions = sets.Set([
    "jpg","jpeg","png","gif","xpm","ppm","pbm","pnm","tiff","tif"
  ]);
  
  def canRender (filename):
    """Check extensions.""";
    name,ext = os.path.splitext(filename);
    ext = ext.lstrip('.').lower();
    if ext in ImageRenderer._extensions:
      return 100;
    else:
      return False;
  canRender = staticmethod(canRender);
    
  # this gives a short ID for the class (used in GUIs and such)
  renderer_id = "image";
  
  # this gives a documentation string. You can use rich text here
  renderer_doc = """<P>The "image" plugin provides rendering of image-type data products.
      It can render any image that is compatible with the Python Image Library.""";
      
  # define renderer options
  DefaultRenderer.addOption("image-thumbnail-width",512,dtype=int,doc="Maximum width of thumbnails");
  DefaultRenderer.addOption("image-thumbnail-height",256,dtype=int,doc="Maximum height of thumbnails");
  
  def __init__ (self,dp,**kw):
    DefaultRenderer.__init__(self,dp,**kw);
    Purr.progressMessage("rendering %s"%dp.filename,sub=True);
    img = PIL.Image.open(dp.fullpath);
    # If image format is not compatible with browsers, save it in PNG format.
    # self.fullimage will refer to the browser-compatible image, to which the thumbnail will link
    if img.format not in ["GIF","JPEG","PNG"]:
      self.fullimage,path,uptodate = self.subproduct("-full.png");
      if not uptodate:
        try:
          img.save(path,"PNG");
        except:
          print "Error saving %s in PNG format"%path;
          traceback.print_exc();
          self.fullimage = dp.filename;
    else:
      self.fullimage = dp.filename;
    # now, do we need to generate a thumbnail?
    tsize = self.getOption("image-thumbnail-width"),self.getOption("image-thumbnail-height");
    width,height = img.size;
    factors = width/float(tsize[0]),height/float(tsize[1]);
    if max(factors) <= 1:
      self.thumbnail = self.fullimage;
    else:
      # regenerate thumbnail if needed
      self.thumbnail,path,uptodate = self.subproduct("-thumb.png");
      try:
        # regenerate only if doesn't exist
        if not uptodate:
          # use max resize factor
          factor = max(factors);
          img = img.resize((int(width/factor),int(height/factor)),PIL.Image.ANTIALIAS);
          img.save(path,"PNG");
      except:
        print "Error saving thumbnail %s in PNG format"%path;
        traceback.print_exc();
        self.thumbnail = None;
  
  def renderThumbnail (self,relpath=""):
    """renderThumbnail() is called to render a thumbnail of the DP (e.g. in Data Product tables).""";
    # no thumbnail -- return empty string
    if self.thumbnail is None:
      return "";
    # else thumbnail is same as full image (because image was small enough), insert directly
    elif self.thumbnail is self.fullimage:
      fname = relpath+self.fullimage;
      return """<IMG SRC="%s" ALT="%s"></IMG>"""%(fname,os.path.basename(self.filename));
    # else return thumbnail linking to full image
    else:
      tname = relpath+self.thumbnail;
      fname = relpath+self.fullimage;
      return """<A HREF="%s"><IMG SRC="%s" ALT="%s"></A>"""%(fname,tname,os.path.basename(self.filename));

# register ourselves with Purr
import Purr.Render
Purr.Render.addRenderer(ImageRenderer,__name__,__file__);