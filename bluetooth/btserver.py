from bluedot.btcomm import BluetoothServer
import signal
import io

import os

current_file = None

os.path.append("../bluetooth")


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
                name = current_file.name
                if os.path.basename(name) == "tle.data":
                    os._exit(0)  # Exit the program if we are done with TLE data
                else:
                    current_file.close()
                    current_file = None

        elif current_file:
            #print("switch_4")
            current_file.write(line)
            current_file.flush()

        else:
            print("No active file to write to\n")
   

def alarm_handler(signum, frame):
    print("Alarm handler called")
    if current_file:
        current_file.close()
    
    print("Bluetooth server stopped")
    os._exit(0)

# Start alarm to kill server after 60 seconds
print("Starting Bluetooth server")
signal.signal(signal.SIGALRM, alarm_handler)
signal.alarm( 30 )

# Start the server and wait for a connection
s = BluetoothServer(data_received)
signal.pause()
