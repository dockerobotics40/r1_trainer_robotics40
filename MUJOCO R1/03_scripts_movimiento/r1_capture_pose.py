#!/usr/bin/env python3
import sys
import time
import json
from datetime import datetime

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

low_state = None

ACTIVE_MOTOR_COUNT = 26

JOINT_NAMES = {
    12: "waist_roll_joint",
    13: "waist_yaw_joint",

    14: "left_shoulder_pitch_joint",
    15: "left_shoulder_roll_joint",
    16: "left_shoulder_yaw_joint",
    17: "left_elbow_joint",
    18: "left_wrist_roll_joint",

    19: "right_shoulder_pitch_joint",
    20: "right_shoulder_roll_joint",
    21: "right_shoulder_yaw_joint",
    22: "right_elbow_joint",
    23: "right_wrist_roll_joint",

    24: "head_pitch_joint",
    25: "head_yaw_joint"
}

CONTROL_JOINTS = [
    12, 13,
    14, 15, 16, 17, 18,
    19, 20, 21, 22, 23,
    24, 25
]


def low_state_handler(msg: LowState_):
    global low_state
    low_state = msg


def wait_lowstate(timeout=10.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if low_state is not None:
            return True
        time.sleep(0.05)
    return False


def capture_pose():
    posiciones = {}

    for idx in CONTROL_JOINTS:
        q = float(low_state.motor_state[idx].q)
        posiciones[str(idx)] = round(q, 6)

    return posiciones


def print_named_table(posiciones):
    print("\n=== CAPTURA R1 CORREGIDA POR ACTUATOR_INDEX ===")
    print("idx | joint | q")
    for idx in CONTROL_JOINTS:
        key = str(idx)
        name = JOINT_NAMES.get(idx, "unknown")
        value = posiciones[key]
        print(f"{idx:02d} | {name:<28} | {value:+.6f}")


def main():
    domain_id = 0
    interface = "lo"

    if len(sys.argv) > 1:
        interface = sys.argv[1]

    print("[INFO] Capturador de poses R1")
    print("[INFO] Usando Actuator_index, no Joint_index.")
    print(f"[INFO] active_motor_count = {ACTIVE_MOTOR_COUNT}")
    print(f"[INFO] domain_id = {domain_id}")
    print(f"[INFO] interface = {interface}")

    ChannelFactoryInitialize(domain_id, interface)

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init(low_state_handler, 10)

    print("[INFO] Esperando LowState...")

    if not wait_lowstate():
        print("[ERROR] No llego LowState. Verifica que unitree_mujoco este abierto con robot r1.")
        return

    posiciones = capture_pose()
    print_named_table(posiciones)

    paso = {
        "nombre": "Paso capturado desde simulador",
        "posiciones": posiciones,
        "duracion": 1.5
    }

    print("\n=== BLOQUE JSON PARA PEGAR EN UN TXT ===")
    print(json.dumps(paso, indent=2, ensure_ascii=False))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"captures/r1_pose_capture_{timestamp}.txt"

    with open(output_path, "w") as f:
        f.write(json.dumps(paso, indent=2, ensure_ascii=False))

    print(f"\n[OK] Captura guardada en: {output_path}")


if __name__ == "__main__":
    main()
