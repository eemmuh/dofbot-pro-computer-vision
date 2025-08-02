#!/usr/bin/env python3
"""
Create a simple cup stacking notebook
"""

import json

def create_simple_notebook():
    """Create a simple notebook"""
    
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Cup Stacking Robot\n",
                    "\n",
                    "This notebook runs your cup stacking system with your trained YOLO model."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Import required modules\n",
                    "import sys\n",
                    "import os\n",
                    "sys.path.append('src')\n",
                    "\n",
                    "print('Cup Stacking System Starting...')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Test imports\n",
                    "try:\n",
                    "    from vision.cup_detector import CupDetector\n",
                    "    print('✅ Cup detector imported')\n",
                    "except ImportError as e:\n",
                    "    print(f'❌ Import error: {e}')\n",
                    "\n",
                    "try:\n",
                    "    from robot.dofbot_controller import DOFBOTController\n",
                    "    print('✅ Robot controller imported')\n",
                    "except ImportError as e:\n",
                    "    print(f'❌ Import error: {e}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Initialize YOLO detector\n",
                    "model_path = 'backup/yolo-cup-memory-optimized_final.weights'\n",
                    "\n",
                    "if os.path.exists(model_path):\n",
                    "    print(f'✅ YOLO model found: {model_path}')\n",
                    "    detector = CupDetector(model_path=model_path, conf_threshold=0.5)\n",
                    "    print('✅ YOLO detector initialized')\n",
                    "else:\n",
                    "    print(f'❌ YOLO model not found: {model_path}')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Test camera\n",
                    "import cv2\n",
                    "\n",
                    "camera = cv2.VideoCapture(0)\n",
                    "if camera.isOpened():\n",
                    "    print('✅ Camera connected')\n",
                    "    ret, frame = camera.read()\n",
                    "    if ret:\n",
                    "        print(f'✅ Frame captured: {frame.shape}')\n",
                    "    else:\n",
                    "        print('❌ Could not read frame')\n",
                    "    camera.release()\n",
                    "else:\n",
                    "    print('❌ Camera not connected')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Simple cup stacking demo\n",
                    "print('🎮 Cup Stacking Demo Ready!')\n",
                    "print('Run the cells above to test your system.')\n",
                    "print('Your trained YOLO model will detect cups automatically.')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    return notebook

def main():
    """Create the notebook"""
    print("Creating simple notebook...")
    
    notebook = create_simple_notebook()
    
    with open('cup-stacking-move.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print("✅ Simple notebook created: cup-stacking-move.ipynb")

if __name__ == "__main__":
    main() 