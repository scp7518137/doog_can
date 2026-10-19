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

ka1 = dc.KeepAlive(start_number=1, stop_number=2, bus=bus1, send_threading=send_threading)

try:
    send_threading.my_start()
    recv_threading.my_start()
    ka1.start()
    print("开启发送线程/接受线程/保活")

    send_threading.transmit_slot(motor1.mode_build(1))
    send_threading.transmit_slot(motor2.mode_build(1))
    print("model 1")
    # 设置状态

    send_threading.transmit_slot(motor1.open_to_angle_build(30))
    send_threading.transmit_slot(motor2.open_to_angle_build(30))
    print("set degree")
    # 编写开环角度命令并放入槽

    time.sleep(3)

    send_threading.transmit_slot(motor1.ask_open_to_angle_build())
    send_threading.transmit_slot(motor2.ask_open_to_angle_build())
    print("ask open_degree_state")
    # 编写查询开环角度命令并放入槽

    for _ in range(2):
        msg_recv = recv_threading.receive_slot()
        assert msg_recv is not None
        match msg_recv.arbitration_id:
            case 0x301:
                id, model = motor1.msg_recv(msg_recv)
            case 0x302:
                id, model = motor2.msg_recv(msg_recv)
        print(f"id is {id}, model is {model}")

    send_threading.transmit_slot(motor1.open_to_angle_build(-30))
    send_threading.transmit_slot(motor2.open_to_angle_build(-30))
    time.sleep(3)

    send_threading.transmit_slot(motor1.ask_open_to_angle_build())
    send_threading.transmit_slot(motor2.ask_open_to_angle_build())

    for _ in range(2):
        msg_recv = recv_threading.receive_slot()
        assert msg_recv is not None
        match msg_recv.arbitration_id:
            case 0x301:
                id, model = motor1.msg_recv(msg_recv)
            case 0x302:
                id, model = motor2.msg_recv(msg_recv)
        print(f"id is {id}, model is {model}")

    send_threading.transmit_slot(motor1.open_to_angle_build(30))
    send_threading.transmit_slot(motor2.open_to_angle_build(30))
    time.sleep(3)

    send_threading.transmit_slot(motor1.ask_open_to_angle_build())
    send_threading.transmit_slot(motor2.ask_open_to_angle_build())

    for _ in range(2):
        msg_recv = recv_threading.receive_slot()
        assert msg_recv is not None
        match msg_recv.arbitration_id:
            case 0x301:
                id, model = motor1.msg_recv(msg_recv)
            case 0x302:
                id, model = motor2.msg_recv(msg_recv)
        print(f"id is {id}, model is {model}")



finally:
    ka1.stop()
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()