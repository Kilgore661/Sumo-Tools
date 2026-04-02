from src.infra.live_store.api import get_history
from time import time
t0 = time()
h = get_history()
#from pdb import set_trace; set_trace()
dates = list( h.keys() )
print( f'{len(h)} basho, {dates[0]} to {dates[-1]}' )
