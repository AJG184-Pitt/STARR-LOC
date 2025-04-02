from serial import Serial
import time

ser = Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(10)

data1 = "100 100\n"
ser.write(data1.encode())
time.sleep(2)

data1 = "200 0\n"
ser.write(data1.encode())
time.sleep(2)

data1 = "0 200\n"
ser.write(data1.encode())
time.sleep(2)

data1 = "-300 -300\n"
ser.write(data1.encode())
time.sleep(2)

time.sleep(1)

ser.readline().decode()

time.sleep(1)

ser.close()
