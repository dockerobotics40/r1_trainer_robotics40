#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

ROOT_SCENE = "/home/samares06/unitree_mujoco/unitree_robots/r1/scene.xml"


def load_xml_recursive(xml_path, visited=None):
    """
    Carga un XML de MuJoCo y resuelve includes simples:
    <include file="r1.xml"/>
    """
    if visited is None:
        visited = set()

    xml_path = os.path.abspath(xml_path)

    if xml_path in visited:
        return []

    visited.add(xml_path)

    if not os.path.isfile(xml_path):
        print(f"[WARN] No existe: {xml_path}")
        return []

    base_dir = os.path.dirname(xml_path)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] No se pudo leer XML: {xml_path}")
        print(e)
        return []

    roots = [(xml_path, root)]

    for include in root.findall(".//include"):
        inc_file = include.attrib.get("file")
        if inc_file:
            inc_path = os.path.join(base_dir, inc_file)
            roots.extend(load_xml_recursive(inc_path, visited))

    return roots


def find_all_elements(roots, tag_name):
    results = []
    for xml_path, root in roots:
        for elem in root.findall(f".//{tag_name}"):
            results.append((xml_path, elem))
    return results


def main():
    print("\n=== INSPECTOR XML UNITREE R1 ===")
    print(f"Escena principal: {ROOT_SCENE}")

    roots = load_xml_recursive(ROOT_SCENE)

    print("\n=== ARCHIVOS XML CARGADOS ===")
    for xml_path, _ in roots:
        print(xml_path)

    joints = find_all_elements(roots, "joint")
    actuators = []

    actuator_tags = [
        "motor",
        "position",
        "velocity",
        "general",
        "intvelocity",
        "damper",
        "cylinder",
        "muscle",
        "adhesion",
    ]

    for tag in actuator_tags:
        actuators.extend(find_all_elements(roots, tag))

    print("\n=== JOINTS ENCONTRADOS ===")
    print("idx_xml | nombre | tipo | rango | archivo")

    named_joints = []

    for idx, (xml_path, joint) in enumerate(joints):
        name = joint.attrib.get("name", "")
        jtype = joint.attrib.get("type", "hinge")
        joint_range = joint.attrib.get("range", "sin rango")
        limited = joint.attrib.get("limited", "")
        damping = joint.attrib.get("damping", "")

        if name:
            named_joints.append(name)

        print(
            f"{idx:02d} | {name} | type={jtype} | "
            f"range={joint_range} | limited={limited} | damping={damping} | "
            f"{xml_path}"
        )

    print("\n=== ACTUADORES / MOTORES ENCONTRADOS ===")
    print("idx_act | tag | nombre_actuador | joint_asociado | ctrlrange | archivo")

    for idx, (xml_path, act) in enumerate(actuators):
        tag = act.tag
        name = act.attrib.get("name", "")
        joint = act.attrib.get("joint", "")
        ctrlrange = act.attrib.get("ctrlrange", "sin ctrlrange")
        gear = act.attrib.get("gear", "")
        kp = act.attrib.get("kp", "")

        print(
            f"{idx:02d} | {tag} | {name} | joint={joint} | "
            f"ctrlrange={ctrlrange} | gear={gear} | kp={kp} | {xml_path}"
        )

    print("\n=== RESUMEN ===")
    print(f"Total joints XML: {len(joints)}")
    print(f"Total actuadores detectados: {len(actuators)}")
    print(f"Joints con nombre: {len(named_joints)}")

    print("\n[OK] Inspeccion XML finalizada.\n")


if __name__ == "__main__":
    main()
