import doog_can as dc
import can
import time
from doog_can import StatusReport


class MortorError(Exception):
    pass

def init_and_start():
    bus1 = dc.can_init("can1")
    send_threading = dc.Transmit_Threading(bus1)
    recv_threading = dc.Receive_Threading(bus1)
    ka1 = dc.KeepAlive(1, 2, send_threading)
    send_threading.my_start()
    recv_threading.my_start()
    ka1.start()
    return bus1, ka1, send_threading, recv_threading


def print_motor(motor: dc.Motor, code: dc.StatusReport | dc.OpenToAngle | dc.FaultrCode | None) -> None:

    if isinstance(code, dc.StatusReport):
        print(f"ID: {motor.node_id} bus: {code.bus_voltage} current: {code.current} mode: {code.mode.name} speed: {code.speed} status: {code.status.name}")
    elif isinstance(code, dc.OpenToAngle):
        print(f"ID: {motor.node_id}\nstatus: {code.status}, angle: {code.moveangle}, settingvoltage: {code.settingvoltage}, relhovdev: {code.relhovdev}, autotage: {code.autotage}")

    elif isinstance(code, dc.FaultrCode):
        print(f"ID: {motor.node_id}\ncode: {code.fault_code.name}\nin_back_off: {code.in_backoff}\nmask: {code.mask.name}\nSTATUS1: {code.STATUS1.name}\nSTATUS2: {code.STATUS2.name}")

    else:
        print("msg not received.........")

try:
    bus1, ka1, send_threading, recv_threading = init_and_start()

    motor1 = dc.Motor(send_threading.messages, recv_threading.msg_dict, recv_threading.fault_msg_dict, 1)
    motor2 = dc.Motor(send_threading.messages, recv_threading.msg_dict, recv_threading.fault_msg_dict, 2)

    motor1.send_mode_cmd(2)
    motor2.send_mode_cmd(2)

    motor1.send_mode_cmd(1)
    motor2.send_mode_cmd(1)

    motor1.send_ask_status_cmd()
    motor2.send_ask_status_cmd()
    print_motor(motor1, motor1.decode_normal_code())
    print_motor(motor2, motor2.decode_normal_code())

    motor1.send_open_to_angle_cmd(10)
    motor2.send_open_to_angle_cmd(10)

    print_motor(motor1, motor1.decode_normal_code())
    print_motor(motor2, motor2.decode_normal_code())

    motor1.send_open_to_angle_cmd(-10)
    motor2.send_open_to_angle_cmd(-10)

    print_motor(motor1, motor1.decode_normal_code())
    print_motor(motor2, motor2.decode_normal_code())

    motor1.send_open_to_angle_cmd(10)
    motor2.send_open_to_angle_cmd(10)

    print_motor(motor1, motor1.decode_normal_code())
    print_motor(motor2, motor2.decode_normal_code())

    motor1.send_open_to_angle_cmd(-10)
    motor2.send_open_to_angle_cmd(-10)

    print_motor(motor1, motor1.decode_normal_code())
    print_motor(motor2, motor2.decode_normal_code())



   
    
finally:
    ka1.stop()
    time.sleep(1)
    print_motor(motor1, motor1.check_motors())
    print_motor(motor2, motor2.check_motors())
    time.sleep(1)
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()

