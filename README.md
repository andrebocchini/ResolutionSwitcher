# ResolutionSwitcher

A command line tool to change the display resolution of computers running Windows.

## Usage

```shell
ResolutionSwitcher.exe --width 1920 --height 1080 --refresh 60
```

You can provide the `width`, `height`, and `refresh` parameters at the same time, or provide them individually. 
If you provide them individually, the tool will use the values for the currently active display settings to make sure it has
all 3 to provide to Windows when it attempts to change the resolution.

For example:

```shell
ResolutionSwitcher.exe --width 1920

ResolutionSwitcher.exe --height 1080

ResolutionSwitcher.exe --refresh 60
```

If you run the tool without providing any parameters, it will print the current display settings, as
well as full dump of all available display settings for all displays on the system.

## Example Usage: Sunshine "Do" and and "Undo" Commands

The tool is useful for scenarios where you need to programmatically change the resolution of a display, for example, 
during "do" and "undo" commands run as part of a [Moonlight](https://moonlight-stream.org/) session via [Sunshine](https://github.com/LizardByte/Sunshine).

This assumes the application is installed at `C:\Program Files\ResolutionSwitcher\ResolutionSwitcher.exe`.

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