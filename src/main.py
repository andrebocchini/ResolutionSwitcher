from sys import exit
from argparse import ArgumentParser
from termcolor import colored, cprint

# Functions for getting display devices and settings
from win32api import EnumDisplayDevices
from win32api import EnumDisplaySettings
from win32api import ChangeDisplaySettingsEx

# Display device state flags
from win32con import DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
from win32con import DISPLAY_DEVICE_PRIMARY_DEVICE

# Display settings constants
from win32con import ENUM_CURRENT_SETTINGS

# Display mode fields
from win32con import DM_PELSWIDTH
from win32con import DM_PELSHEIGHT
from win32con import DM_DISPLAYFREQUENCY

# Resolution change results
from win32con import DISP_CHANGE_SUCCESSFUL
from win32con import DISP_CHANGE_RESTART
from win32con import DISP_CHANGE_BADFLAGS
from win32con import DISP_CHANGE_BADMODE
from win32con import DISP_CHANGE_BADPARAM
from win32con import DISP_CHANGE_FAILED
from win32con import DISP_CHANGE_NOTUPDATED
from win32con import DISP_CHANGE_BADDUALVIEW

from pywintypes import DEVMODEWType

# Application metadata
VERSION: str = "v2.0.1"
NAME: str = "ResolutionSwitcher"

# Terminal colors
TERM_COLOR_SUCCESS = 'green'
TERM_COLOR_ERROR = 'red'
TERM_COLOR_HEADER = 'blue'
TERM_COLOR_MESSAGE = None


class DisplayDevice:
    def __init__(self, device: DEVMODEWType):
        self.identifier: str = device.DeviceName
        self.display_name: str = device.DeviceString
        self.active_mode: DisplayMode = get_active_display_mode_for_device(device.DeviceName)
        self.available_modes: list[DisplayMode] = get_all_available_modes_for_device(device.DeviceName)
        self.is_attached: bool = is_attached_device(device.StateFlags)
        self.is_primary: bool = is_primary_device(device.StateFlags)

    def __str__(self):
        return self.identifier


class DisplayMode:
    def __init__(self, width: int, height: int, refresh: int):
        self.width: int = width
        self.height: int = height
        self.refresh: int = refresh

    def __str__(self):
        return str(self.width) + "x" + str(self.height) + " @ " + str(self.refresh) + "Hz"

    def as_devmodew_type(self) -> DEVMODEWType:
        devmode = DEVMODEWType()
        devmode.PelsWidth = self.width
        devmode.PelsHeight = self.height
        devmode.DisplayFrequency = self.refresh
        devmode.Fields = DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQUENCY
        return devmode


def is_attached_device(state_flags: int) -> bool:
    return state_flags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP == DISPLAY_DEVICE_ATTACHED_TO_DESKTOP


def is_primary_device(state_flags: int) -> bool:
    return state_flags & DISPLAY_DEVICE_PRIMARY_DEVICE == DISPLAY_DEVICE_PRIMARY_DEVICE


def get_all_display_devices() -> list[DisplayDevice]:
    devices: list[DisplayDevice] = []

    index_of_current_device: int = 0
    finished_searching_for_devices: bool = False

    while not finished_searching_for_devices:
        try:
            display_adapter: DEVMODEWType = EnumDisplayDevices(None, index_of_current_device, 0)
            device: DisplayDevice = DisplayDevice(display_adapter)

            devices.append(device)
        except:
            finished_searching_for_devices = True
        finally:
            index_of_current_device += 1

    return devices


def get_active_display_mode_for_device(device_identifier: str) -> DisplayMode | None:
    try:
        display_mode = EnumDisplaySettings(device_identifier, ENUM_CURRENT_SETTINGS)

        return DisplayMode(display_mode.PelsWidth, display_mode.PelsHeight, display_mode.DisplayFrequency)
    except:
        return None


def get_all_available_modes_for_device(device_identifier: str) -> list[DisplayMode]:
    modes: list[DisplayMode] = []

    # Tell Windows to cache display mode information
    EnumDisplaySettings(device_identifier, 0)

    index_of_current_mode: int = 1
    finished_getting_modes: bool = False

    while not finished_getting_modes:
        try:
            display_mode: DEVMODEWType = EnumDisplaySettings(device_identifier, index_of_current_mode)
            modes.append(
                DisplayMode(display_mode.PelsWidth, display_mode.PelsHeight, display_mode.DisplayFrequency)
            )
            index_of_current_mode += 1
        except:
            finished_getting_modes = True

    return modes


def print_device_info(device: DisplayDevice, detailed: bool = False):
    # Device details
    print_message(f'\n[{device.display_name}]', TERM_COLOR_HEADER, attrs=['bold'])
    print_message(f'Identifier: {device.identifier}')
    print_message(f'Active Mode: {str(device.active_mode)}')
    print_message(f'Primary: {str(device.is_primary)}')
    print_message(f'Attached: {str(device.is_attached)}')

    if not detailed:
        return

    print_message("\n[Available Modes]", TERM_COLOR_HEADER, attrs=['bold'])

    for i in range(0, len(device.available_modes), 3):
        try:
            print_message(f"{device.available_modes[i]}".ljust(25), end='')
            print_message(f"{device.available_modes[i + 1]}".ljust(25), end='')
            print_message(f"{device.available_modes[i + 2]}".ljust(25))
        except:
            pass


def set_device_mode(device_identifier: str, device_mode: DEVMODEWType) -> int:
    if device_mode is None:
        raise ValueError("Display settings cannot be empty")

    return ChangeDisplaySettingsEx(device_identifier, device_mode, 0)


def print_human_readable_mode_change_result(result: int):
    if result == DISP_CHANGE_SUCCESSFUL:
        print_success("Display settings changed successfully")
    elif result == DISP_CHANGE_RESTART:
        print_error("The computer must be restarted for the graphics mode to work")
    elif result == DISP_CHANGE_BADFLAGS:
        print_error("An invalid set of flags was passed in")
    elif result == DISP_CHANGE_BADMODE:
        print_error("The graphics mode is not supported")
    elif result == DISP_CHANGE_BADPARAM:
        print_error("An invalid parameter was passed in")
    elif result == DISP_CHANGE_FAILED:
        print_error("The display driver failed the specified graphics mode")
    elif result == DISP_CHANGE_NOTUPDATED:
        print_error("Unable to write settings to the registry")
    elif result == DISP_CHANGE_BADDUALVIEW:
        print_error("The settings change was unsuccessful because the system is DualView capable")
    else:
        print_error("An unknown error occurred")


def argument_parser() -> ArgumentParser:
    p = ArgumentParser(
        prog=NAME,
        description='Command line tool to change Windows display settings',
        usage=f'{NAME} --version | --devices | --device <identifier> | --width <width> --height <height> --refresh '
              f'<refresh>'
    )

    version_group = p.add_argument_group()
    version_group.add_argument('--version', action='version', version=VERSION)

    devices_group = p.add_mutually_exclusive_group()
    devices_group.add_argument('--devices', action='store_true', help='List all active display devices')
    devices_group.add_argument('--device', type=str, help='List all available modes for a device')

    mode_change_group = p.add_argument_group()
    mode_change_group.add_argument('--width', type=int, help='The width of the new display mode')
    mode_change_group.add_argument('--height', type=int, help='The height of the new display mode')
    mode_change_group.add_argument('--refresh', type=int, help='The refresh rate of the new display mode')

    return p


def print_message(message: str, color: str = None, attrs: list[str] = None, end: str = None):
    colored_message = colored(message, color, attrs=attrs)
    cprint(colored_message, color, attrs=attrs, end=end)


def print_success(message: str):
    colored_message = colored(message, TERM_COLOR_SUCCESS)
    cprint(colored_message)


def print_error(error: str):
    print_message("Error: " + error, 'red', attrs=['bold'])


if __name__ == '__main__':
    parser = argument_parser()
    args = parser.parse_args()

    display_devices: list[DisplayDevice] = get_all_display_devices()

    if len(display_devices) is None:
        print_error("No display devices found")
        exit(-1)

    if args.width or args.height or args.refresh:
        if args.width is None:
            print_error("Width is required")
            exit(-1)

        if args.height is None:
            print_error("Height is required")
            exit(-1)

        if args.refresh is None:
            print_error("Refresh rate is required")
            exit(-1)

        new_mode: DisplayMode = DisplayMode(args.width, args.height, args.refresh)
        new_mode_as_devmodew_type: DEVMODEWType = new_mode.as_devmodew_type()

        if args.device is not None:
            new_mode_as_devmodew_type.DeviceName = args.device

            print_message(f'Attempting to change {args.device} settings to: {str(new_mode)}')
        else:
            print_message(f'Attempting to change primary display settings to: {str(new_mode)}')

        device_mode_change_result: int = set_device_mode(args.device, new_mode_as_devmodew_type)
        print_human_readable_mode_change_result(device_mode_change_result)

        if device_mode_change_result != DISP_CHANGE_SUCCESSFUL:
            exit(device_mode_change_result)
    elif args.device is not None:
        identifier: str = args.device
        target_device: DisplayDevice | None = next(
            (device for device in display_devices if device.identifier == identifier), None
        )

        if target_device is None:
            print_error(f'Device {identifier} not found')
            exit(-1)

        print_device_info(target_device, detailed=True)
    else:
        print_message(f'Display devices found: {len(display_devices)}')

        for display_device in display_devices:
            print_device_info(display_device)
