test:
		PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -v

git_mirror_up:

			git config --global url."https://githubfast.com/".insteadOf "https://github.com/"
			@echo "✅ 已开启 github 镜像 (githubfast.com)"

git_mirror_down:
			git config --global --unset url."https://githubfast.com/".insteadOf
			@echo "⬇️ 已关闭 github 镜像"

can_up:
		sudo ip link set can1 type can bitrate 1000000
		sudo ip link set can1 up

can_text:
		ip -details link show can1

can_down:
		sudo ip link set can1 down
		ip -details link show can1

can_reset:
		$(MAKE) can_down
		$(MAKE) can_up

usb_check_MAC:
		ip -br a

usb_set_MAC:
		sudo ip link set $(MAC) up
		cat /sys/class/net/$(MAC)/carrier
		sudo ip addr add 10.55.0.1/24 dev $(MAC)
		ping -c 10 10.55.0.2

usb_board_set:
		sudo modprobe g_ether
		sudo ip link set usb0 up
		sudo ip addr add 10.5.0.2/24 dev usb0