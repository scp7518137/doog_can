import doog_can as dc
import can
import time

bus1 = dc.can_init("can1")
# 定义bus1
motor1 = dc.Motor(bus=bus1, node_id=1)
# 定义电机1
send_threading = dc.Transmit_Threading(bus=bus1)
# 初始化发送线程
send_threading.my_start()
# 开启发送线程
msg = motor1.mode_build(1)
# 生成msg
assert msg is not None
send_threading.transmit_slot(msg)
# 填充
time.sleep(0.5)
send_threading.my_stop()

