from setuptools import setup
import os
from glob import glob

package_name = 'r1_camera_viewer'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Visor de cámara frontal del robot Unitree R1 vía ROS2',
    license='MIT',
    entry_points={
        'console_scripts': [
            'camera_viewer = r1_camera_viewer.camera_viewer_node:main',
        ],
    },
)
