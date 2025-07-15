#!/usr/bin/env python3
"""
Fix smbus import issue for Arm_Lib
"""

import sys
import os

# Add smbus2 as smbus for compatibility
try:
    import smbus2 as smbus
    sys.modules['smbus'] = smbus
    print("✅ smbus compatibility fixed")
except ImportError:
    print("❌ smbus2 not available")

# Now try to import Arm_Lib
try:
    from Arm_Lib import Arm_Device
    print("✅ Arm_Lib imported successfully")
    
    # Test creating Arm_Device
    arm = Arm_Device()
    print("✅ Arm_Device created successfully")
    
except Exception as e:
    print(f"❌ Error importing Arm_Lib: {e}") 