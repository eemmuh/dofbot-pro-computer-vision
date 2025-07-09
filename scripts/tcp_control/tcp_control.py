import socket
import time

# Change this to your Jetson's IP if running from another machine
HOST = "127.0.0.1"  # or "35.50.62.89"
PORT = 6000

def send_command(cmd):
    print(f"Sending: {cmd.strip()}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(cmd.encode())
        # Optional: receive response
        try:
            data = s.recv(1024)
            print("Received:", data.decode())
        except Exception:
            pass

if __name__ == "__main__":
    # Example: Move to home position (replace with real command for your robot)
    send_command("home\n")
    time.sleep(1)
    # Example: Move servo 1 to 90 degrees (replace with real command)
    send_command("servo1:90\n")
    time.sleep(1)
    # Add more commands as needed 