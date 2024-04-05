from sys import (
    stdout,
    stderr,
    exit
)
from argparse import ArgumentParser
from termcolor import (
    colored,
    cprint
)
from display_adapters import (
    DisplayMode,
    set_display_mode_for_device
)
from custom_types import DisplayAdapterException, PrimaryMonitorException, HdrException
from display_monitors import (
    get_all_display_monitors,
    DisplayMonitor,
    set_hdr_state_for_monitor,
    get_primary_monitor
)

# Application metadata
VERSION: str = "v3.0.1"
NAME: str = "ResolutionSwitcher"


def print_all_available_modes_for_monitor(monitor: DisplayMonitor):
    number_of_columns: int = 3

    print_message("[Available Modes]\n", 'blue', attrs=['bold'])

    for i in range(0, len(monitor.adapter.available_modes)):
        print_message(f"{monitor.adapter.available_modes[i]}".ljust(25), end='')

        if (i + 1) % number_of_columns == 0:
            print_message("")


def print_monitor_info(monitor: DisplayMonitor):
    justification: int = 16

    print_message(f"[{monitor.name}]\n", 'blue', attrs=['bold'])
    print_message(f"ID:".ljust(justification) + f"{monitor.identifier()}")
    print_message(f"Adapter:".ljust(justification) + f"{monitor.adapter.display_name}")
    print_message(f"Resolution:".ljust(justification) + f"{monitor.active_mode()}")
    print_message(f"Primary:".ljust(justification) + f"{monitor.is_primary()}")
    print_message(f"Attached:".ljust(justification) + f"{monitor.is_attached()}")

    hdr_supported = monitor.is_hdr_supported()

    print_message(f"HDR Supported:".ljust(justification) + f"{hdr_supported}")

    if hdr_supported:
        print_message(f"HDR Enabled:".ljust(justification) + f"{monitor.is_hdr_enabled()}")


def argument_parser() -> ArgumentParser:
    p = ArgumentParser(
        prog=NAME,
        description='Command line tool to change Windows display settings',
        usage=f'{NAME} --version | --monitors | --monitor <ID> | --width <width> --height <height> --refresh '
              f'<refresh> | hdr <true/false>'
    )

    version_group = p.add_argument_group()
    version_group.add_argument('--version', action='version', version=VERSION)

    monitor_group = p.add_mutually_exclusive_group()
    monitor_group.add_argument('--monitors', action='store_true', help='List all active monitors')
    monitor_group.add_argument('--monitor', type=str, help='List all available modes for a monitor')

    mode_change_group = p.add_argument_group()
    mode_change_group.add_argument('--width', type=int, help='The width of the new display mode')
    mode_change_group.add_argument('--height', type=int, help='The height of the new display mode')
    mode_change_group.add_argument('--refresh', type=int, help='The refresh rate of the new display mode')

    hdr_group = p.add_argument_group()
    hdr_group.add_argument('--hdr', type=str, help='Enable/Disable HDR on the monitor')

    return p


def print_message(message: str, color: str = None, attrs: list[str] = None, end: str = None, is_error: bool = False):
    file = stderr if is_error else stdout
    colored_message = colored(message, color, attrs=attrs)
    cprint(colored_message, color, attrs=attrs, end=end, file=file)


def print_success(message: str):
    colored_message = colored(message, 'green')
    cprint(colored_message)


def print_error(error: str):
    print_message("Error: " + error, 'red', attrs=['bold'])


if __name__ == '__main__':
    parser = argument_parser()
    args = parser.parse_args()

    all_monitors: list[DisplayMonitor] = get_all_display_monitors()

    if len(all_monitors) == 0:
        print_error("No monitors found")
        exit(-1)

    if args.width or args.height or args.refresh:
        should_change_resolution: bool = args.width is not None and args.height is not None and args.refresh is not None
        should_change_hdr: bool = args.hdr is not None

        if not should_change_resolution:
            print_error("Width, height and refresh rate are required")
            
            if not should_change_hdr:
                exit(-1)

        if should_change_hdr:
            if args.hdr.lower() not in ['true', 'false']:
                print_error("Valid values for HDR are 'true' or 'false'")
                exit(-1)

        try:
            identifier: str = args.monitor

            if identifier is None:
                print_message("Monitor ID not specified")
                print_message("Will attempt to identify primary monitor")
                identifier = get_primary_monitor(all_monitors).identifier()

            if should_change_resolution:
                display_mode: DisplayMode = DisplayMode(args.width, args.height, args.refresh)

                print_message(f'Attempting to change {identifier} settings to {str(display_mode)}')
                set_display_mode_for_device(display_mode, identifier)
                print_success("Display settings changed successfully")

            if should_change_hdr:
                for target_monitor in all_monitors:
                    if target_monitor.adapter.identifier == identifier:
                        if not target_monitor.is_hdr_supported():
                            print_success(f"{target_monitor.adapter.identifier} does not support HDR")
                            print_success("Exiting...")
                            exit(-1)

                        hdr_state = True if args.hdr.lower() == 'true' else False

                        print_message(f'Attempting to {"enable" if hdr_state else "disable"} HDR on {identifier}')
                        set_hdr_state_for_monitor(hdr_state, target_monitor)
                        print_success(f"HDR {'enabled' if hdr_state else 'disabled'} successfully")

        except DisplayAdapterException as e:
            print_error(str(e))
            exit(-1)

        except PrimaryMonitorException as e:
            print_error(str(e))
            exit(-1)

        except HdrException as e:
            print_error(f"Error when trying to change HDR state. Failed with error {str(e)}")
            exit(-1)

    elif args.monitor is not None:
        identifier: str = args.monitor

        for target_monitor in all_monitors:
            if target_monitor.adapter.identifier == identifier:
                print_message("")
                print_monitor_info(target_monitor)
                print_message("")
                print_all_available_modes_for_monitor(target_monitor)

                exit(0)

        print_error(f'Device {identifier} not found')
        exit(-1)

    else:
        print_message(f'Monitors found: {len(all_monitors)}\n')

        for target_monitor in all_monitors:
            print_monitor_info(target_monitor)
            print_message("")
