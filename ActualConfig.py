from enum import Enum
from datetime import datetime

class Mode(Enum):
	MANUAL = "manual"
	TEMPERATURE_TRACKING = "t-tracking"
	SCANNING = "scanning"




class ActualConfig:

	def __init__(self):
		self.__isRunning = False
		self.__mode = Mode.TEMPERATURE_TRACKING
		self.__attenuator = 30
		self.__frequencyMHz = 5850
		self.__startRequest = False
		self.__isAttModified = False;
		self.__isFreqModified = False
		self.__isModeModified = False
		self.__startTime = datetime.now()
		self.__stopTime = None

		
	def isRunning(self):
		return self.__isRunning
		
	def requestStartProcess(self):
		self.__startRequest = True
		
	def startProcess(self):
		if not self.__isRunning:
			self.__startTime = datetime.now()
			self.__stopTime = None
		self.__isRunning = True
		
	def stopProcess(self):
		self.__isRunning = False
		self.__stopTime = datetime.now()
		
	def getAttenuator(self):
		return self.__attenuator
		
	def setAttenuator(self, att: int):
		assert isinstance(att, int)
		assert att>=0 and att<=31, f"Attenuation {att} is out of allowed range."
		self.__attenuator = att
		self.__isAttModified = True
		
	def getFrequencyMhz(self):
		return self.__frequencyMHz
		
	def setFrequencyMHz(self, frequency):
		assert isinstance(frequency, int) or isinstance(frequency, float)
		self.__frequencyMHz = frequency
		self.__isFrequencyModified = True
		
	def setMode(self, mode: Mode):
		print("Mode changed to:", mode)
		self.__mode = mode
		self.__isModeModified = True
		
	def getMode(self):
		return self.__mode
	
	def getStartRequest(self):
		sr = self.__startRequest
		self.__startRequest = False
		return sr
	
	def getProcessTime(self):
		toTime = None
		if self.isRunning():
			toTime = datetime.now()
		else:
			if self.__stopTime is None:
				return 0
			else:
				toTime = self.__stopTime
		delta = toTime - self.__startTime
		all_seconds = delta.total_seconds()
		return int(all_seconds)
	
	def getProcessTimeStr(self):
#		if self.__stopTime is not None:
		all_seconds = self.getProcessTime()
		if all_seconds == 0:
			return "00:00"
		minutes = all_seconds // 60
		seconds = all_seconds % 60
		out =  f"{minutes:02}:{seconds:02}"
		print(out)
		return out
#		else:
#			return "00:00"
			
	
	
	def isAttModified(self):
		return self.__isAttModified
		
	def isFreqModified(self):
		return self.__isFreqModified
		
	def isModeModified(self):
		return self.__isModeModified
		
		

ActualConfigInstance = ActualConfig()


		
