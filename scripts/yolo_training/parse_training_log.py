#!/usr/bin/env python3
"""
Parse YOLO training output and extract key metrics
Usage: ./darknet detector train ... | python3 parse_training_log.py
"""

import sys
import re
from datetime import datetime

def parse_training_line(line):
    """Parse a training output line and extract metrics"""
    # Pattern for training lines: "1: loss = 5.123 (avg loss = 5.123) ..."
    pattern = r'(\d+):\s+loss\s*=\s*([\d.]+)\s*\(avg\s+loss\s*=\s*([\d.]+)\)'
    match = re.search(pattern, line)
    
    if match:
        iteration = int(match.group(1))
        loss = float(match.group(2))
        avg_loss = float(match.group(3))
        return iteration, loss, avg_loss
    
    # Pattern for mAP lines: "mean average precision (mAP@0.50) = 0.123"
    map_pattern = r'mean average precision \(mAP@0\.50\)\s*=\s*([\d.]+)'
    map_match = re.search(map_pattern, line)
    
    if map_match:
        mAP = float(map_match.group(1))
        return None, None, None, mAP
    
    return None, None, None, None

def main():
    print("YOLO Training Monitor")
    print("=" * 50)
    
    best_loss = float('inf')
    best_map = 0.0
    
    try:
        for line in sys.stdin:
            line = line.strip()
            
            # Parse training metrics
            result = parse_training_line(line)
            
            if len(result) == 3:  # Training iteration
                iteration, loss, avg_loss = result
                if iteration is not None:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Track best loss
                    if loss < best_loss:
                        best_loss = loss
                        loss_status = "NEW BEST!"
                    else:
                        loss_status = ""
                    
                    print(f"[{timestamp}] Iter {iteration:4d} | Loss: {loss:6.3f} | Avg: {avg_loss:6.3f} {loss_status}")
            
            elif len(result) == 4:  # mAP result
                iteration, loss, avg_loss, mAP = result
                if mAP is not None:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Track best mAP
                    if mAP > best_map:
                        best_map = mAP
                        map_status = "NEW BEST!"
                    else:
                        map_status = ""
                    
                    print(f"[{timestamp}] mAP@0.50: {mAP:.3f} {map_status}")
                    print("-" * 50)
            
            # Print other important lines
            elif "Saving weights" in line:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
            elif "Error" in line or "error" in line:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {line}")
            
            sys.stdout.flush()
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        print(f"Best loss achieved: {best_loss:.3f}")
        print(f"Best mAP achieved: {best_map:.3f}")

if __name__ == "__main__":
    main() 