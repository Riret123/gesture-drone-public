from setuptools import find_packages, setup

package_name = 'gesture_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='riret',
    maintainer_email='riret@todo.todo',
    description='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ Ð¶ÐµÑÑ‚Ð¾Ð² Ñ€ÑƒÐºÐ¸ (ÐºÑƒÐ»Ð°Ðº/Ð¾Ñ‚ÐºÑ€Ñ‹Ñ‚Ð°Ñ Ð»Ð°Ð´Ð¾Ð½ÑŒ) Ñ‡ÐµÑ€ÐµÐ· ÐºÐ°Ð¼ÐµÑ€Ñƒ Ð¸ MediaPipe, Ð¿ÑƒÐ±Ð»Ð¸ÐºÐ°Ñ†Ð¸Ñ Ð² /flight_cmd',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'gesture_node = gesture_control.gesture_node:main',
            'keyboard_teleop = gesture_control.keyboard_teleop:main',
            'dronectl = gesture_control.dronectl:main'
        ],
    },
)
