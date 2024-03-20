class Data:
    def __init__(self):
        self.ax = 0.
        self.ay = 0.
        self.az = 0.
        self.rx = 0.
        self.ry = 0.
        self.rz = 0.

    def __sub__(self, other):
        new = Data()

        new.ax = self.ax - other.ax
        new.ay = self.ay - other.ay
        new.az = self.az - other.az
        new.rx = self.rx - other.rx
        new.ry = self.ry - other.ry
        new.rz = self.rz - other.rz


        new.ax = round(new.ax, 3)
        new.ay = round(new.ay, 3)
        new.az = round(new.az, 3)
        new.rx = round(new.rx, 3)
        new.ry = round(new.ry, 3)
        new.rz = round(new.rz, 3)

        return new

    def __str__(self):
        return f"Data{{a: {{x: {self.ax}, y: {self.ay}, z: {self.az}}}, r: {{x: {self.rx}, y: {self.ry}, z: {self.rz}}}}}"


def parse_float(line: str, trigger: str) -> str:
    s = ""

    index = line.find(trigger)
    if index == -1:
        print(f"[ERROR] Could not parse {trigger}")
        return None

    index += len(trigger) + 2

    while True:
        if line[index] not in "1234567890.-":
            break
        s += (line[index])
        index += 1
    return round(float(s), 3)


def sanitize_line(line_bytes) -> str:
    line = line_bytes.decode('UTF-8')
    return line.replace("\r", "").replace("\n", "")


def wait_for(trigger: str, port_serie):
    while True:
        line = sanitize_line(port_serie.readline())

        if line.startswith(trigger):
            break


def read_one(port_serie) -> Data:
    if not port_serie.isOpen():
        return None

    data = Data()

    while True:
        line = sanitize_line(port_serie.readline())

        if line == "":
            break

        if line.startswith("Acceleration"):
            # print(f"accel: {line}")

            x = parse_float(line, 'X')
            y = parse_float(line, 'Y')
            z = parse_float(line, 'Z')

            data.ax = x
            data.ay = y
            data.az = z

        elif line.startswith("Rotation"):
            # print(f"rota: {line}")

            x = parse_float(line, 'X')
            y = parse_float(line, 'Y')
            z = parse_float(line, 'Z')

            data.rx = x
            data.ry = y
            data.rz = z

        elif line.startswith("Temperature"):
            # print(f"temp: {line}")
            temp = parse_float(line, 'Temperature:')

        else:
            print(f"Could not understand: {line}")

    return data
