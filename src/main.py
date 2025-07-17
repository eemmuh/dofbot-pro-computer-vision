import cv2
import time
from vision.cup_detector import CupDetector
from robot.dofbot_controller import DOFBOTController
from robot.stacking_controller import StackingController

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Initialize cup detector with trained YOLO model
    # Update this path to your trained model weights
    model_path = "backup/yolo-cup-memory-optimized_final.weights"  # After training
    detector = CupDetector(model_path=model_path, conf_threshold=0.5)
    
    # Initialize DOFBOT controller with auto-detection
    print("Initializing DOFBOT controller...")
    robot = DOFBOTController()
    
    if not robot.connect():
        print("❌ Error: Could not connect to DOFBOT")
        print("Please check:")
        print("1. DOFBOT is connected via USB")
        print("2. DOFBOT is powered on")
        print("3. DOFBOT is in operation mode")
        print("4. Run 'python3 test_dofbot_connection.py' to test connection")
        return

    print("✅ DOFBOT connected successfully!")
    
    # Initialize stacking controller
    print("Initializing stacking controller...")
    stacker = StackingController(robot)
    print("✅ Stacking controller ready!")
    print("Cup Stacking System Ready!")
    print("Press 'q' to quit, 's' to start stacking sequence")

    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Detect cups
            detections = detector.detect_cups(frame)
            cup_positions = detector.get_cup_positions(frame)
            
            # Draw detections on frame
            frame_with_detections = detector.draw_detections(frame.copy(), detections)
            
            # Display cup count
            cv2.putText(frame_with_detections, f"Cups detected: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display frame with detections
            cv2.imshow('Cup Detection - YOLOv4', frame_with_detections)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and len(cup_positions) > 0:
                print(f"Starting stacking sequence with {len(cup_positions)} cups...")
                try:
                    stacker.execute_stack_sequence(cup_positions)
                except Exception as e:
                    print(f"❌ Stacking sequence failed: {e}")

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        robot.disconnect()
        print("System shutdown complete")

if __name__ == "__main__":
    main() 

    