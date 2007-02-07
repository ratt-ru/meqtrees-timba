
import Meow.LMDirection

class NaughtyDirection (Meow.LMDirection):
  def n (self,dir0=None):
    """Returns 'n' coordinate for this direction.
    We're naughty so we always return 1.
    """;
    n = self.ns.n;
    if not n.initialized():
      n << 1;
    return n;
 
