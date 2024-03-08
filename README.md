# ResolutionSwitcher

A command line tool to change the display resolution of computers running Windows.

## Usage Examples

List all available devices on the system

```shell
ResolutionSwitcher
```

Display all available resolutions for device with identifier `\\.\DISPLAY2`

```shell
ResolutionSwitcher --device \\.\DISPLAY2
```

Change the resolution of the primary display device

```shell
ResolutionSwitcher --width 1920 --height 1080 --refresh 60
```

Change the resolution of device with identifier `\\.\DISPLAY2`

```shell
ResolutionSwitcher --width 1920 --height 1080 --refresh 60 --device \\.\DISPLAY2
```

Display available help information

```shell
ResolutionSwitcher --help
```

## Sunshine "Do" and and "Undo" Commands

The tool is useful for scenarios where you need to programmatically change the resolution of a display, for example, 
during "do" and "undo" commands run as part of a [Moonlight](https://moonlight-stream.org/) session via [Sunshine](https://github.com/LizardByte/Sunshine).

These examples assume the application is installed at `C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe`.

### Do Command

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --width %SUNSHINE_CLIENT_WIDTH% --height %SUNSHINE_CLIENT_HEIGHT% --refresh %SUNSHINE_CLIENT_FPS%
```

### Undo Command

```shell
cmd /C "C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe" --width 3840 --height 2160 --refresh 144
```

## Building

The tool is written in [Python](https://www.python.org/) and uses [`pywin32`](https://pypi.org/project/pywin32/) to
interact with the Windows API.

For distribution, the Python script is compiled into an executable using [`pyinstaller`](https://www.pyinstaller.org/).