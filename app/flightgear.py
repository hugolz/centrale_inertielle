import __main__
import subprocess
import os
from app.logger import info, warn

# --native-fdm=socket,out,30,localhost,5501,udp --native-fdm=socket,in,30,localhost,5502,udp --fdm=null --max-fps=30 --altitude=3000

BIN_PATH = os.path.dirname(os.path.abspath(__main__.__name__)) + "/app/bin"

process = None


def start(args: list[str]):
    global process
    if process != None:
        warn(
            "[SAFETY] Ignored a call to start flightgear as it's appears to already be started")
        return
    cmd = f"{BIN_PATH}/flightgear/fgfs.exe {' '.join(args)}"
    info("Starting fligtear")
    process = subprocess.Popen(
        cmd.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def stop():
    global process
    if process == None:
        # No action needed
        return

    from app.logger import warn
    process.kill()

    # Clean up the process's pipes to allow safe terminaison of the program
    _, _ = process.communicate()
    process = None
    warn("flightgear exited")
