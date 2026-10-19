import doog_can as dc
import can
import time
from doog_can import StatusReport

bus1 = dc.can_init("can2")
# 定义bus1

motor1 = dc.Motor(bus=bus1, node_id=1)
print("定义电机1")

send_threading = dc.Transmit_Threading(bus=bus1)
recv_threading = dc.Receive_Threading(bus=bus1)
print("初始化发送/接受线程")

ka1 = dc.KeepAlive(start_number=1, stop_number=1, bus=bus1, send_threading=send_threading)

try:
    send_threading.my_start()
    recv_threading.my_start()
    ka1.start()
    print("开启发送线程/接受线程/保活")
    now, older = time.time(), time.time() 

    now = time.time()
    older = time.time()
    for i in range(6):
        msg = motor1.mode_build(i)
        print(f"切换为模式{i}")
        assert msg is not None
        send_threading.transmit_slot(msg)

        msg = motor1.ask_status_build()
        print("查询状态")
        assert msg is not None
        send_threading.transmit_slot(msg)

        msg_recv = recv_threading.receive_slot()
        assert msg_recv is not None
        id, model = motor1.msg_recv(msg_recv)
        print(f"id is {id}, model is {model}")

finally:
    ka1.stop()
    send_threading.my_stop()
    recv_threading.my_stop()
    bus1.shutdown()
