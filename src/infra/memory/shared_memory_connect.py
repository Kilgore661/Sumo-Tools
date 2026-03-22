from multiprocessing import shared_memory
import pickle
import sys
from .version import VERSION
from time import time
def connect():
    try:
        shm = shared_memory.SharedMemory(name=f'history{VERSION}')
        print("Loading annotated history from shared memory ... ", end='', flush=True)
        t0=time()
        history = pickle.loads(bytes(shm.buf))
        print(f"Success in {time()-t0:.2f}s")
        
        return history
        
    except FileNotFoundError:
        print(f"\n\n\nError: Shared memory segment 'history{VERSION}' not found.")
        print("py -m infra.memory.shared_memory_start\n\n")
        return None
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'shm' in locals():
            shm.close()

if __name__ == '__main__':
    h = connect()
    if h:
        print( f"Connected to 'history{VERSION}'" )
