test:
		PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -v

can_up:
		sudo ip link set can1 type can bitrate 1000000
		sudo ip link set can1 up

can_text:
		ip -details link show can1

can_down:
		sudo ip link set can1 down
		ip -details link show can1