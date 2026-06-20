"""CLI shim for support-domain fixed-point sandbox runs."""
from time import time
t0=time()

from .run import main


if __name__ == "__main__":
    main()
    print( f'{time()-t0:.0f} sec.' )
