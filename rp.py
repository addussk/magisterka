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
# host_port = ports[2]

# print("Found host port: {}".format(host_port.device))

# ser = serial.Serial(
#     host_port.device, 
#     9600, 
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS,
#     timeout=1,
#     write_timeout=1,
# )

# while True:
#     print("writing")
#     try:
#         ser.write(b'hello')
#     except:
#         print("Write