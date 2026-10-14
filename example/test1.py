import can
import doog_can as dc

bus1 = dc.can_init("can1")
ka1 = dc.KeepAlive(start_number=1, stop_number=1, bus=bus1)
ka1.start()

motor1 = dc.Motor(bus=bus1, node_id=1)

i: int = 0
def msg_ask(i: int) -> None:
    print(f"===== {i} =====")
    id, msg = motor1.ask_status()
    print(f"ID: {id}")
    print(f"位置: {msg.status} 速度: {msg.speed} 电流: {msg.current} 模式: {msg.mode} bus电压: {msg.bus_voltage}")
    print("====================")

msg_ask(i)

motor1.set_mode(1)
i += 1
print("此时为模式1开环模式检测")
msg_ask(i)

motor1.set_mode(3)
i += 1
print("此时为模式3对齐模式检测")
msg_ask(i)



ka1.stop()
bus1.shutdown()