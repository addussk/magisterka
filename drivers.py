#common
import time
import random
#libs potrzebne dla LTDZ
import serial.tools.list_ports as port_list
import serial
#adc
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("Warning: read by ADC is not possible")
#hmc
import digitalio

#Syntezator czestotliwosci
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
            print(com)
            if com[-2] == "CH340" or com[0] == "/dev/ttyUSB0":
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
        
        if (len(str(in_freq)) == 10):
            self.send_command("F.{}".format(in_freq), in_serialPort)
        else:
            self.send_command("F.{}_".format(in_freq), in_serialPort)

    #kod do testow klasy
    def test():
        x = LTDZ()

        x.find_device()

        # x.turn_RF_out_off(x.config_serial())

        # x.turn_chip_off(x.config_serial())

        x.turn_chip_on(x.config_serial())

        x.turn_RF_out_on(x.config_serial())

        x.set_power(x.config_serial(), 2)

        x.set_freq(x.config_serial(), 102000000)

try:
    # powoduje wyswietlenie warningu: The system cannot find the path specified na PC
    from w1thermsensor import W1ThermSensor
except:
    print("w1thermsensor didn't include")
class DS1820():

    def read_temp(self):
        # odczyt temperatury dziala przy podlaczeniu odpowiedniego czujnika, w innym przypadku dane zostana wygenerowane
        try:
            sensor = W1ThermSensor()
            temp = sensor.get_temperature()
            print("read temp function:")
            print(temp)
            return temp
        except:
            sum, in_min_temp, in_max_temp =0, 0, 100

            for x in range(5):
                sum += round(random.uniform(in_min_temp, in_max_temp), 1)

            return int(sum/5)


class ADC_driver():
    voltage = None
    raw_value = None

    def __init__(self) -> None:
        # libs need by ADC driver, check if it available if not raise Exception.
        try:
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn
        except:
            raise Exception("Warning: read by ADC is not possible")

    # funckja do odczytu napiecia z czujnika via I2C
    def read_voltage(self):
        # def adc_measurement():
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        #Single Ended Mode
        chan = AnalogIn(ads, ADS.P0)
        print(chan.value, chan.voltage)

        self.voltage = chan.voltage
        self.raw_value = chan.value

        return chan.voltage

class HMC624():
    # General information: remember to set P/S pin to high to enable serial mode interface    
    ATTENUATION = {
        32 : 0b000000,
        16 : 0b011111,
        8 : 0b101111,
        4 : 0b110111,
        2 : 0b111011,
        1 : 0b111101,
        0.5 : 0b111110,
        0 : 0b111111,
    }

    RECEIVER_BUFFER_SIZE = 1 # Number of bytes
    LAST_MSGS = bytearray(RECEIVER_BUFFER_SIZE+1) # buffor to hold last received msg
    spiDriver = None  # pointer to SPI object from busio libs
    le = None # pointer to object represent gpio pin represents latch enable pin

    def __init__(self) -> None:
        # create the spi bus
        self.spiDriver = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # create the LE (latch pin)
        self.le = digitalio.DigitalInOut(board.CE0)
        self.le.direction = digitalio.Direction.OUTPUT
        self.le.value = True # high level set on pin disenables configuration of attenuation
        # configuration of SPI 
        self.configureSpi()
    
    def configureSpi(self, inBaudrate=10000000, inPhase=0, inPolarity=0):
        while not self.spiDriver.try_lock():
            pass
        try:
            self.spiDriver.configure(baudrate=inBaudrate, phase=inPhase, polarity=inPolarity)

        finally:
            self.spiDriver.unlock()

    def write(self, msg):
        if type(msg) != type(list()):
            raise Warning("Only array should be pass")
        
        while not self.spiDriver.try_lock():
            pass
        
        try:
            # low level allow to write data inside register
            self.le.value = False

            self.spiDriver.write(bytes(msg))

            #LE must be toggled high to latch the new attenuation state into the device. 
            self.le.value = True
        finally:
            self.spiDriver.unlock()

    def read(self):
        receivedBuffer = bytearray(self.RECEIVER_BUFFER_SIZE)

        while not self.spiDriver.try_lock():
            pass
        
        try:
            # low level allow to write data inside register
            self.le.value = False

            self.spiDriver.readinto(receivedBuffer)

            #LE must be toggled high to latch the new attenuation state into the device. 
            self.le.value = True
        finally:
            self.spiDriver.unlock()

        self.LAST_MSGS = receivedBuffer

        return receivedBuffer
    
    # att value in dB
    def setAttenuation(self, att):
        if att not in self.ATTENUATION.keys():
            raise Warning("Picked wrong value of attenuation")

        self.write([self.ATTENUATION[att]])

        retVal = self.read()
        print(retVal)
        retVal = int.from_bytes(retVal,byteorder='big', signed=False)
        print(retVal)
        retVal = retVal << 2
        print(retVal)
        if self.ATTENUATION[att] == retVal:
            print("equal")
        else: print('diff')

x = HMC624()
x.setAttenuation(32)