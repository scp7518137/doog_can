import doog_can as dc
import can

def _six_bus_init() -> tuple[can.BusABC, can.BusABC]:
    bus1, bus2 = dc.vbus_init(name="doog_can")
    # can初始化

    ka1 = dc.KeepAlive(start_number=1, stop_number=6, bus=bus1)
    ka1.start()
    # 1-6电机保活
    return bus1, bus2

def test_keep_alive() -> None:
    bus1, bus2 = _six_bus_init()

    for _ in range(1,36,1):
        msg: can.Message | None = bus2.recv(timeout=0.02)
        assert msg is not None
        node_id = msg.arbitration_id
        assert 1 <= node_id - 0x100 <= 6
        assert msg.data.hex() == "0800000000000000"
    dc.vbus_close(bus1)
    dc.vbus_close(bus2)

def test_doog_can_send() -> None:
    bus1, bus2 = dc.vbus_init(name="doog_can")

    motor1 = dc.Motor(bus=bus1, node_id=1)
    motor2 = dc.Motor(bus=bus1, node_id=2)
    motor3 = dc.Motor(bus=bus1, node_id=3)
    motor4 = dc.Motor(bus=bus1, node_id=4)
    motor5 = dc.Motor(bus=bus1, node_id=5)
    motor6 = dc.Motor(bus=bus1, node_id=6)
    # 设置六个电机

    motor1.set_speed(10)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 1
    assert msg.data.hex() == "0164000000000000"

    motor1.set_speed(-5)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 1
    assert msg.data.hex() == "01ceff0000000000"

    motor2.set_voltage(0.6)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 2
    assert msg.data.hex() == "023c000000000000"

    motor3.set_mode(1)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 3
    assert msg.data.hex() == "0301000000000000"

    motor3.set_mode(4)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 3
    assert msg.data.hex() == "0304000000000000"

    motor4.set_direction(1)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 4
    assert msg.data.hex() == "0401000000000000"

    motor5.set_torque(1)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 5
    assert msg.data.hex() == "0564000000000000"

    motor6.set_position(1)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 6
    assert msg.data.hex() == "0610270000000000"

    motor6.open_to_angle(90)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 6
    assert msg.data.hex() == "0784030000000000"

    motor6.open_to_angle(-90)
    msg: can.Message | None = bus2.recv()
    assert msg is not None
    assert msg.arbitration_id - 0x100 == 6
    assert msg.data.hex() == "077cfc0000000000"


