from serial import *
import read_card.serial_reader as serial_reader
import read_card.listener as listener

# Port série ttyACM0
# Vitesse de baud : 9600
# Timeout en lecture : 1 sec
# Timeout en écriture : 1 sec


def main():
    listener.start_threaded()

    base_data = serial_reader.Data()

    xyz = [0, 0, 0]

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
                xyz = [0, 0, 0]
                base_data = read_data

            data = serial_reader.Data()
            threshhold = 0.10
            if read_data.rx + read_data.ry + read_data.rz > threshhold or read_data.rx - read_data.ry - read_data.rz < -threshhold:
                data = base_data - read_data
            # print(f"Received data: {data}")
            xyz[0] += data.rx
            xyz[1] += data.ry
            xyz[2] += data.rz
            print(f"x: {round(xyz[0], 2)}, \ty: {round(xyz[1], 2)}, \tz: {round(xyz[2], 2)}")


def cleanup():
    listener.stop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    cleanup()
