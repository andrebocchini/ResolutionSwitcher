from argparse import ArgumentParser

# Functions for getting display devices and settings
from win32api import EnumDisplayDevices
from win32api import EnumDisplaySettings
from win32api import ChangeDisplaySettings

# Display device state flags
from win32con import ENUM_CURRENT_SETTINGS
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

VERSION: str = "v1.0.0"
NAME: str = "ResolutionSwitcher"

class DisplayDevice:
    def __init__(self, name: str, string: str, state_flags: int):
        self.name = name
        self.string = string
        self.state_flags = state_flags

    def __str__(self):
        return self.name


class DisplayMode:
    def __init__(self, width: int, height: int, refresh: int):
        self.width = width
        self.height = height
        self.refresh = refresh

    def __str__(self):
        return str(self.width) + "x" + str(self.height) + " @ " + str(self.refresh) + "Hz"

    def as_devmodew_type(self) -> DEVMODEWType:
        devmode = DEVMODEWType()
        devmode.PelsWidth = self.width
        devmode.PelsHeight = self.height
        devmode.DisplayFrequency = self.refresh
        devmode.Fields = DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQUENCY
        return devmode


def get_all_display_devices() -> list[DisplayDevice]:
    devices: list[DisplayDevice] = []

    index_of_current_device: int = 0
    finished_searching_for_devices: bool = False

    while not finished_searching_for_devices:
        try:
            display_adapter = EnumDisplayDevices(None, index_of_current_device, 0)
            devices.append(
                DisplayDevice(display_adapter.DeviceName, display_adapter.DeviceString, display_adapter.StateFlags)
            )
        except:
            finished_searching_for_devices = True
        finally:
            index_of_current_device += 1

    return devices


def get_active_display_mode_for_device(device: DisplayDevice) -> DisplayMode | None:
    try:
        display_mode = EnumDisplaySettings(device.name, ENUM_CURRENT_SETTINGS)

        return DisplayMode(
            display_mode.PelsWidth, display_mode.PelsHeight, display_mode.DisplayFrequency
        )
    except:
        return None


def get_all_available_modes_for_device(device: DisplayDevice) -> list[DisplayMode]:
    modes: list[DisplayMode] = []

    # Tell Windows to cache display mode information
    EnumDisplaySettings(device.name, 0)

    index_of_current_mode: int = 1
    finished_getting_modes: bool = False

    while not finished_getting_modes:
        try:
            display_mode: DEVMODEWType = EnumDisplaySettings(device.name, index_of_current_mode)
            modes.append(
                DisplayMode(display_mode.PelsWidth, display_mode.PelsHeight, display_mode.DisplayFrequency)
            )
            index_of_current_mode += 1
        except:
            finished_getting_modes = True

    return modes


def print_device_info(device: DisplayDevice, display_mode: DisplayMode):
    # Device details
    print("\n[" + device.string + "]\n")
    print("Width: " + str(display_mode.width))
    print("Height: " + str(display_mode.height))
    print("Refresh: " + str(display_mode.refresh) + "Hz")


def print_all_available_modes_for_device(device: DisplayDevice):
    all_available_display_modes = get_all_available_modes_for_device(device)

    print("\n[Available Modes]\n")
    for display_mode in all_available_display_modes:
        print(str(display_mode))


def set_device_mode(device_mode: DisplayMode) -> int:
    if device_mode is None:
        raise ValueError("Settings cannot be None")

    return ChangeDisplaySettings(device_mode.as_devmodew_type(), 0)


def print_human_readable_mode_change_result(result: int):
    if result == DISP_CHANGE_SUCCESSFUL:
        print("Display settings changed successfully")
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
        usage=f'{NAME} --width <width> | --height <height> | --refresh <refresh>'
    )

    version_group = p.add_mutually_exclusive_group()
    version_group.add_argument('--version', action='version', version=VERSION)

    mode_change_group = p.add_mutually_exclusive_group()
    mode_change_group.add_argument('--width', type=int)
    mode_change_group.add_argument('--height', type=int)
    mode_change_group.add_argument('--refresh', type=int)

    return p


def print_error(error: str):
    print("Error: " + error)


if __name__ == '__main__':
    parser = argument_parser()
    args = parser.parse_args()

    display_devices: list[DisplayDevice] = get_all_display_devices()

    primary_display_device: DisplayDevice = display_devices[0] if not len(display_devices) == 0 else None

    if primary_display_device is None:
        print_error("No display devices found")
        exit(-1)

    primary_display_device_mode: DisplayMode = get_active_display_mode_for_device(primary_display_device)

    if primary_display_device_mode is None:
        print_error("Unable to get display settings for primary display device")
        exit(-1)

    # If the user doesn't provide any arguments, list the current display settings for all active devices

    if not args.width and not args.height and not args.refresh:
        for display_device in display_devices:
            active_display_mode_for_device = get_active_display_mode_for_device(display_device)

            if active_display_mode_for_device is not None:
                print_device_info(display_device, active_display_mode_for_device)
                print_all_available_modes_for_device(display_device)
    else:
        # We use the arguments that the user provided. For any argument they did not
        # provide, we use the values in the current display settings
        new_width: int = args.width if args.width else primary_display_device_mode.width
        new_height: int = args.height if args.height else primary_display_device_mode.height
        new_refresh: int = args.refresh if args.refresh else primary_display_device_mode.refresh
        new_mode: DisplayMode = DisplayMode(new_width, new_height, new_refresh)

        print("Attempting to change display settings to: " + str(new_mode))

        device_mode_change_result: int = set_device_mode(new_mode)
        print_human_readable_mode_change_result(device_mode_change_result)

        if device_mode_change_result != DISP_CHANGE_SUCCESSFUL:
            exit(device_mode_change_result)
