#!/usr/bin/env python3
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

from unitree_sdk2py.utils.crc import CRC

low_state = None

ACTIVE_MOTOR_COUNT = 26

LEG_JOINTS = list(range(0, 12))
WAIST_JOINTS = [12, 13]
ARM_JOINTS = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
HEAD_JOINTS = [24, 25]


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


def gains_for_joint(i):
    if i in LEG_JOINTS:
        return 70.0, 2.0
    if i in WAIST_JOINTS:
        return 35.0, 1.5
    if i in ARM_JOINTS:
        return 25.0, 1.0
    if i in HEAD_JOINTS:
        return 15.0, 0.8
    return 0.0, 0.0


def build_hold_cmd(base_q):
    crc = CRC()
    cmd = unitree_hg_msg_dds__LowCmd_()

    cmd.mode_pr = 0
    cmd.mode_machine = getattr(low_state, "mode_machine", 0)

    for i in range(len(cmd.motor_cmd)):
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].q = 0.0
        cmd.motor_cmd[i].dq = 0.0
        cmd.motor_cmd[i].tau = 0.0
        cmd.motor_cmd[i].kp = 0.0
        cmd.motor_cmd[i].kd = 0.0

    for i in range(ACTIVE_MOTOR_COUNT):
        kp, kd = gains_for_joint(i)
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].q = float(base_q[i])
        cmd.motor_cmd[i].dq = 0.0
        cmd.motor_cmd[i].tau = 0.0
        cmd.motor_cmd[i].kp = kp
        cmd.motor_cmd[i].kd = kd

    cmd.crc = crc.Crc(cmd)
    return cmd


def main():
    print("[INFO] Smoke test R1: hold full body.")
    print("[INFO] Mantiene los 26 actuadores reales del R1 en su posicion actual.")
    print("[INFO] Usar solo en MuJoCo.")

    ChannelFactoryInitialize(0, "lo")

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init(low_state_handler, 10)

    pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    pub.Init()

    print("[INFO] Esperando LowState...")

    if not wait_lowstate():
        print("[ERROR] No llego LowState.")
        return

    base_q = [0.0 for _ in range(ACTIVE_MOTOR_COUNT)]

    for i in range(ACTIVE_MOTOR_COUNT):
        base_q[i] = float(low_state.motor_state[i].q)

    print("[OK] LowState recibido.")
    print("\n=== BASE_Q CAPTURADO ===")
    for i, q in enumerate(base_q):
        print(f"{i:02d}: {q:+.6f}")

    input("\n[ACCION] Mira el simulador. Presiona Enter para enviar hold full body por 8 segundos...")

    cmd = build_hold_cmd(base_q)

    t0 = time.time()
    while time.time() - t0 < 8.0:
        pub.Write(cmd)
        time.sleep(0.002)

    print("[OK] Smoke test full body finalizado.")


if __name__ == "__main__":
    main()
