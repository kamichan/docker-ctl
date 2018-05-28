# -*- coding: utf-8 -*-

import sys, os
import atexit
import readline
from docker   import Docker
from process  import Process
from command  import Command

class Console:

    def __init__(self):
        self.running   = True
        self.matches   = []
        self.docker    = Docker()
        self.commands  = {
            'history'   : Command(self.history_command,     ['--clear']),
            'clear'     : Command(self.clear_command,       []),
            'exit'      : Command(self.exit_command,        ['--all']),
        }
        self.history   = os.path.join(os.environ['HOME'], '.docker_ctl_history')

        #tab completion
        readline.parse_and_bind('tab: complete')
        # history
        self.init_history()
        # completer
        readline.set_completer(self.completer)
        readline.set_completer_delims(' \t\n;')
        # save history when exiting
        atexit.register(readline.write_history_file, self.history)


    # Initialize history
    def init_history(self):
        try:
            # read history from disk
            readline.read_history_file(self.history)
            # max history length
            readline.set_history_length(1000)
        except:
            pass

    # daemon
    def start_daemon(self):
        while self.running:
            try:
                directive = self.listen()
            except KeyboardInterrupt:
                print('') # print a '\n'
                break

            # It's empty
            directive = directive.strip()
            if directive == '':
                break

            # tab char replace to space
            directive = directive.replace('\t', ' ')

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
                self.commands[cmd].handle(args)
            else:
                self.docker.call(cmd, args)

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

    # Auto complete
    def completer(self, text, state):
        # handle matches
        if state == 0:
            commands    = []
            line_buffer = readline.get_line_buffer()

            cmd = ''
            if ' ' in line_buffer:
                cmd = line_buffer.split(' ')[0]

            if self.docker.in_container():
                if cmd != '' and self.docker.container.commands.has_key(cmd):
                    commands = self.docker.container.commands[cmd].list_args()
                else:
                    commands = self.docker.container.get_command_list()
            else:
                if cmd != '':
                    if self.commands.has_key(cmd):
                        commands = self.commands[cmd].list_args()
                    elif self.docker.commands.has_key(cmd):
                        commands = self.docker.commands[cmd].list_args()
                else:
                    commands = self.get_command_list()

            if text == '':
                self.matches = commands
            else:
                self.matches = self.matches_generator(text, commands)

        try:
            if len(self.matches) == 1 and self.matches[0] == text:
                readline.insert_text(' ')
                return None
            else:
                return self.matches[state]
        except IndexError:
            pass

        return None

    def matches_generator(self, prefix, commands):
        matches = []
        length  = len(prefix)
        for cmd in commands:
            if cmd.startswith(prefix, 0, length):
                matches.append(cmd)

        return matches

    def get_command_list(self):
        return self.commands.keys() + self.docker.get_command_list()

    # print_invalid operation
    def print_invalid_operation(self, cmd, args):
        print('Invalid operation: %s %s' % (cmd, args))

    # Command: history
    def history_command(self, args):
        if args == '':
            len = readline.get_current_history_length()
            for index in range(1, len + 1):
                print('%s' % readline.get_history_item(index))
        elif args == '--clear':
            readline.clear_history()
        else:
            self.print_invalid_operation('history', args)

    # Command: clear
    def clear_command(self, args):
        if args == '':
            Process('clear').execute(True)
        else:
            self.print_invalid_operation('clear', args)

    # Command: exit
    def exit_command(self, args):
        if args == '':
            if self.docker.in_container():
                self.docker.exit_container()
            else:
                self.stop_daemon()
        elif args == '--all':
            self.stop_daemon()
        else:
            self.print_invalid_operation('exit', args)