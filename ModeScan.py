import time
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode
from MeasurementSession import MeasurementSession
from RfPowerDetector import rfPowerDetectorInstance 
from PiecykAutomationInterface import PAI_Instance as pai
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing


	
minFrequency = 5700
maxFrequency = 5900 
step = 5            # MHz
	
		
		
def runScanningMode():
	pai.request(PRSynthLevel(2))         
	pai.request(PRSynthRfEnable(1))      
	pai.request(PRAttenuator(att)) 		

	ms = MeasurementSession()
	r = range(self.minFrequency, self.maxFrequency, self.step)
	for frequency in r:
		print(f"Scanning at frequency={frequency} MHz")
		resp = pai.request(PRSynthFreq(frequency * 1e6))
		rflLevelDbm = rfPowerDetectorInstance.getRflPowerDbm()
		fwdLevelDbm = rfPowerDetectorInstance.getFwdPowerDbm()
		returnLossDb = rfPowerDetectorInstance.getReturnLossDb()
		ms.addDataPoint(fwdLevelDbm, rflLevelDbm, frequency)
	
	print("----------> FINISHED SCANNING")
	aci.stopProcess()
	
	return ms     # DO ZASTANOWIENIA, CZY TAK
	
	
	
