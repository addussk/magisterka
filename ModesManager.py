import time, threading
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode
from ModeManual import runManualMode
from ModeTemperatureTracking import runTemperatureTrackingMode
from ModeScan import runScanningMode
from MlxSensorArray import mlxSensorArrayInstance


# main loop
def modes_manager():
	
	while True:
		mlxSensorArrayInstance.update_readings()    # Regularna aktualizacja sensorów temperatury bez względu na wybrany tryb pracy
		
		if aci.getStartRequest():
			if not aci.isRunning():      
				target = None
				mode = aci.getMode()
				if mode == Mode.MANUAL:
					target = runManualMode
				elif mode == Mode.TEMPERATURE_TRACKING:
					target = runTemperatureTrackingMode
				elif mode == Mode.SCANNING:
					target = runScanningMode
				if target is not None:
					t = threading.Thread(target = target)
					t.start()
					aci.startProcess()
			else:
				pass   # Ignorujemy żądanie startu, jeśli jest aktualnie działający process
		print(".")
		time.sleep(0.3)



