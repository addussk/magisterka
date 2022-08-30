import time
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode
from MeasurementSession import MeasurementSession
from RfPowerDetector import rfPowerDetectorInstance 
from PiecykAutomationInterface import PAI_Instance as pai
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing
from MeasurementSession import MeasurementSessionInstance as msi
import copy

	
minFrequency = 5700
maxFrequency = 5900 
step = 10            # MHz
	
		
		
def runScanningMode():
	msi.clearAllTraces()
	att = 15
	pai.request(PRSynthLevel(2))         
	pai.request(PRSynthRfEnable(1))      
	pai.request(PRAttenuator(att)) 		

	ms = MeasurementSession()
	r = range(minFrequency, maxFrequency, step)

	while aci.isRunning() and aci.getMode()==Mode.SCANNING:
		ms.clearAllTraces()
		ms.isFrequencyDomain = True
		for frequency in r:
			resp = pai.request(PRSynthFreq(frequency * 1e6))
			print(f"Scanning at frequency={frequency} MHz")
			resp = pai.request(PRSynthFreq(frequency * 1e6))
			rflLevelDbm = rfPowerDetectorInstance.getRflPowerDbm()
			fwdLevelDbm = rfPowerDetectorInstance.getFwdPowerDbm()
			ms.addDataPoint(fwdLevelDbm, rflLevelDbm, frequency)
			if not aci.isRunning():
				break
		msi.replaceTracesFromOtherInstance(ms)
	
	# Turn off the RF after STOP command or mode change
	pai.request(PRStopExperiment())
	pai.request(PRSynthRfEnable(0))  
		
	aci.stopProcess()

	print("----------> FINISHED SCANNING")
	
	
	
