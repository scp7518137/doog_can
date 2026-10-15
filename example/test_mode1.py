import can
import doog_can as dc
import time

bus1 = dc.can_init("can1")
ka1 = dc.KeepAlive(start_number=1, stop_number=1, bus=bus1)
ka1.start()

motor1 = dc.Motor(bus=bus1, node_id=1)

i: int = 0
def msg_ask() -> None:
    print("===== 返回当前status解析 =====")
    id, msg = motor1.ask_status()
    print(f"ID: {id}")
    print(f"位置: {msg.status} 速度: {msg.speed} 电流: {msg.current} 模式: {msg.mode} bus电压: {msg.bus_voltage}")
    print("====================")

def msg_openask() -> None:
    print("===== 返回当前angle解析 =====")
    id, msg = motor1.ask_open_to_angle()
    print(f"ID: {id}")
    print(f"运动状态: {msg.status} 设置电压: {msg.settingvoltage} bus电压: {msg.busvoltage} 剩余角度: {msg.remainangle}")
    print("====================")

msg_ask()

print("切换为开环模式")
motor1.set_mode(1)
i += 1
msg_ask()

print("正转30'")
motor1.open_to_angle(30)
msg_openask()
while(1):
    id, msg = motor1.ask_open_to_angle()
    if msg.status == 2:
        break
    print("running")
print("达到指定位置")
msg_openask()

ka1.stop()
bus1.shutdown()