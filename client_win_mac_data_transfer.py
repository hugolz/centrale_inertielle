import socket
import serial
from read_card import serial_reader

"""
Goal:
    send what your receive from the card
"""

HOST = '127.0.0.1'    # The remote host
PORT = 50021  # The same port as used by the server
BUF_SIZE = 1024


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}, buffer size: {BUF_SIZE}")
            with serial.Serial(port="COM6", baudrate=115200, timeout=1, writeTimeout=1) as port_serie:
                # send(s, port_serie.readline())
                # print(port_serie.readline())
                #
                serial_reader.wait_for("", port_serie)
                serial_reader.wait_for("Adafruit MPU6050 test!", port_serie)
                serial_reader.wait_for("MPU6050 Found!", port_serie)
                serial_reader.wait_for(
                    "Accelerometer range set to:", port_serie)
                serial_reader.wait_for("Gyro range set to:", port_serie)
                serial_reader.wait_for("Filter bandwidth set to:", port_serie)
                serial_reader.wait_for("", port_serie)
                while True:
                    e = port_serie.readline()
                    print(f"Sending: {e}")
                    s.send(e)

                s.close()
        except KeyboardInterrupt:
            pass
            # cleanup()
            # quit
