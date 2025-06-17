import cv2
import time
from vision.cup_detector import CupDetector
from robot.dofbot_controller import DOFBOTController

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Initialize cup detector
    detector = CupDetector(model_path="path/to/yolo/weights.weights")
    
    # Initialize DOFBOT controller
    robot = DOFBOTController()
    if not robot.connect():
        print("Error: Could not connect to DOFBOT")
        return

    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Detect cups
            cup_positions = detector.get_cup_positions(frame)
            
            # Display frame with detections
            cv2.imshow('Cup Detection', frame)
            
            # Check for exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # TODO: Implement stacking sequence
            # 1. Detect initial cup stack
            # 2. Plan stacking sequence
            # 3. Execute stacking sequence
            # 4. Return to initial configuration

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        robot.disconnect()

if __name__ == "__main__":
    main() 