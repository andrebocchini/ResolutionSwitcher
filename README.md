# ResolutionSwitcher

A command line tool to change the display resolution and HDR state of computers running Windows.

# Usage

```
usage: ResolutionSwitcher --version | --monitors | --monitor <ID> | --width <width> --height <height> --refresh <refresh> | --hdr <true/false>

Command line tool to change Windows display settings

options:
  -h, --help          show this help message and exit
  --monitors          List all active monitors
  --monitor MONITOR   List all available modes for a monitor (e.g. \\.\DISPLAY1)

  --version           show program's version number and exit

  --width WIDTH       The width of the new display mode (e.g. 1920)
  --height HEIGHT     The height of the new display mode (e.g. 1080)
  --refresh REFRESH   The refresh rate of the new display mode (e.g. 144)
  --temp              Make resolution change temporary (do not persist to registry)

  --hdr <true|false>  Enable/Disable HDR on the monitor
```

# Examples

List all available devices on the system

```shell
ResolutionSwitcher
```

Display detailed information for device with identifier `\\.\DISPLAY2`

```shell
ResolutionSwitcher --monitor \\.\DISPLAY2
```

Change the resolution of the primary display device

```shell
ResolutionSwitcher --width 1920 --height 1080 --refresh 60
```

Change the resolution of device with identifier `\\.\DISPLAY2`

```shell
ResolutionSwitcher --width 1920 --height 1080 --refresh 60 --monitor \\.\DISPLAY2
```

Enable HDR on device with identifier `\\.\DISPLAY2`

```shell
ResolutionSwitcher --hdr true --monitor \\.\DISPLAY2
```

Disable HDR on the primary device

```shell
ResolutionSwitcher --hdr false
```

Display available help information

```shell
ResolutionSwitcher --help
```

# Sunshine "Do" and and "Undo" Commands

The tool is useful for scenarios where you need to programmatically change the resolution of a display, for example, 
during "do" and "undo" commands run as part of a [Moonlight](https://moonlight-stream.org/) session via [Sunshine](https://github.com/LizardByte/Sunshine).

These examples assume the application is installed at `C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe`.

## Do Commands

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --width %SUNSHINE_CLIENT_WIDTH% --height %SUNSHINE_CLIENT_HEIGHT% --refresh %SUNSHINE_CLIENT_FPS%
```

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --hdr %SUNSHINE_CLIENT_HDR%
```

## Undo Commands

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --width 3840 --height 2160 --refresh 144
```

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --hdr false
```

# Building

The tool is written in [Python](https://www.python.org/) and uses the [ctypes](https://docs.python.org/3/library/ctypes.html) library to interact with the Windows API.

For distribution, the Python script is compiled into an executable using [`pyinstaller`](https://www.pyinstaller.org/).
