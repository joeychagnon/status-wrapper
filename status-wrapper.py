#! /usr/bin/env python2

"""Status-Wrapper

Usage:
    status-wrapper
        [-i <path> | --icon=<path>]
        [-v | --sysv ]
        [-d | --systemd ]
        [-o <cmd> | --open=<cmd> ]
        <cmd>
    status-wrapper (-h | --help)
    status-wrapper --version

Options:
    -h --help                 Show this screen.
    --version                 Show version.
    -i <path> --icon=<path>   The icon to display.
    -o <cmd> --open=<cmd>     Command to bring the application to the foreground.
    -d --systemd              The command is a systemd user service.
    -v --sysv                 The command is a SysVinit style script.

"""

import docopt
import gtk
import gobject
import os
import subprocess
import signal

def find_file(name, search_path, pathsep=os.pathsep):
    for path in string.split(search_path, pathsep):
        candidate = os.path.join(path, name)
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
    return None

def make_popup(h):
    def on_popup(data, event_button, event_time):
        menu = gtk.Menu()

        open_item = gtk.MenuItem('Open')
        restart_item = gtk.MenuItem('Restart')
        quit_item = gtk.MenuItem('Quit')

        menu.append(open_item)
        menu.append(restart_item)
        menu.append(quit_item)

        open_item.connect_object('activate', lambda event: h.open(), 'Open')
        restart_item.connect_object('activate', lambda event: h.restart(), 'Restart')
        quit_item.connect_object('activate', make_quit(h), 'Quit')

        open_item.show()
        restart_item.show()
        quit_item.show()

        menu.popup(None, None, None, event_button, event_time)

    return on_popup

def make_quit(h):
    def do(event):
        h.stop()
        gtk.main_quit()
    return do

def make_monitor(h):
    def do():
        if not h.status():
            gtk.main_quit()
    return do

class ServiceWrapper(object):
    SEPARATOR = ' '

    def __init__(self, service, open_cmd=None):
        self.service = service
        self.open_cmd = open_cmd

    def _run(self, cmd):
        return subprocess.check_output(cmd.split(ServiceWrapper.SEPARATOR))

    def open(self):
        if self.open_cmd:
            self._run(self.open_cmd)

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

    def status(self):
        pass

class SystemdServiceWrapper(ServiceWrapper):
    def __init__(self, service, open_cmd=None):
        super(SystemdServiceWrapper, self).__init__(service, open_cmd)

    def _act(self, action):
        return self._run('systemctl --user %s %s.service' % (action, self.service))

    start = lambda self: self._act('start')
    stop = lambda self: self._act('stop')
    restart = lambda self: self._act('restart')
    status = lambda self: self._act('--no-pager status')

class SysVServiceWrapper(ServiceWrapper):
    PATH='.:%s/.config/init.d'

    def __init__(self, service, open_cmd=None):
        super(SysVServiceWrapper, self).__init__(service, open_cmd)
        self.scr = self.find_file()

    def find_file(self, pathsep=os.pathsep):
        for path in SysVServiceWrapper.PATH.split(pathsep):
            candidate = os.path.join(path, self.service)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
        return None

    def _act(self, action):
        self._run('"%s" %s' % (self.scr, action))

    start = lambda self: self._act('start')
    stop = lambda self: self._act('stop')
    restart = lambda self: self._act('restart')
    status = lambda self: self._act('status')

def main():
    global config
    config = {}

    args = docopt.docopt(__doc__, version='status-wrapper 0.1')
    open_cmd = args['--open']

    if args['--sysv']:
        service = find_file(args['<cmd>'], '.:%s/.config/init.d' % os.environ('HOME'))
        h = SysVServiceWrapper(service, open_cmd)
    else:
        h = SystemdServiceWrapper(args['<cmd>'], open_cmd)

    if args['--icon']:
        tray = gtk.status_icon_new_from_file(args['--icon'])
    else:
        tray = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)

    h.start()

    tray.connect('activate', lambda event: h.open())
    tray.connect('popup-menu', make_popup(h))
    gobject.timeout_add(10000, make_monitor(h))
    gtk.main()

if __name__ == '__main__':
    main()
