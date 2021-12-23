import serial.tools.list_ports as port_list
import serial
import time


class LTDZ():
    
    com_port = "INVALID"
    
    def find_device(self):
        # znalezienie wszystkich podlaczonych portow
        ports = list(port_list.comports())
        available_coms = list()

        # uporzadkowanie nazwy kazdego wykrytego portu
        for p in ports:
            available_coms.append(str(p).split(" "))

        # znalezienie portu do ktorego wpiete jest urzadzenie
        for com in available_coms:
            if com[3] == "CH340":
                self.com_port = com[0]

    def config_serial(self, in_baudrate=9600, in_bytesize=8, in_timout=2, in_stopbits=serial.STOPBITS_ONE):

        if self.com_port.upper() == "INVALID":
            raise Exception("Error with COM transmision")

        return serial.Serial(
            port=self.com_port, baudrate=in_baudrate, bytesize=in_bytesize, timeout=in_timout, stopbits=in_stopbits
        )

    def send_command(self, in_command, in_serialPort):
        serialString = ""  # Buffor dla wiadomosci zwrotnej
        timeout_counter = 5 # ilosc sekund dla informacji zwrotnej od syntezatora

        in_serialPort.write(str.encode(in_command)) 
         
        while timeout_counter:
            # Wait until there is data waiting in the serial buffer
            if in_serialPort.in_waiting > 0:
                # Read data out of the buffer until a carraige return / new line is found
                serialString = in_serialPort.readline()

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
            else:
                time.sleep(1)
                timeout_counter-=1
        
        if not timeout_counter:
            raise Exception("Error: ACK didn't receive")

    def turn_chip_on(self, in_serialPort):
        self.send_command("C.1_", in_serialPort)

    def turn_chip_off(self, in_serialPort):
        self.send_command("C.0_", in_serialPort)
    
    def turn_RF_out_on(self, in_serialPort):
        self.send_command("R.1_", in_serialPort)

    def turn_RF_out_off(self, in_serialPort):
        self.send_command("R.0_", in_serialPort)
 
    def set_power(self, in_serialPort, in_power):
        if (in_power > 4) or (in_power is None):
            raise Exception("Warning: Parametr mocy jest zbyt duzy, wybierz z zakresu 0-3")

        self.send_command("P.{}_".format(in_power), in_serialPort)

    def set_freq(self, in_serialPort, in_freq):
        if (in_freq is None) or (len(str(in_freq)) > 10):
            raise Exception("Warning: Wartosc czestotliwosci jest zbyt duza, zakres 10cyft")

        self.send_command("R.{}_".format(in_freq), in_serialPort)

x = LTDZ()

x.find_device()

# x.turn_RF_out_off(x.config_serial())

# x.turn_chip_on(x.config_serial())

# x.turn_RF_out_on(x.config_serial())

# x.set_power(x.config_serial(), 0)

# x.set_freq(x.config_serial(), 102000000)





