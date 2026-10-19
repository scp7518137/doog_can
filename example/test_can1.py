import doog_can as dc
import can
import time
from doog_can import StatusReport

bus1 = dc.can_init("can1")
bus2 = dc.can_init("can0")
# 定义bus1, bus1

motor1 = dc.Motor(bus=bus1, node_id=1)
# 定义电机1
print("定义电机1")

send_threading = dc.Transmit_Threading(bus=bus1)
# 初始化发送线程
print("初始化发送线程")

try:
    send_threading.my_start()
    # 开启发送线程
    print("开启发送线程")

    msg = motor1.mode_build(1)
    print("生成msg")
    assert msg is not None
    send_threading.transmit_slot(msg)
    print(f"已发送{msg}")
    # 填充

    msg_recv = bus2.recv(timeout = 0.05)
    if msg_recv is not None:
        msg_recv_id = msg_recv.arbitration_id
        msg_recv_data = bytes(msg_recv.data)
        report: StatusReport = dc.decode_frame(msg_recv_data)
        print(f"已接收 {msg_recv_id - 0x200} {report}")
    else:
        print("未接收")

finally:
    send_threading.my_stop()
    bus1.shutdown()
    bus2.shutdown()

