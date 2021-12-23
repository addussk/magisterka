import serial
import serial.tools.list_ports as list_ports
from time import sleep

ports = list_ports.comports()

for port in ports:
    print(port)

if len(ports) == 0:
    print("Couldn't find any ports")
    exit(1)

# For now we only expect one port to be available
host_port = ports[0]


print(host_port.device)
print("Found host port: {}".format(host_port.device))

ser = serial.Serial(
    host_port.device, 
    9600, 
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
    write_timeout=1,
)

try:
    ser.write(b'C.1_')
except:
    print("Write timeout. Continue...")

while True:
    # Wait until there is data waiting in the serial buffer
    if ser.in_waiting > 0:
        # Read data out of the buffer until a carraige return / new line is found
        serialString = ser.readline()

        # Print the contents of the serial data
        try:
            print(serialString.decode("Ascii"))
            if serialString.decode("Ascii")[:2] == "@.":
                print("ustawienie sie powiodlo\n")
                break
            else:
                print("Cos poszlo nie tak: {} \n".format(serialString.decode("Ascii")))
        except:
            raise Exception("Transmission error while reading msg via UART")