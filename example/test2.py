import can
import doog_can as dc

bus1 = dc.can_init()
motor1 = dc.Motor(bus=bus1, node_id=1)
id, msg = motor1.ask_status()
print(f"this id is motor{id}")

print(f"位置: {msg.status}\n速度: {msg.speed}\n电流: {msg.current}\n模式: {msg.mode}\nbus电压: {msg.bus_voltage}")
bus1.shutdown()