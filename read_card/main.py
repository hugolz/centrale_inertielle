from serial import *
import serial_reader
import listener

# Port série ttyACM0
# Vitesse de baud : 9600
# Timeout en lecture : 1 sec
# Timeout en écriture : 1 sec

def main():
    listener.start_threaded()

    base_data = serial_reader.Data()

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

            data = base_data - read_data
            print(f"Received data: {data}")

def cleanup():
    listener.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    cleanup()
