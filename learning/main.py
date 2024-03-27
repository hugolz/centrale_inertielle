from serial import *
import read_card.serial_reader as serial_reader
import read_card.listener as listener
import time
from flightgear_python.fg_if import FDMConnection

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


def main():
    listener.start_threaded()

    base_data = serial_reader.Data()

    fdm_conn = FDMConnection(fdm_version=24)
    fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
    fdm_conn.connect_tx('localhost', 5502)
    fdm_conn.start()  # Start the FDM RX/TX loop
    phi_rad_parent = 0.0
    psi_rad_parent = 0.0
    theta_rad_parent = 0.0

    with Serial(port="COM6", baudrate=115200, timeout=1, writeTimeout=1) as port_serie:
        serial_reader.wait_for("", port_serie)
        serial_reader.wait_for("Adafruit MPU6050 test!", port_serie)
        serial_reader.wait_for("MPU6050 Found!", port_serie)
        serial_reader.wait_for("Accelerometer range set to:", port_serie)
        serial_reader.wait_for("Gyro range set to:", port_serie)
        serial_reader.wait_for("Filter bandwidth set to:", port_serie)
        serial_reader.wait_for("", port_serie)
        while True:

            last = listener.get_last_key()
            read_data = serial_reader.read_one(port_serie)

            if last == "esc":
                break
            elif last == "s":
                print("Save")
                base_data = read_data
                phi_rad_parent = 0.0
                psi_rad_parent = 0.0
                theta_rad_parent = 0.0

            data = base_data - read_data
            print(f"Received data: {data}")

            # Flightgear
            # phi_rad_parent += data.rz / 10
            # send tuple

            addphi = round(data.rz / 100, 3)*30
            addpsi = round(data.rx / 100, 3)*30
            addtheta = round(data.ry / 100, 3)*30
            phi_rad_parent += addphi
            psi_rad_parent += addpsi
            theta_rad_parent += addtheta
            print(addphi, addpsi)
            fdm_event_pipe.parent_send(
                (phi_rad_parent, psi_rad_parent, theta_rad_parent,))


def cleanup():
    listener.stop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    cleanup()
