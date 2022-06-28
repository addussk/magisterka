from enum import Enum


class CommandType(Enum):
    CMD_UNDEFINED = 0
    CMD_EXEC = 1
    CMD_RXSTATE = 2
    CMD_HEARTBEAT = 3
    CMD_SHUTDOWN = 4

class AnswerType(Enum):
    ANS_UNDEFINED = 0
    ANS_OK = 1
    ANS_ERR = 2


# An instance of this class represents a single UDP packet received by client
class PiecykAnswer():
    
    ansDict = {
        AnswerType.ANS_UNDEFINED : 'UNDEFINED',
        AnswerType.ANS_OK        : 'OK',
        AnswerType.ANS_ERR       : 'ERROR'
    }    
    
    def __init__(self, packet=('',('localhost', 1234))):
        self.inputString = packet[0]
        self.addressFrom = packet[1][0]
        self.portFrom = packet[1][1]
        self.transactionId = 0
        self.evalString = ''
        self._defaultValues()
        if (len(self.inputString)>5):
            self.decode(self.inputString)
    
    # decode input string into 
    def decode(self, inputString):
        # check, whether we have a correct marker at beginning of the string
        try:
          #  print(inputString)
            if (inputString[0]=='<'): 
                tokens = inputString.split(':')
               # print(tokens)
                for t in tokens:
                    if t == "<_>":
                        continue
                    t = t.replace("\x00", "")
                    paramCode = t[0]
                    valueStr = t[1:]
                    #value = float(valueStr)
                    
                    if paramCode == "t":
                        self.timeFromStart = float(valueStr)
                    elif paramCode == "T":
                        self.temperatureNow = float(valueStr)
                    elif paramCode == "D":
                        self.temperatureRequested = float(valueStr)
                    elif paramCode == "a":
                        self.attenuation = int(valueStr)
                    elif paramCode == "p":
                        self.pllPowerLevel = int(valueStr)
                    elif paramCode == "f":
                        self.frequency = float(valueStr)
                    elif paramCode == "r":
                        self.rfOn = bool(int(valueStr))
                    elif paramCode == "c":
                        self.automaticControl = bool(int(valueStr))
        except Exception as err:
            print(err)
            self._defaultValues()
        
    def _defaultValues(self):
        self.timeFromStart = 0
        self.temperatureNow = 0
        self.temperatureRequested = 0
        self.attenuation = 0
        self.pllPowerLevel = 0
        self.frequency = 0
        self.rfOn = False
    
    def __str__(self):
        s = "PiecykAnswer contains:\n"
        s += f" - time from start : {self.timeFromStart} s\n"
        s += f" - temperature now : {self.temperatureNow} C\n"
        s += f" - temperature requested : {self.temperatureRequested} C\n"
        s += f" - attenuation : {self.attenuation} [dB]\n"
        s += f" - pll power level : {self.pllPowerLevel}\n"
        s += f" - frequency : {self.frequency / 1e6} MHz\n"
        s += f" - rf is ON : {self.rfOn}\n"
        s += f" - automatic control : {self.automaticControl}\n"
        return s

