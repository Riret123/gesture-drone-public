# Engineering boundaries

New portable logic lives inside the existing setuptools-discovered gesture_control
package. No new ROS nodes were introduced except dronectl, registered in setup.py;
its std_msgs/rclpy dependencies already exist in package.xml. Offline modules need
only Python standard library. No ROS runtime or MediaPipe imports in logic.

Tests parse package Python syntax, check pure-module import boundaries, package
resource/manifests and the new CLI entry point. Existing ROS tests require ament
and remain separate. Flake8/ament lint is not installed here; no lint pass claimed.
New public policy APIs include unit-bearing docstrings and type hints; legacy
source formatting and API documentation have not been rewritten wholesale.
