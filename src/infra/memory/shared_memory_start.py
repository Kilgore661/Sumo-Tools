# Shared memory for elo test program.
# Run from src with:
#     py -m infrastructure.memory.shared_memory_start

from multiprocessing import shared_memory
from sandpit.GTB.optimisation.others2.infrastructure.persistence.new_sumo_serialiser import load_history_with_annotations
import pickle
import sys
from time import time
t0 = time()
print('Loading ...', end=' ', flush=True)
h = load_history_with_annotations('_files/output_fsm/histories_with_annotations/1958_01 to 2025_11')
print(f'Done.')# Size in memory: ', end='', flush=True)

# Serialize the history object
serial = pickle.dumps(h)
#print(f'{len(serial)/1000:.2f}K')

try:
    # Test deserialization to make sure it works
    #print('Testing deserialization...', end=' ', flush=True)
    test_unpickle = pickle.loads(serial)
    #print('Success!')
    
    # Create shared memory with enough space for the serialized data
    print('Creating shared memory...', end=' ', flush=True)
    shm = shared_memory.SharedMemory(name='history3', create=True, size=len(serial))
    print(f'Done! ({time()-t0:.0f}s)')
    
    # Write the serialized data to shared memory
    shm.buf[:len(serial)] = serial
    
    # Print shared memory information
    if 0:
        print(f"Shared memory successfully created.")
        print(f"Name: {shm.name}")
        print(f"Size: {shm.size/1000:.2f}K")
        print("\nAny process can now access this data using:")
        print("from multiprocessing import shared_memory")
        print("import pickle")
        print("shm = shared_memory.SharedMemory(name='history2')")
        print("history = pickle.loads(bytes(shm.buf))")
    
    # Keep running so the memory stays accessible
    input("\nPress Enter to release memory and exit...")
    
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up resources
    if 'shm' in locals():
        shm.close()
        shm.unlink()
