from PiecykAnswer import CommandType

# An instance of this class represents a single UDP packet sent by client
class PiecykRequest():

    transactionId = 0    
    outputString = ""
    
    def __init__(self):
        self.transactionId = self.transactionId + 1
#        self.cmdToken = "(empty)"
#        self.cmdValue = ""
        self.outputString = ""
        
    def encode(self, cmdToken="", cmdValue=""):
        PiecykRequest.transactionId = PiecykRequest.transactionId + 1
      #  print(f"---{cmdToken}---")
        assert cmdToken!="", f"cmdToken is empty! given:{cmdToken}"
        self.outputString = cmdToken
        cmdValue = str(cmdValue)
        if cmdValue != "":
            self.outputString += "=" + cmdValue
        self.outputString += "\0"
        return self.outputString

    def get(self):
        return self.outputString

    def __str__(self):
        return f"Request: {self.get()}"
    

class PRStartExperiment(PiecykRequest):
    def __init__(self):
        PiecykRequest.__init__(self)
        self.encode("START_EX")

class PRStopExperiment(PiecykRequest):
    def __init__(self):
        PiecykRequest.__init__(self)
        self.encode("STOP_EX")

class PRFakeTemperature(PiecykRequest):       # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self, temperature_c):
        PiecykRequest.__init__(self)
        self.encode("FAKE_TEMP", temperature_c)


class PRSynthFreq(PiecykRequest):           # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self, frequency_hz):
        PiecykRequest.__init__(self)
        self.encode("SYNTH_FREQ", frequency_hz)

class PRSynthLevel(PiecykRequest):          # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self, level):
        level=int(level)
        assert level>=0 and level<=3, f"PLL synthesizer's power level allowed range: 0...3, given {level}"
        PiecykRequest.__init__(self)
        self.encode("SYNTH_LEVEL", level)

# To żądanie włącza syntezer PLL oraz zasilanie wzmacniacza!!!
class PRSynthRfEnable(PiecykRequest):      # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self, state):
        state=int(state)
        assert state==0 or state==1, f"RF output state can be 0 (OFF) or 1 (ON), given {state}"
        PiecykRequest.__init__(self)
        self.encode("SYNTH_RF", state)      
        
class PRAttenuator(PiecykRequest):          # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self, att_db):
        att_db = int(att_db)
        assert att_db>=0 and att_db<=31, f"Attenuator: allowed range of attenuation is 0...31 dB, but {att_db} dB was given"
        PiecykRequest.__init__(self)
        self.encode("ATTEN", att_db)
        
class PRExit(PiecykRequest):               # na to zadanie serwer nie odpowiada - rozwazyc dopisanie odpowiedzi
    def __init__(self):
        PiecykRequest.__init__(self)
        self.encode("EXIT")

class PRPing(PiecykRequest):
    def __init__(self, value):
        PiecykRequest.__init__(self)
        self.encode("PING", value)


if __name__=="__main__":

    pi = PRPing("Test")
    print(pi)
    print(pi.get())

#    pr = PiecykRequest()
#    print(pr.encode())
#    prse = PRStartExperiment()
   

#    print(prse.get())

    pr =  PRExit()
    print(pr.get())

    
