from bluedot.btcomm import BluetoothServer
from signal import pause
import io

import sys

current_file = None


def data_received(data):
    
    global current_file
    text = io.StringIO(data)
    

    while True:
        line = text.readline()
        if not line:
            break

        #print(line)

        if (line == "GPS DATA\n"):
            #print("switch 1\n")
            if current_file:
                current_file.close()
            current_file= open("gps.data", "w")

        elif (line == "TLE DATA\n"):
            #print("switch 2\n")
            if current_file:
                current_file.close()
            current_file = open("tle.data", "w")
    
        elif (line == "END\n"):
            #print("switch_3\n")
            if current_file:
                current_file.close()
            current_file = None

        elif current_file:
            #print("switch_4")
            current_file.write(line)
            current_file.flush()

        else:
            print("No active file to write to\n")
   

print("Starting Bluetooth server")
s = BluetoothServer(data_received)
pause()
