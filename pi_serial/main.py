from serial import Serial
import time

ser = Serial('dev/ttyACM0', 9600, timeout=1)
time.sleep(1)

data = "3.5 4.7\n"

ser.write(data.encode())

time.sleep(1)

ser.close()
