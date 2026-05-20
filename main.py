import os
import time
import multiprocessing
import signal
import sys

# Ensure unbuffered output for Docker logs
sys.stdout.reconfigure(line_buffering=True)

# Rogue configurations via Environment Variables
STRESS_CPU = os.getenv("STRESS_CPU", "false").lower() == "true"
STRESS_MEM = os.getenv("STRESS_MEM", "false").lower() == "true"
STRESS_PIDS = os.getenv("STRESS_PIDS", "false").lower() == "true"

MEM_STEP_MB = int(os.getenv("MEM_STEP_MB", "50"))
MEM_SLEEP_SEC = int(os.getenv("MEM_SLEEP_SEC", "2"))

print("🚀 Rogue App Initialized", flush=True)
print(f"--- Configuration ---", flush=True)
print(f"STRESS_CPU:  {STRESS_CPU}", flush=True)
print(f"STRESS_MEM:  {STRESS_MEM} (Step: {MEM_STEP_MB}MB every {MEM_SLEEP_SEC}s)", flush=True)
print(f"STRESS_PIDS: {STRESS_PIDS}", flush=True)
print(f"---------------------", flush=True)

def cpu_stresser():
    print("🔥 CPU Stresser Started (Spinning...)", flush=True)
    try:
        while True:
            pass # Burn cycles
    except Exception as e:
        print(f"❌ CPU Stresser Failed: {e}", flush=True)

def mem_stresser():
    print("🧠 Memory Stresser Started (Leaking...)", flush=True)
    memory_hog = []
    try:
        while True:
            # Append 1MB strings
            for _ in range(MEM_STEP_MB):
                memory_hog.append(" " * (1024 * 1024))
            print(f"💾 Allocated {len(memory_hog)}MB so far...", flush=True)
            time.sleep(MEM_SLEEP_SEC)
    except MemoryError:
        print("🛑 MemoryError caught in child!", flush=True)
    except Exception as e:
        print(f"❌ Memory Stresser Unexpected Failure: {e}", flush=True)

def pid_stresser():
    print("bomb PID Stresser Started (Forking...)", flush=True)
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
                # print(f"child Created child PID: {pid}", flush=True)
                time.sleep(0.1) # Slowly fork to watch it climb
        except OSError as e:
            print(f"🛑 Fork failed: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    processes = []
    
    if STRESS_CPU:
        for _ in range(multiprocessing.cpu_count()):
            p = multiprocessing.Process(target=cpu_stresser, name="CPU-Stresser")
            p.start()
            processes.append(p)
            
    if STRESS_MEM:
        p = multiprocessing.Process(target=mem_stresser, name="MEM-Stresser")
        p.start()
        processes.append(p)
        
    if STRESS_PIDS:
        p = multiprocessing.Process(target=pid_stresser, name="PID-Stresser")
        p.start()
        processes.append(p)

    print("✅ All stressors launched. Monitoring children...", flush=True)
    
    try:
        while True:
            # Check if any child died
            for p in processes:
                if not p.is_alive():
                    print(f"⚠️ Process {p.name} (PID {p.pid}) has terminated! Exit code: {p.exitcode}", flush=True)
                    if p.exitcode == -signal.SIGKILL:
                        print(f"🚨 ALERT: Process {p.name} was likely KILLED by OOM Killer!", flush=True)
                    # Remove it from monitoring to stop spamming
                    processes.remove(p)
            
            if not processes:
                print("💀 All stressors have died. Rogue app idle.", flush=True)
                break
                
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Stopping rogue app...", flush=True)
        for p in processes:
            p.terminate()
        sys.exit(0)
    
    # Stay alive so the container doesn't restart immediately
    while True:
        time.sleep(10)
