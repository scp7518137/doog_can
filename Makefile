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