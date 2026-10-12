test:
		PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -v

can:
		sudo ip link set can0 type can bitrate 1000000
		sudo ip link set can0 up

can_text:
		ip -details link show can0