import os
import time
import multiprocessing
import signal
import sys

# Rogue configurations via Environment Variables
STRESS_CPU = os.getenv("STRESS_CPU", "false").lower() == "true"
STRESS_MEM = os.getenv("STRESS_MEM", "false").lower() == "true"
STRESS_PIDS = os.getenv("STRESS_PIDS", "false").lower() == "true"

MEM_STEP_MB = int(os.getenv("MEM_STEP_MB", "50"))
MEM_SLEEP_SEC = int(os.getenv("MEM_SLEEP_SEC", "2"))

print("🚀 Rogue App Initialized")
print(f"--- Configuration ---")
print(f"STRESS_CPU:  {STRESS_CPU}")
print(f"STRESS_MEM:  {STRESS_MEM} (Step: {MEM_STEP_MB}MB every {MEM_SLEEP_SEC}s)")
print(f"STRESS_PIDS: {STRESS_PIDS}")
print(f"---------------------")

def cpu_stresser():
    print("🔥 CPU Stresser Started (Spinning...)")
    while True:
        pass # Burn cycles

def mem_stresser():
    print("🧠 Memory Stresser Started (Leaking...)")
    memory_hog = []
    while True:
        # Append 1MB strings
        for _ in range(MEM_STEP_MB):
            memory_hog.append(" " * (1024 * 1024))
        print(f"💾 Allocated {len(memory_hog)}MB so far...")
        time.sleep(MEM_SLEEP_SEC)

def pid_stresser():
    print("💣 PID Stresser Started (Forking...)")
    while True:
        try:
            # Fork a child that just sleeps
            pid = os.fork()
            if pid == 0:
                # Child process
                time.sleep(1000)
                os._exit(0)
            else:
                # Parent process
                print(f"👶 Created child PID: {pid}")
                time.sleep(0.1) # Slowly fork to watch it climb
        except OSError as e:
            print(f"🛑 Fork failed: {e}")
            time.sleep(5)

if __name__ == "__main__":
    processes = []
    
    if STRESS_CPU:
        # Start one CPU stresser per available core
        for _ in range(multiprocessing.cpu_count()):
            p = multiprocessing.Process(target=cpu_stresser)
            p.start()
            processes.append(p)
            
    if STRESS_MEM:
        p = multiprocessing.Process(target=mem_stresser)
        p.start()
        processes.append(p)
        
    if STRESS_PIDS:
        p = multiprocessing.Process(target=pid_stresser)
        p.start()
        processes.append(p)

    print("✅ All stressors launched. Monitoring...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping rogue app...")
        for p in processes:
            p.terminate()
        sys.exit(0)
