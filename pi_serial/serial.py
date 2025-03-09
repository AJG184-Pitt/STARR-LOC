import serial
import time

ser = serial.Serial('dev/tty/ACM0', 9600, timeout=1)
time.sleep(2)

data = "3.5 4.7"

ser.write(data.encode())

time.sleep(2)

ser.close()
