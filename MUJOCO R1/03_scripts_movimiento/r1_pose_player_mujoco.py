#!/usr/bin/env python3
import sys
import time
import json
import os

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread


ACTIVE_MOTOR_COUNT = 26

LEG_JOINTS = list(range(0, 12))
WAIST_JOINTS = [12, 13]
LEFT_ARM_JOINTS = [14, 15, 16, 17, 18]
RIGHT_ARM_JOINTS = [19, 20, 21, 22, 23]
HEAD_JOINTS = [24, 25]

POSE_JOINTS = WAIST_JOINTS + LEFT_ARM_JOINTS + RIGHT_ARM_JOINTS + HEAD_JOINTS


JOINT_NAMES = {
    0: "left_hip_pitch_joint",
    1: "left_hip_roll_joint",
    2: "left_hip_yaw_joint",
    3: "left_knee_joint",
    4: "left_ankle_pitch_joint",
    5: "left_ankle_roll_joint",

    6: "right_hip_pitch_joint",
    7: "right_hip_roll_joint",
    8: "right_hip_yaw_joint",
    9: "right_knee_joint",
    10: "right_ankle_pitch_joint",
    11: "right_ankle_roll_joint",

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


JOINT_LIMITS = {
    0: [-2.932153143, 2.548180708],
    1: [-1.047197551, 1.745329252],
    2: [-2.7402, 2.7402],
    3: [-0.174532925, 2.42600766],
    4: [-0.87266, 0.57596],
    5: [-0.2618, 0.2618],

    6: [-2.932153143, 2.548180708],
    7: [-1.745329252, 1.047197551],
    8: [-2.7402, 2.7402],
    9: [-0.17453, 2.42600766],
    10: [-0.87266, 0.57596],
    11: [-0.261799388, 0.261799388],

    12: [-0.5236, 0.5236],
    13: [-2.618, 2.618],

    14: [-3.1416, 2.0944],
    15: [-0.22689, 2.4784],
    16: [-1.9199, 1.9199],
    17: [-0.97564, 2.1852],
    18: [-1.9199, 1.9199],

    19: [-3.1416, 2.0944],
    20: [-2.47849, 0.2268],
    21: [-1.9199, 1.9199],
    22: [-0.97564, 2.1852],
    23: [-1.9199, 1.9199],

    24: [-0.62832, 0.62832],
    25: [-2.0071, 2.0071]
}


def gains_for_joint(i):
    """
    Ganancias R1 v6.
    Objetivo: eliminar twitching de brazos antes de volver a probar poses amplias.
    """

    # Piernas: mantener estables.
    if i in LEG_JOINTS:
        return 12.0, 0.8

    # Cintura: suave.
    if i in WAIST_JOINTS:
        return 15.0, 1.0

    # Hombros y codos: más suave que v5.
    if i in [14, 15, 16, 17, 19, 20, 21, 22]:
        return 14.0, 1.2

    # Muñecas: muy suaves.
    if i in [18, 23]:
        return 8.0, 0.8

    # Cabeza.
    if i == 24:
        return 15.0, 0.8

    if i == 25:
        return 6.0, 0.4

    return 0.0, 0.0


class R1PosePlayer:
    def __init__(self, control_dt=0.002):
        self.control_dt = control_dt
        self.crc = CRC()

        self.low_state = None
        self.mode_machine = 0

        self.lowcmd_publisher = None
        self.lowstate_subscriber = None
        self.writer_thread = None

        self.q_init = [0.0 for _ in range(ACTIVE_MOTOR_COUNT)]
        self.target_pos = [0.0 for _ in range(ACTIVE_MOTOR_COUNT)]
        self.current_cmd_pos = [0.0 for _ in range(ACTIVE_MOTOR_COUNT)]

        self.T = 1.0
        self.t = 0.0

        # Rampa de activacion de ganancias.
        # Evita activar Kp/Kd de golpe al iniciar LowCmd.
        self.writer_start_time = None
        self.gain_ramp_duration = 2.5

    def low_state_handler(self, msg):
        self.low_state = msg
        if hasattr(msg, "mode_machine"):
            self.mode_machine = msg.mode_machine

    def init_channels(self):
        self.lowcmd_publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher.Init()

        self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.lowstate_subscriber.Init(self.low_state_handler, 10)

    def wait_lowstate(self, timeout=10.0):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.low_state is not None:
                return True
            time.sleep(0.05)
        return False

    def initialize_from_lowstate(self):
        for i in range(ACTIVE_MOTOR_COUNT):
            q = float(self.low_state.motor_state[i].q)
            self.q_init[i] = q
            self.target_pos[i] = q
            self.current_cmd_pos[i] = q

        print("\n[POSE INICIAL CAPTURADA]")
        for i in range(ACTIVE_MOTOR_COUNT):
            print(f"{i:02d} | {JOINT_NAMES.get(i, 'unknown'):<28} | {self.current_cmd_pos[i]:+.6f}")
        print("[FIN POSE INICIAL]\n")

    def interpolate(self, q0, q1):
        if self.T <= 0:
            return q1

        s = max(0.0, min(self.t / self.T, 1.0))
        return q0 + (q1 - q0) * s

    def gain_scale(self):
        if self.writer_start_time is None:
            return 0.0

        elapsed = time.time() - self.writer_start_time
        return max(0.0, min(elapsed / self.gain_ramp_duration, 1.0))

    def build_cmd(self):
        cmd = unitree_hg_msg_dds__LowCmd_()

        cmd.mode_pr = 0
        cmd.mode_machine = self.mode_machine

        for i in range(len(cmd.motor_cmd)):
            cmd.motor_cmd[i].mode = 1
            cmd.motor_cmd[i].q = 0.0
            cmd.motor_cmd[i].dq = 0.0
            cmd.motor_cmd[i].tau = 0.0
            cmd.motor_cmd[i].kp = 0.0
            cmd.motor_cmd[i].kd = 0.0

        for i in range(ACTIVE_MOTOR_COUNT):
            kp, kd = gains_for_joint(i)
            scale = self.gain_scale()
            kp *= scale
            kd *= scale

            q = self.interpolate(self.q_init[i], self.target_pos[i])

            cmd.motor_cmd[i].mode = 1
            cmd.motor_cmd[i].q = float(q)
            cmd.motor_cmd[i].dq = 0.0
            cmd.motor_cmd[i].tau = 0.0
            cmd.motor_cmd[i].kp = kp
            cmd.motor_cmd[i].kd = kd

        cmd.crc = self.crc.Crc(cmd)
        return cmd

    def lowcmd_write(self):
        if self.low_state is None:
            return

        cmd = self.build_cmd()
        self.lowcmd_publisher.Write(cmd)

        self.t += self.control_dt

    def start_writer(self):
        if self.writer_thread is None:
            self.writer_start_time = time.time()
            self.writer_thread = RecurrentThread(
                self.control_dt,
                target=self.lowcmd_write,
                name="r1_lowcmd_writer"
            )
            self.writer_thread.Start()
            print("[INFO] LowCmd writer iniciado.")

    def validate_positions(self, updates):
        valid = {}

        for k, v in updates.items():
            try:
                idx = int(k)
                value = float(v)
            except Exception:
                print(f"[WARN] Posicion ignorada por formato invalido: {k}: {v}")
                continue

            if idx < 0 or idx >= ACTIVE_MOTOR_COUNT:
                print(f"[WARN] Indice fuera de rango ignorado: {idx}")
                continue

            if idx not in POSE_JOINTS:
                print(f"[WARN] Indice {idx} pertenece a piernas. Ignorado para rutinas de poses.")
                continue

            lo, hi = JOINT_LIMITS[idx]
            if value < lo or value > hi:
                print(
                    f"[WARN] Valor fuera de rango en {idx} "
                    f"({JOINT_NAMES.get(idx)}): {value:.6f}. "
                    f"Rango permitido [{lo:.6f}, {hi:.6f}]. Se limita."
                )
                value = max(lo, min(hi, value))

            valid[idx] = value

        return valid

    def move_to(self, updates, duration=1.0):
        if self.low_state is None:
            raise RuntimeError("No hay LowState. No se puede mover de forma segura.")

        valid_updates = self.validate_positions(updates)

        for i in range(ACTIVE_MOTOR_COUNT):
            self.q_init[i] = self.current_cmd_pos[i]
            self.target_pos[i] = self.current_cmd_pos[i]

        for idx, value in valid_updates.items():
            self.target_pos[idx] = value

        self.T = max(0.05, float(duration))
        self.t = 0.0

        while self.t < self.T:
            time.sleep(self.control_dt)

        self.t = self.T

        for i in range(ACTIVE_MOTOR_COUNT):
            self.current_cmd_pos[i] = self.target_pos[i]
            self.q_init[i] = self.target_pos[i]

        time.sleep(0.05)

    def play_routine(self, routine):
        name = routine.get("nombre_rutina", "rutina_sin_nombre")
        pasos = routine.get("pasos", [])

        print(f"\n[INFO] Ejecutando rutina R1: {name}")
        print(f"[INFO] Numero de pasos: {len(pasos)}")

        for idx, paso in enumerate(pasos, start=1):
            pname = paso.get("nombre", f"Paso {idx}")
            dur = float(paso.get("duracion", 1.0))
            posiciones = paso.get("posiciones", {})

            print(f"\n-> {pname}")
            print(f"   duracion = {dur:.2f}s")
            print(f"   joints = {list(posiciones.keys())}")

            self.move_to(posiciones, dur)

        print("\n[INFO] Rutina finalizada.")

    def hold_final(self, duration=2.0):
        print(f"[INFO] Sosteniendo postura final por {duration:.1f}s...")
        t0 = time.time()
        while time.time() - t0 < duration:
            cmd = self.build_cmd()
            self.lowcmd_publisher.Write(cmd)
            time.sleep(self.control_dt)

    def stop(self):
        self.hold_final(1.0)

        if self.writer_thread is not None:
            try:
                self.writer_thread.Wait()
            except Exception:
                pass
            self.writer_thread = None

        print("[INFO] Player detenido.")

    def load_routine(self, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"No existe el archivo: {filepath}")

        with open(filepath, "r") as f:
            content = f.read().strip()

        routine = json.loads(content)

        if "pasos" not in routine:
            raise ValueError("El archivo debe tener una clave principal 'pasos'.")

        return routine


def main():
    print("[INFO] R1 Pose Player MuJoCo")
    print("[INFO] Usando Actuator_index corregido.")
    print("[INFO] Usar solo con R1 en unitree_mujoco y XML parchado con sensores articulares.")

    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python3 scripts/r1_pose_player_mujoco.py routines_txt/archivo.txt")
        return

    routine_path = sys.argv[1]

    ChannelFactoryInitialize(0, "lo")

    player = R1PosePlayer(control_dt=0.002)
    player.init_channels()

    print("[INFO] Esperando LowState...")

    if not player.wait_lowstate():
        print("[ERROR] No llego LowState. Verifica que unitree_mujoco este abierto.")
        return

    player.initialize_from_lowstate()

    input("[ACCION] Verifica que el R1 este estable en MuJoCo. Presiona Enter para iniciar...")

    routine = player.load_routine(routine_path)

    try:
        player.start_writer()
        player.play_routine(routine)

    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C detectado. Deteniendo...")

    finally:
        player.stop()
        print("[INFO] Programa terminado.")


if __name__ == "__main__":
    main()
