import serial
import time

# Configure serial port
port = "/dev/ttyACM0"  # Change to your Arduino port (e.g., "/dev/ttyUSB0" on Linux or "COM3" on Windows)
baudrate = 9600  # Match with your Arduino sketch

try:
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"Connected to {port} at {baudrate} baud.")
    
    # Open a file to write the output
    with open("MPU_9250_cal_data_3_28_2025.txt", "w") as file:
        while True:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').strip()
                print(data)  # Print to console
                file.write(data + "\n")
                file.flush()  # Save data to file in real-time
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nLogging stopped by user.")
finally:
    ser.close()
