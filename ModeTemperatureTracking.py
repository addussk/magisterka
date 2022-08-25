import time
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode
from RfPowerDetector import rfPowerDetectorInstance 
from PiecykAutomationInterface import PAI_Instance as pai
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing
from MeasurementSession import MeasurementSessionInstance as msi
from MlxSensorArray import mlxSensorArrayInstance

def runTemperatureTrackingMode():
	print("---------> Starting TEMPERATURE TRACKING mode")

	msi.clearAllTraces()

	pai.request(PRSynthLevel(2))         
	pai.request(PRSynthRfEnable(1))      
	pai.request(PRAttenuator(aci.getAttenuator())) 		
	pai.request(PRStartExperiment())
	
	while aci.isRunning() and aci.getMode()==Mode.TEMPERATURE_TRACKING:
		receivedPwr = rfPowerDetectorInstance.getRflPowerDbm()
		transmittedPwr = rfPowerDetectorInstance.getFwdPowerDbm()
		requestedTemperature = round(pai.lastResponse.temperatureRequested, 2)
		frequency = aci.getFrequencyMhz()
		msi.addDataPoint(transmittedPwr, receivedPwr, frequency, tempRequested=requestedTemperature)
		temperature = mlxSensorArrayInstance.get_averaged_temperature()
		pai.request(PRFakeTemperature(temperature))
		time.sleep(0.5)
		
	# Turn off the RF after STOP command or mode change
	pai.request(PRStopExperiment())
	aci.stopProcess()
	
	print("----------> FINISHED TEMPERATURE TRACKING")
