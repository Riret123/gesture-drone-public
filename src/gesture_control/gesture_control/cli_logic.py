"""Portable dronectl argument parsing; dry run unless --send is explicit."""
import argparse

COMMANDS = {'takeoff': 'open_palm', 'land': 'land', 'hold': 'hold', 'emergency': 'emergency'}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='SITL-only command publisher; dry run by default')
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('--send', action='store_true')
    parser.add_argument('--sitl-isolated', action='store_true',
                        help='attest physical FC isolation and SITL routing')
    args = parser.parse_args(argv)
    if args.send and not args.sitl_isolated:
        parser.error('--send requires --sitl-isolated; this does not detect hardware')
    return COMMANDS[args.command], args.send
