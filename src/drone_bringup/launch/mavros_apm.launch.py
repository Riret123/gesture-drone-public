"""Launch installed MAVROS ArduPilot configuration with an explicit FCU endpoint.

No physical serial device is selected by default. Target IDs remain 1/1 and GCS
forwarding remains empty unless explicitly supplied. Resolve PCB/UART identity,
baud, power and routing using docs/core/BRINGUP.md before manual observation.
Only physically isolated SITL may be used for automated flight scenarios.
This wrapper does not configure FC parameters or establish hardware identity.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    mavros_share = get_package_share_directory('mavros')

    fcu_url_arg = DeclareLaunchArgument(
        'fcu_url',
        # Explicit endpoint required; never select a physical FC by omission.
        description='Порт+скорость соединения с AERO SELFIE H743, '
                     'формат <устройство>:<baud>',
    )
    gcs_url_arg = DeclareLaunchArgument(
        'gcs_url',
        default_value='',
        description='Необязательный проброс потока в GCS (Mission Planner и т.п.)',
    )
    tgt_system_arg = DeclareLaunchArgument('tgt_system', default_value='1')
    tgt_component_arg = DeclareLaunchArgument('tgt_component', default_value='1')

    apm_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(mavros_share, 'launch', 'apm.launch')
        ),
        launch_arguments={
            'fcu_url': LaunchConfiguration('fcu_url'),
            'gcs_url': LaunchConfiguration('gcs_url'),
            'tgt_system': LaunchConfiguration('tgt_system'),
            'tgt_component': LaunchConfiguration('tgt_component'),
        }.items(),
    )

    return LaunchDescription([
        fcu_url_arg,
        gcs_url_arg,
        tgt_system_arg,
        tgt_component_arg,
        apm_launch,
    ])
