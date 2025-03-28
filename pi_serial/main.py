from serial import Serial
import time

ser = Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(20)

data1 = "30\n"
ser.write(data1.encode())

time.sleep(1)

data2 = "30\n"
ser.write(data2.encode)

time.sleep(1)

ser.readline().decode()

time.sleep(1)

ser.close()
