import time
import socket
import queue as Queue
import threading
import PiecykAnswer
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing

class PiecykAutomationInterface:
    
    def __init__(self, address, commandPort, answerPort):
        self.__address = address
        self.__commandPort = commandPort
        self.__answerPort = answerPort
        self.timeout = 3              # timeout given in seconds
        self.qUdpAnswers = Queue.Queue()
        self.osUdp = None
        self.cmdSocket = None
        self.ansSocket = None
        self.lastResponse = None
        print("PAI init:", vars(self))

    def init(self):
        print(f"Starting PiecykAutomationInterface... (commandPort={self.__commandPort} answerPort={self.__answerPort})")
        
        try:        
            self.cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.ansSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.ansSocket.bind(("", self.__answerPort))
        except socket.error as exc:
            print (f"Socket error: {exc}")
            print ("PiecykAutomationInterface FAILED and will stop.")
            return False
        else:
            self.osUdp = PiecykClientUdpListener(self.qUdpAnswers, self.ansSocket)
            self.osUdp.start()
            time.sleep(0.01)
            print("Ports are open.")
            return True
    
    def __enter__(self):
        return self
    
    # Instead of a destructor
    def __exit__(self, exc_type, exc_value, traceback):
        print ("PiecykAutomationInterface: EXIT received")
        if not self.osUdp is None:
            self.osUdp.enable = False
            print("...waiting to finish the udp listener...")
            self.osUdp.join()    # wait for exiting the thread befor closing the ansSocket
        self.cmdSocket.close()
        self.ansSocket.close()
        print("PiecykAutomationInterface has closed ports and says 'Good bye!'")


    # Use this method to send request to client.
    # Method is blocking, so it waits until the response is received and decoded.
    # The method returns values received in packet.
    # In case of timeout or packet decoding error, an exception is raised.
    # Arguments:
    #   cmdType   - type of the request (values of CommandType enum)
    #   cmdString - name of property or method on the RX object (server side)
    #   argsTuple - single value or tuple of several values which will be passed as arguments to the called method
    
    # UWAGA!!!!!!!!!!!! Powyższy komentarz jest nieaktualny
    
    
    def request(self, req):
        startTime = time.time()
        
        print(req.get())
        print()
        request = req.outputString.encode()
        
        #print ("Request: " + request)
        self.cmdSocket.sendto(request, (self.__address, int(self.__commandPort)))

        # ----------- Wait for the answer and process it ----------------------
        while (time.time() - startTime) < self.timeout:
            if (not self.qUdpAnswers.empty()):
                oac = self.qUdpAnswers.get()  # here we get already parsed answers
#                print "req.tid=" + str(orc.transactionId) + " ans.tid=" + str(oac.transactionId)
              #  if not oac.transactionId == orc.transactionId:  # discard the answer packet if transactionId differs from request's transactionId
              #      continue
              #  if oac.ansType == AnswerType.ANS_ERR:
              #      print ('Error message: ' + oac.message)
              #      #TODO: raise an exception here!
              #  print ("Answer: " + oac.inputString)
              #  print(oac)  
                self.lastResponse = oac
                return oac
            time.sleep(0.001)
                
        print ('Timeout error! Server did not repond.')
        # TODO: raise an exception here!        
        return None




class PiecykClientUdpListener(threading.Thread):
    
    def __init__(self, qUdpAnswers, ansSocket):
        threading.Thread.__init__(self, name="Thread PiecykClientUdpListener")
        self.qUdpAnswers = qUdpAnswers
        self.ansSocket = ansSocket
        self.enable = True
        
    def run(self):
        print("Starting PiecykClientUdpListener thread...")
        self.ansSocket.settimeout(0.5)  # this is necessary to be able to exit the thread gently (self.enable will be changed to False externally)
        while self.enable:
#            print("Listener's loop...")
            try:
                data, addr = self.ansSocket.recvfrom(1500)
            except TimeoutError as e:
                print("Exception:", e)
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK or err == errno.ETIMEDOUT:   #TODO: this is probably not correct
                    print('No data available')
                    continue
                else:
                    continue
            except OSError as e:
                pass    # do nothing if there is no data
            else:
            #    print("Received data:", data)
                oac = PiecykAnswer.PiecykAnswer((data.decode(), addr))            
                self.qUdpAnswers.put(oac)
            #    print(oac)
                                
        print("PiecykClientUdpListener thread stopped.")


PAI_Instance = PiecykAutomationInterface("localhost", 30033, 30034)
PAI_Instance.init()

if __name__=="__main__":
#    with PiecykAutomationInterface("localhost", 30033, 30034) as pai:
    with PAI_Instance as pai:
        print (pai)
        #pai.init()
    #    time.sleep(3)
        pai.request(PRPing("TestPing"))
        pai.request(PRStopExperiment())
        time.sleep(1)
     #   pai.request(PRStopExperiment())
     #   pai.request(PRStartExperiment())
     #   pai.request(PRStopExperiment())
        pai.request(PRFakeTemperature(35))    # no resp
        pai.request(PRSynthFreq(5800000000))  # no resp
        pai.request(PRSynthLevel(2))           # no resp
        pai.request(PRSynthRfEnable(1))        # no resp
        resp = pai.request(PRAttenuator(5))           # no resp
     #   pai.request(PRExit())                   # no resp
        time.sleep(1)
      #  pai.request(PRStartExperiment())
        time.sleep(2)
        pai.request(PRSynthLevel(2))         
        pai.request(PRSynthRfEnable(1))      
        pai.request(PRAttenuator(5))         
        pai.request(PRStopExperiment())
        pai.request(PRPing("TestPing"))
        pai.request(PRPing("TestPing"))
        time.sleep(1)
        pai.request(PRPing("TestPing"))
        pai.request(PRPing("TestPing"))
   #     pai.request(PRSynthRfEnable(0))
        print("Main thread finished")
    
   
    
              
