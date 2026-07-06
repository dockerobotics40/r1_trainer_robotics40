#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path

XML_PATH = Path("/home/samares06/unitree_mujoco/unitree_robots/r1/r1.xml")

JOINTS = [
    "left_hip_pitch_joint",
    "left_hip_roll_joint",
    "left_hip_yaw_joint",
    "left_knee_joint",
    "left_ankle_pitch_joint",
    "left_ankle_roll_joint",

    "right_hip_pitch_joint",
    "right_hip_roll_joint",
    "right_hip_yaw_joint",
    "right_knee_joint",
    "right_ankle_pitch_joint",
    "right_ankle_roll_joint",

    "waist_roll_joint",
    "waist_yaw_joint",

    "left_shoulder_pitch_joint",
    "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint",
    "left_elbow_joint",
    "left_wrist_roll_joint",

    "right_shoulder_pitch_joint",
    "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint",
    "right_elbow_joint",
    "right_wrist_roll_joint",

    "head_pitch_joint",
    "head_yaw_joint",
]


def main():
    if not XML_PATH.exists():
        raise FileNotFoundError(XML_PATH)

    backup = XML_PATH.with_suffix(".xml.bak_patch_sensors")
    backup.write_text(XML_PATH.read_text())
    print(f"[OK] Backup creado: {backup}")

    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    sensor = root.find("sensor")
    if sensor is None:
        sensor = ET.SubElement(root, "sensor")

    existing_names = {
        elem.attrib.get("name")
        for elem in sensor
        if elem.attrib.get("name")
    }

    # Evitar duplicar si el parche se ejecuta más de una vez.
    expected_first = "left_hip_pitch_joint_pos"
    if expected_first in existing_names:
        print("[INFO] Los sensores articulares ya existen. No se modifica el XML.")
        return

    new_sensors = []

    # 1) Primero posiciones: sensordata[0 : 26]
    for joint in JOINTS:
        new_sensors.append(
            ET.Element("jointpos", {
                "name": f"{joint}_pos",
                "joint": joint
            })
        )

    # 2) Luego velocidades: sensordata[26 : 52]
    for joint in JOINTS:
        new_sensors.append(
            ET.Element("jointvel", {
                "name": f"{joint}_vel",
                "joint": joint
            })
        )

    # 3) Luego fuerzas/torques de actuador: sensordata[52 : 78]
    for joint in JOINTS:
        actuator = f"{joint}_ctrl"
        new_sensors.append(
            ET.Element("actuatorfrc", {
                "name": f"{joint}_tau",
                "actuator": actuator
            })
        )

    # Insertar al inicio del bloque <sensor>, antes de pelvis/IMU.
    for elem in reversed(new_sensors):
        sensor.insert(0, elem)

    # ET.indent no existe en Python 3.8. El XML sigue siendo valido sin pretty-print.
    tree.write(XML_PATH, encoding="utf-8", xml_declaration=False)

    print(f"[OK] Sensores agregados al XML: {XML_PATH}")
    print(f"[OK] Total sensores articulares agregados: {len(new_sensors)}")
    print("[INFO] Reinicia unitree_mujoco para cargar el XML modificado.")


if __name__ == "__main__":
    main()
