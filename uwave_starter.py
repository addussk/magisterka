# Moduł odpowiedzialny za uruchamianie programu uwave, którego zadaniem jest sterowanie
# syntezerem PLL, tłumikiem oraz działanie automatyki grzania.

import psutil
import subprocess
import os
import signal

UWAVE_PATH = "/home/pi/magisterka/uwave_bin"
UWAVE_PROCESS_NAME = "uwave"


# Zrodlo:  https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
# Killing: https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                print("------PROCESS STATUS:", str(proc.status()))
                if proc.status() == psutil.STATUS_ZOMBIE:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    print("----- uwave detected as ZOMBIE PROCESS - an attempt to kill it")
                    return False
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;


def checkIfUwaveIsRunning():
    return checkIfProcessRunning(UWAVE_PROCESS_NAME)


def startUwaveProcess():
    print("Starting:", os.getcwd(), UWAVE_PROCESS_NAME)
    cwd = os.getcwd()
    os.chdir(UWAVE_PATH)
    subprocess.Popen(
        ["./"+UWAVE_PROCESS_NAME],
       # stdout=subprocess.PIPE,
       # stderr=subprocess.PIPE,
       # text=True,
        shell=True,
        preexec_fn=os.setsid
    )
    os.chdir(cwd)   # return to original folder

if __name__=="__main__":
    print(os.getcwd())
    print(checkIfUwaveIsRunning())
    startUwaveProcess()
    print(checkIfUwaveIsRunning())
    print(os.getcwd())
