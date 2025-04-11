import psutil
import re

def find_chrome_debug_ports():
    debug_instances = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    # Look for --remote-debugging-port argument
                    for i, arg in enumerate(cmdline):
                        if '--remote-debugging-port' in arg:
                            # Extract port number using regex
                            if '=' in arg:
                                port = arg.split('=')[1]
                            else:
                                # Check next argument for port number
                                port = cmdline[i + 1]
                            debug_instances.append({
                                'pid': proc.info['pid'],
                                'port': port,
                                'command': ' '.join(cmdline)
                            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return debug_instances

# Usage
debug_instances = find_chrome_debug_ports()
if debug_instances:
    print("Chrome instances running in debug mode:")
    for instance in debug_instances:
        print(f"PID: {instance['pid']}, Debug Port: {instance['port']}")
else:
    print("No Chrome instances running in debug mode found")
