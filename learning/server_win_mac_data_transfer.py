import socket
import time
from read_card import serial_reader
from read_card import listener
from flightgear_python.fg_if import FDMConnection
"""
Goal:
    Receive the card's ouput from the socket, parse it and send it to flightgear
"""

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 50021  # Port to listen on (non-privileged ports are > 1023)


# Port série ttyACM0
# Vitesse de baud : 9600
# Timeout en lecture : 1 sec
# Timeout en écriture : 1 sec


def fdm_callback(fdm_data, event_pipe):
    if event_pipe.child_poll():
        phi_rad_child, psi_rad_child, theta_rad_child, = event_pipe.child_recv()  # unpack tuple
        # set only the data that we need to
        fdm_data['theta_rad'] = theta_rad_child  # we can force our own values
        fdm_data['psi_rad'] = psi_rad_child  # we can force our own values
        fdm_data['phi_rad'] = phi_rad_child  # we can force our own values
        print(fdm_data)
        # fdm_data.alt_m = fdm_data.alt_m + phi_rad_child  # or just make a relative change
    return fdm_data  # return the whole structure


def main(s):
    s.bind((HOST, PORT))
    s.listen()
    print(f"[INFO] Binded to {HOST}:{PORT}")
    while True:
        try:
            conn, addr = s.accept()
            handle_client(conn, addr)
        except Exception as e:
            print(f"[ERROR] An error occured while handling connection w/ a client: {e}")


def handle_client(conn, addr):
    print(f"[INFO] Connected by {addr}")
    base_data = serial_reader.Data()
    fdm_conn = FDMConnection(fdm_version=24)
    fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
    fdm_conn.connect_tx('localhost', 5502)
    fdm_conn.start()  # Start the FDM RX/TX loop
    phi_rad_parent = 0.0
    psi_rad_parent = 0.0
    theta_rad_parent = 0.0

    while True:
        read_data = serial_reader.read_one_from_socket(conn, 1024)
        if read_data == None:
            break

        last_key = listener.get_last_key()
        if last_key == "s":
            print("Save")
            base_data = read_data
            phi_rad_parent = 0.0
            psi_rad_parent = 0.0
            theta_rad_parent = 0.0

        data = base_data - read_data
        print(f"Received data: {data}")

        addphi = round(data.rz / 100, 3)*30
        addpsi = round(data.rx / 100, 3)*30
        addtheta = round(data.ry / 100, 3)*30
        phi_rad_parent += addphi
        psi_rad_parent += addpsi
        theta_rad_parent += addtheta
        print(addphi, addpsi)
        fdm_event_pipe.parent_send(
            (phi_rad_parent, psi_rad_parent, theta_rad_parent,))
    print(f"[INFO] The socket w/ {addr} has been closed")


if __name__ == "__main__":
    listener.start_threaded()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        main(s)
    except Exception as e:
        print("[ERROR] Main exited due to: {e}")
    listener.stop()
