import __main__
import sys
import subprocess
import os

# --native-fdm=socket,out,30,localhost,5501,udp --native-fdm=socket,in,30,localhost,5502,udp --fdm=null --max-fps=30 --altitude=3000

BIN_PATH = os.path.dirname(os.path.abspath(__main__.__name__)) + "/app/bin"


def start(args: list[str]):
    cmd = f"{BIN_PATH}/flightgear/fgfs.exe {' '.join(args)}"
    print(cmd, "\n", cmd.split(" "))
    process = subprocess.Popen(
        cmd.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
