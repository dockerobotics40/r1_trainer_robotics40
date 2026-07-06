import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/docker/camara_r1_ws/install/r1_camera_viewer'
