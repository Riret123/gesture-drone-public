"""Explicit keyboard command mapping, independent of terminal and ROS."""
KEY_COMMANDS = {'t': 'open_palm', 'l': 'land', 'h': 'hold', ' ': 'emergency'}


def command_for_key(key):
    return KEY_COMMANDS.get(key.lower())
