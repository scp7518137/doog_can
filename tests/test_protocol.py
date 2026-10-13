from doog_can.protocol import build_frame


def test_encode_set_speed():
    frame_id, data = build_frame(node_id=1, cmd=1, value=10)
    assert frame_id == 0x101
    assert data.hex() == "0164000000000000"

    frame_id, data = build_frame(node_id=1, cmd=1, value=-5)
    assert frame_id == 0x101
    assert data.hex() == "01ceff0000000000"


def test_encode_set_voltage():
    frame_id, data = build_frame(node_id=1, cmd=2, value=0.6)
    assert frame_id == 0x101
    assert data.hex() == "023c000000000000"

def test_encode_set_mode():
    frame_id, data = build_frame(node_id=1, cmd=3, value=1)
    assert frame_id == 0x101
    assert data.hex() == "0301000000000000"

    frame_id, data = build_frame(node_id=1, cmd=3, value=4)
    assert frame_id == 0x101
    assert data.hex() == "0304000000000000"

def test_encode_set_direction():
    frame_id, data = build_frame(node_id=1, cmd=4, value=1)
    assert frame_id == 0x101
    assert data.hex() == "0401000000000000"

def test_encode_set_torque():
    frame_id, data = build_frame(node_id=1, cmd=5, value=1)
    assert frame_id == 0x101
    assert data.hex() == "0564000000000000"

def test_encode_set_position():
    frame_id, data = build_frame(node_id=1, cmd=6, value=1)
    assert frame_id == 0x101
    assert data.hex() == "0610270000000000"

def test_encode_set_Opentoangle():
    frame_id, data = build_frame(node_id=1, cmd=7, value=90)
    assert frame_id == 0x101
    assert data.hex() == "0784030000000000"

    frame_id, data = build_frame(node_id=1, cmd=7, value=-90)
    assert frame_id == 0x101
    assert data.hex() == "077cfc0000000000"

def test_ask_status():
    frame_id, data = build_frame(node_id=1, cmd=16, value=1)
    assert frame_id == 0x101
    assert data.hex() == "1000000000000000"

def test_ask_Opentoangle():
    frame_id, data = build_frame(node_id=1, cmd=9, value=1)
    assert frame_id == 0x101
    assert data.hex() == "0900000000000000"