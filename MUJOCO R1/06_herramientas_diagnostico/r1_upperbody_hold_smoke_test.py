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


def build_hold_cmd(base_q):
    crc = CRC()
    cmd = unitree_hg_msg_dds__LowCmd_()

    cmd.mode_pr = 0
    cmd.mode_machine = getattr(low_state, "mode_machine", 0)

    # Inicializar todo el arreglo IDL en modo sin torque efectivo.
    for i in range(len(cmd.motor_cmd)):
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].q = 0.0
        cmd.motor_cmd[i].dq = 0.0
        cmd.motor_cmd[i].tau = 0.0
        cmd.motor_cmd[i].kp = 0.0
        cmd.motor_cmd[i].kd = 0.0

    # Solo torso, brazos y cabeza.
    # Piernas quedan sin PD desde este script para evitar posturas erróneas.
    for i in CONTROL_JOINTS:
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].q = float(base_q[i])
        cmd.motor_cmd[i].dq = 0.0
        cmd.motor_cmd[i].tau = 0.0
        cmd.motor_cmd[i].kp = 20.0
        cmd.motor_cmd[i].kd = 1.0

    cmd.crc = crc.Crc(cmd)
    return cmd


def main():
    print("[INFO] Smoke test R1: sostener torso, brazos y cabeza.")
    print("[INFO] No se ordena ningun movimiento nuevo.")
    print("[INFO] No se controlan piernas desde este script.")

    ChannelFactoryInitialize(0, "lo")

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init(low_state_handler, 10)

    pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    pub.Init()

    print("[INFO] Esperando LowState...")

    if not wait_lowstate():
        print("[ERROR] No llego LowState.")
        return

    base_q = [0.0 for _ in range(len(low_state.motor_state))]

    for i in range(ACTIVE_MOTOR_COUNT):
        base_q[i] = float(low_state.motor_state[i].q)

    print("[OK] LowState recibido.")
    print("[INFO] Enviando hold por 5 segundos...")

    cmd = build_hold_cmd(base_q)

    t0 = time.time()
    while time.time() - t0 < 5.0:
        pub.Write(cmd)
        time.sleep(0.002)

    print("[OK] Smoke test finalizado.")


if __name__ == "__main__":
    main()
