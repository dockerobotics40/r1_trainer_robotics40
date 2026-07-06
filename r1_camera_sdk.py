#!/usr/bin/env python3
"""
Visor de cámara R1 con selección de resolución y modo multi-vista.

Resoluciones disponibles (del mismo sensor frontal):
  720p → 1280x720  (VideoClient nativo)
  360p → 640x360   (downscale)
  180p → 320x180   (downscale)

Controles:
  1 → solo 720p
  2 → solo 360p
  3 → solo 180p
  a → todas simultáneas
  ESC → salir
"""
import sys
import os
import cv2
import numpy as np

_SDK_PATH = os.path.expanduser("~/unitree_sdk2_python")
if _SDK_PATH not in sys.path:
    sys.path.insert(0, _SDK_PATH)

os.environ.setdefault(
    "CYCLONEDDS_URI",
    f"file://{os.path.expanduser('~')}/unitree_ros2/ros_config.xml"
)

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

SIZES = {
    "720p": (1280, 720),
    "360p": (640, 360),
    "180p": (320, 180),
}

MODES = ["720p", "360p", "180p", "all"]
MODE_KEYS = {ord("1"): "720p", ord("2"): "360p", ord("3"): "180p", ord("a"): "all"}

HELP = (
    "R1 Camera Viewer | "
    "1=720p  2=360p  3=180p  A=todas  ESC=salir"
)


def resize(frame: np.ndarray, res: str) -> np.ndarray:
    w, h = SIZES[res]
    if frame.shape[1] == w and frame.shape[0] == h:
        return frame
    return cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)


def draw_label(frame: np.ndarray, text: str) -> np.ndarray:
    out = frame.copy()
    cv2.putText(out, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(out, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def build_all_view(frame720: np.ndarray) -> np.ndarray:
    """
    Diseño:
      ┌──────────────────────────┐
      │        720p (grande)     │
      ├────────────┬─────────────┤
      │    360p    │  180p+pad   │
      └────────────┴─────────────┘
    """
    f720 = draw_label(frame720, "720p  1280x720")
    f360 = draw_label(resize(frame720, "360p"), "360p  640x360")
    f180 = draw_label(resize(frame720, "180p"), "180p  320x180")

    row_h = f360.shape[0]   # 360
    row_w = f720.shape[1]   # 1280

    # Centrar 180p verticalmente dentro de un bloque de row_h x 640px
    block_w = row_w - f360.shape[1]  # 640
    block = np.zeros((row_h, block_w, 3), dtype=np.uint8)
    y_off = (row_h - f180.shape[0]) // 2
    x_off = (block_w - f180.shape[1]) // 2
    block[y_off:y_off + f180.shape[0], x_off:x_off + f180.shape[1]] = f180

    bottom = np.hstack([f360, block])
    return np.vstack([f720, bottom])


def main() -> None:
    iface = sys.argv[1] if len(sys.argv) > 1 else ""
    mode  = sys.argv[2] if len(sys.argv) > 2 else "720p"
    if mode not in MODES:
        mode = "720p"

    if iface:
        ChannelFactoryInitialize(0, iface)
    else:
        ChannelFactoryInitialize(0)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    print(HELP, flush=True)
    print(f"Modo inicial: {mode}", flush=True)

    window = "R1 Camera"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    while True:
        code, data = client.GetImageSample()
        if code != 0:
            print(f"Error frame: code={code}", flush=True)
            if cv2.waitKey(100) == 27:
                break
            continue

        raw = np.frombuffer(bytes(data), dtype=np.uint8)
        frame = cv2.imdecode(raw, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        if mode == "all":
            display = build_all_view(frame)
            cv2.setWindowTitle(window, "R1 Camera — todas las resoluciones")
        else:
            display = draw_label(resize(frame, mode), f"{mode}  {SIZES[mode][0]}x{SIZES[mode][1]}")
            cv2.setWindowTitle(window, f"R1 Camera — {mode}")

        cv2.imshow(window, display)

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            break
        if key in MODE_KEYS:
            mode = MODE_KEYS[key]
            print(f"Modo: {mode}", flush=True)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
