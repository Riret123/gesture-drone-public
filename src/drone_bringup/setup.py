import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'drone_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='riret',
    maintainer_email='riret@todo.todo',
    description='Launch-конфигурации для запуска дрона: MAVROS для AERO SELFIE H743 (ArduPilot) и т.п.',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'flight_cmd_bridge = drone_bringup.flight_cmd_bridge:main',
        ],
    },
)
