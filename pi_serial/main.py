from serial import Serial
import time

ser = Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(10)

data1 = "30"

ser.write(data1.encode())
data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 0\n"
ser.write(data.encode())
time.sleep(2)

data = "100 0\n"
ser.write(data.encode())
time.sleep(2)

data = "100 0\n"
ser.write(data.encode())
time.sleep(2)

data = "100 0\n"
ser.write(data.encode())
time.sleep(2)

data = "100 0\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

data = "100 -50\n"
ser.write(data.encode())
time.sleep(2)

time.sleep(1)

ser.readline().decode()

time.sleep(1)

ser.close()
