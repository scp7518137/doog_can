import doog_can as dc
import can
import time
from doog_can import StatusReport


class MortorError(Exception):
    pass

def start() -> None:
    send_threading.my_start()
    recv_threading.my_start()
    ka1.start()

def set_model(model1: int, model2: int) -> None:
    send_threading.transmit_slot(motor1.build_mode_cmd(model1))
    send_threading.transmit_slot(motor2.build_mode_cmd(model2))

def set_angle(angle1: float, angle2: float) -> None:
    send_threading.transmit_slot(motor1.build_open_to_angle_cmd(angle1))
    send_threading.transmit_slot(motor2.build_open_to_angle_cmd(angle2))
    print("set angle")

def set_direction(d1: int, d2: int) -> None:
    send_threading.transmit_slot(motor1.build_direction_cmd(d1))
    send_threading.transmit_slot(motor2.build_direction_cmd(d2))

def ask_state() -> None:
    send_threading.transmit_slot(motor1.build_ask_open_to_angle_cmd())
    send_threading.transmit_slot(motor2.build_ask_open_to_angle_cmd())

def read_angle() -> tuple[can.Message | None, can.Message | None]:
    print("waiting angle.........")
    motor1_msg: can.Message | None = recv_threading.receive_nomal_slot(1)
    motor2_msg: can.Message | None = recv_threading.receive_nomal_slot(2)
    return motor1_msg, motor2_msg

def check_default() -> None:
    print("Checking fault frame......")
    while True:
        msg: can.Message | None = recv_threading.reveive_fault_slot()
        if msg is None:
            break
        print("Motors have err......")
        assert msg is not None
        node_id = msg.arbitration_id - 0x400
        code: dc.FaultrCode = dc.decode_faultcode(bytes(msg.data))
        print(f"ID: {node_id}\ncode: {code.fault_code.name}\nin_back_off: {code.in_backoff}\nmask: {code.mask.name}\nSTATUS1: {code.STATUS1.name}\nSTATUS2: {code.STATUS2.name}")


def print_angle(msg: can.Message) -> None:
    node_id = msg.arbitration_id - 0x300
    data: bytes = bytes(msg.data)
    code = dc.decode_opentoangle(data)
    print(f"ID: {node_id}\nstatus: {code.status}, angle: {code.moveangle}, settingvoltage: {code.settingvoltage}, relhovdev: {code.relhovdev}, autotage: {code.autotage}")

try:
    bus1 = dc.can_init("can1")
    # 定义bus1

    motor1 = dc.Motor(bus=bus1, node_id=1)
    motor2 = dc.Motor(bus=bus1, node_id=2)
    print("定义电机1/2")

    send_threading = dc.Transmit_Threading(bus=bus1)
    recv_threading = dc.Receive_Threading(bus=bus1)
    print("初始化发送/接受线程")

    ka1 = dc.KeepAlive(start_number=1, stop_number=2, bus=bus1, send_threading=send_threading)

    start()
    set_model(2, 2)
    print("设置为对齐模式")
    time.sleep(1)

    set_model(1, 1)

    print("发送1")
    set_angle(10, 10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()

    print("发送2")
    set_angle(-10, -10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()

    print("发送3")
    set_angle(10, 10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()


    
finally:
    ka1.stop()
    time.sleep(1)
    check_default()
    time.sleep(1)
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()

try:
    bus1 = dc.can_init("can1")
    # 定义bus1

    motor1 = dc.Motor(bus=bus1, node_id=1)
    motor2 = dc.Motor(bus=bus1, node_id=2)
    print("定义电机1/2")

    send_threading = dc.Transmit_Threading(bus=bus1)
    recv_threading = dc.Receive_Threading(bus=bus1)
    print("初始化发送/接受线程")

    ka1 = dc.KeepAlive(start_number=1, stop_number=2, bus=bus1, send_threading=send_threading)

    start()
    set_model(2, 2)
    print("设置为对齐模式")
    time.sleep(1)

    set_model(1, 1)

    print("发送4")
    set_angle(10, 10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()

    print("发送5")
    set_angle(-10, -10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()

    print("发送6")
    set_angle(10, 10)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()


    
finally:
    ka1.stop()
    time.sleep(1)
    check_default()
    time.sleep(1)
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()
