#!/usr/bin/env python3
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

low_state = None


def low_state_handler(msg: LowState_):
    global low_state
    low_state = msg


def main():
    domain_id = 0
    interface = "lo"

    if len(sys.argv) > 1:
        interface = sys.argv[1]

    print(f"[INFO] Inicializando DDS")
    print(f"[INFO] domain_id = {domain_id}")
    print(f"[INFO] interface = {interface}")

    ChannelFactoryInitialize(domain_id, interface)

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init(low_state_handler, 10)

    print("[INFO] Esperando LowState por topic: rt/lowstate")

    t0 = time.time()
    while time.time() - t0 < 10.0:
        if low_state is not None:
            break
        time.sleep(0.1)

    if low_state is None:
        print("[ERROR] No llego LowState en domain_id=0, interface=lo.")
        print("[DIAGNOSTICO] El simulador puede estar publicando otro tipo de mensaje o no estar publicando rt/lowstate.")
        return

    print("\n[OK] LowState recibido.")
    print(f"mode_machine: {getattr(low_state, 'mode_machine', 'N/A')}")
    print(f"cantidad motor_state: {len(low_state.motor_state)}")

    print("\n=== MOTOR_STATE DISPONIBLE ===")
    print("idx | q | dq | tau_est")

    for i in range(min(40, len(low_state.motor_state))):
        m = low_state.motor_state[i]
        q = float(getattr(m, "q", 0.0))
        dq = float(getattr(m, "dq", 0.0))
        tau_est = float(getattr(m, "tau_est", 0.0))
        print(f"{i:02d} | {q:+.6f} | {dq:+.6f} | {tau_est:+.6f}")

    print("\n[FIN]")


if __name__ == "__main__":
    main()
