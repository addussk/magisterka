import time
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode
from RfPowerDetector import rfPowerDetectorInstance 
from PiecykAutomationInterface import PAI_Instance as pai
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing
from MeasurementSession import MeasurementSessionInstance as msi


def runManualMode():
	print("---------> Starting MANUAL mode")
	
	msi.clearAllTraces()
	
	pai.request(PRSynthLevel(2))         
	pai.request(PRSynthRfEnable(1))      
	pai.request(PRAttenuator(aci.getAttenuator())) 		
	
	while aci.isRunning() and aci.getMode()==Mode.MANUAL:
		receivedPwr = rfPowerDetectorInstance.getRflPowerDbm()
		transmittedPwr = rfPowerDetectorInstance.getFwdPowerDbm()
		requestedTemperature = round(pai.lastResponse.temperatureRequested, 2)
		frequency = aci.getFrequencyMhz()
		msi.addDataPoint(transmittedPwr, receivedPwr, frequency, tempRequested=requestedTemperature)
		time.sleep(1)
		print("MANUAL RUNNING")
		# Frequency and attenuator control is performed directly by callbacks



	# Turn off the RF after STOP command or mode change
	pai.request(PRStopExperiment())
	pai.request(PRSynthRfEnable(0))  
	aci.stopProcess()

	print("---------->  FINISHED MANUAL")
