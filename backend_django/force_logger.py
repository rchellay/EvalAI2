#!/usr/bin/env python3
"""
Force logs to appear in Render by writing to stdout and stderr
"""

import sys
import datetime

def force_log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {level}: {message}"
    
    # Write to stdout (appears in Render logs)
    print(log_msg, flush=True)
    
    # Write to stderr (also appears in Render logs)
    sys.stderr.write(log_msg + "\n")
    sys.stderr.flush()
    
    # Try writing to a file that might be accessible
    try:
        with open("/tmp/evalai_debug.log", "a") as f:
            f.write(log_msg + "\n")
            f.flush()
    except:
        pass

# Test function
if __name__ == "__main__":
    force_log("Testing force log function")
    force_log("This should appear in Render logs", "DEBUG")
    force_log("Error test", "ERROR")