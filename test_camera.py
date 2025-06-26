import cv2

cap = cv2.VideoCapture(0)  # Try 0, or 1 if you have multiple cameras
if not cap.isOpened():
    print("❌ Could not open camera (/dev/video0)")
    exit(1)

print("✅ Camera opened successfully! Press any key to close the window.")
ret, frame = cap.read()
if ret:
    cv2.imshow('Camera Test', frame)
    cv2.waitKey(0)
else:
    print("❌ Failed to capture image from camera.")

cap.release()
cv2.destroyAllWindows()




