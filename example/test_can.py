import can
import doog_can as dc
import time

bus1 = dc.can_init("can1")
ka1 = dc.KeepAlive(start_number=1, stop_number=1, bus=bus1)
ka1.start()

motor1 = dc.Motor(bus=bus1, node_id=1)

def msg_ask() -> None:
    print(f"====================")
    id, msg = motor1.ask_status()
    print(f"ID: {id}")
    print(f"位置: {msg.status} 速度: {msg.speed} 电流: {msg.current} 模式: {msg.mode} bus电压: {msg.bus_voltage}")
    print("====================")

msg_ask()

motor1.set_mode(1)
print("此时为模式1开环模式检测")
msg_ask()


for i in range(150):
    msg_ask()
    print(f"第 {i} 次查询 总共 150")

# motor1.set_mode(3)
# print("此时为模式3对齐模式检测")
# msg_ask()

print("开始暂停 测试ka1")
time.sleep(0.5)
print("暂停结束,关闭ka1 bus1")
ka1.stop()
bus1.shutdown()