# status-wrapper

A simple utility to add icons to services that don't have them.

## Motivation

The application that motivated this project was actually Plex. I run the server
under my user account so it can access my media library. However, there's no
visual indication that the server is running without running some sort of status
command.

## Examples

Monitor a systemd user service.

```bash
# Assuming there is a service file in ~/.local/share/systemd/user/example.service.
./status-wrapper.py --systemd --open='xdg-open https://localhost:1234' --icon=~/.local/share/icons/48x48/apps/example.png example
```

Monitor a sysv-style user service.

```bash
./status-wrapper.py --sysv --open='xdg-open https://localhost:1234' --icon=~/.local/share/icons/48x48/apps/example.png ~/.config/init.d/example
```

## Actions

Your SysV script needs to implement `[start, stop, status, restart]`.
