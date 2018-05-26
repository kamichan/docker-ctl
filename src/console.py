# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from docker   import Docker

class Console:

    def __init__(self):
        self.running   = True
        self.history   = []
        self.docker    = Docker()
        self.commands  = {
            'select'    : self.select_command,
            'history'   : self.history_command,
            'exit'      : self.exit_command,
        }

    # daemon
    def start_daemon(self):
        while self.running:
            try:
                directive = self.listen()
            except KeyboardInterrupt:
                print("\n")
                break

            # It's empty
            directive = directive.strip()
            if directive == '':
                break

            # tab char replace to space
            directive = directive.replace("\t", ' ')

            cmd  = ''
            args = ''
            # Get command
            index = directive.find(' ', 0)
            if index == -1:
                cmd  = directive
            else:
                cmd  = directive[0:index]
                args = directive[index:].strip()

            # exit
            if self.commands.has_key(cmd):
                handler = self.commands[cmd]
                handler(args)
            else:
                self.docker.call(cmd, args)

            # Add it to history
            self.history.append({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'cmd': cmd})

    # Stop the daemon
    def stop_daemon(self):
        self.running = False

    # Listen the input
    def listen(self):
        if self.docker.in_container():
            prompt = "docker(%s\033[0;33m@@%s\033[0m)# " % (self.docker.container.name, self.docker.container.id)
        else:
            prompt = 'docker> '

        return raw_input(prompt)

    def select_command(self, args):
        if args != '':
            self.docker.enter_container(args)
        else:
            print('Invalid container')

    def history_command(self, args):
        for log in self.history:
            print("%s \033[0;31m%s\033[0m" % (log['time'], log['cmd']))

    def exit_command(self, args):
        if args == '':
            if self.docker.in_container():
                self.docker.exit_container()
            else:
                self.stop_daemon()
        elif args == 'all':
            self.stop_daemon()