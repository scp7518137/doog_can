import doog_can as dc
import can
import time
from doog_can import StatusReport

bus1 = dc.can_init("can1")
# 定义bus1

motor1 = dc.Motor(bus=bus1, node_id=1)
motor2 = dc.Motor(bus=bus1, node_id=2)
print("定义电机1/2")

send_threading = dc.Transmit_Threading(bus=bus1)
recv_threading = dc.Receive_Threading(bus=bus1)
print("初始化发送/接受线程")

class MortorError(Exception):
    pass

ka1 = dc.KeepAlive(start_number=1, stop_number=2, bus=bus1, send_threading=send_threading)

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
    print("set degree")

def set_direction(d1: int, d2: int) -> None:
    send_threading.transmit_slot(motor1.build_direction_cmd(d1))
    send_threading.transmit_slot(motor2.build_direction_cmd(d2))

def ask_state() -> None:
    send_threading.transmit_slot(motor1.build_ask_open_to_angle_cmd())
    send_threading.transmit_slot(motor2.build_ask_open_to_angle_cmd())

def read_angle() -> tuple[can.Message | None, can.Message | None]:
    print("waiting angle.........")
    motor1_msg: can.Message | None = recv_threading.receive_slot(1)
    motor2_msg: can.Message | None = recv_threading.receive_slot(2)
    return motor1_msg, motor2_msg

def check_default() -> None:
    print("Checking fault tag......")
    result = any(recv_threading.fault_tag.values())
    if result:
        print("Motor has err......")
        faulty_ids = [node_id for node_id, fault_tag in recv_threading.fault_tag.items() if fault_tag]
        read_angle()
        for id in faulty_ids:
            msg: can.Message | None = recv_threading.receive_slot(id)
            assert msg is not None
            node_id = msg.arbitration_id - 0x400
            data: bytes = bytes(msg.data)
            code = dc.decode_faultcode(data)
            print(f"ID: {node_id}\nfault_code: {code.fault_code}\nnumber: {code.number}\nstate: {code.state}\nstattus1:{code.STATUS1}\nstatus2: {code.STATUS2}")
            raise MortorError("MORTOR ERROR")
    print("continue......")




def print_angle(msg: can.Message) -> None:
    node_id = msg.arbitration_id - 0x300
    data: bytes = bytes(msg.data)
    code = dc.decode_opentoangle(data)
    print(f"ID: {node_id}\nstatus: {code.status}, angle: {code.moveangle}, settingvoltage: {code.settingvoltage}, relhovdev: {code.relhovdev}, autotage: {code.autotage}")

try:
    start()
    set_model(2, 2)
    print("设置为对齐模式")
    time.sleep(1)

    set_model(1, 1)

    set_angle(30, 30)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()
    
    set_angle(-30, -30)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()



    set_angle(30, 30)
    motor1_degree, motor2_degree = read_angle()
    assert motor1_degree and motor2_degree is not None
    print_angle(motor1_degree)
    print_angle(motor2_degree)
    check_default()

    
finally:
    ka1.stop()
    check_default()
    time.sleep(2)
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()
