from serial import Serial
import time

ser = Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(10)

data = "10 10\n"
ser.write(data.encode())
time.sleep(2)

data = "20 20\n"
ser.write(data.encode())
time.sleep(2)

data = "30 30\n"
ser.write(data.encode())
time.sleep(2)

data = "40 40\n"
ser.write(data.encode())
time.sleep(2)

data = "50 50\n"
ser.write(data.encode())
time.sleep(2)

data = "60 60\n"
ser.write(data.encode())
time.sleep(2)

data = "70 70\n"
ser.write(data.encode())
time.sleep(2)

data = "80 80\n"
ser.write(data.encode())
time.sleep(2)

data = "70 70\n"
ser.write(data.encode())
time.sleep(2)

data = "60 60\n"
ser.write(data.encode())
time.sleep(2)

data = "50 50\n"
ser.write(data.encode())
time.sleep(2)

data = "40 40\n"
ser.write(data.encode())
time.sleep(2)

data = "30 30\n"
ser.write(data.encode())
time.sleep(2)

data = "20 20\n"
ser.write(data.encode())
time.sleep(2)

data = "10 10\n"
ser.write(data.encode())
time.sleep(2)

data = "0 0\n"
ser.write(data.encode())
time.sleep(2)

time.sleep(1)

ser.readline().decode()

time.sleep(1)

ser.close()
