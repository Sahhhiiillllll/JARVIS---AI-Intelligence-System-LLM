import subprocess
import time
import os
import sys

log_file = 'frontend.log'
pid_file = 'server.pid'

# Open log file for writing
with open(log_file, 'w') as log:
    # Start the server
    proc = subprocess.Popen([sys.executable, '-m', 'http.server', '8080'],
                            stdout=log, stderr=subprocess.STDOUT)
    # Write PID
    with open(pid_file, 'w') as f:
        f.write(str(proc.pid))

# Wait a bit
time.sleep(2)

# Check if process is still running
if proc.poll() is None:
    running = True
else:
    running = False

# Output PID
print(proc.pid)

# Output ps output
try:
    ps_output = subprocess.check_output(['ps', '-p', str(proc.pid)], text=True, stderr=subprocess.STDOUT)
    print(ps_output.strip())
except subprocess.CalledProcessError as e:
    print(f"Process {proc.pid} not found: {e.output}")

# Tail last 5 lines of log file
try:
    with open(log_file, 'r') as f:
        lines = f.readlines()
        last_five = ''.join(lines[-5:]) if len(lines) >= 5 else ''.join(lines)
        print(last_five, end='')
except FileNotFoundError:
    print("Log file not found")
