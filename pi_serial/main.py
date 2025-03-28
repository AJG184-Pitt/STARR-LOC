from serial import Serial
import time

ser = Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(0.5)

data = "30 30\n"

ser.write(data.encode())

time.sleep(0.5)

ser.close()
