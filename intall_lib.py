import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

all_needed_libs = ["wlthermsensor", "dash", "flask"]

for lib in all_needed_libs:
    install(lib)
