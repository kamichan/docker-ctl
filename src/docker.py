# -*- coding: utf-8 -*-

import sys
import subprocess

class Docker:

    def __init__(self):
        self.container = None

    def enter_container(self, id):
        output, status = self.execute('inspect -f "{{.Name}}" ' + id)
        if status != 0:
            print("Invalid container")
        else:
            self.container = Container(id, output[0], self)

    def exit_container(self):
        self.container = None

    def in_container(self):
        return self.container != None

    # Execute directive and get output
    def execute(self, directive):
        output = []
        # Exec directive
        pro = subprocess.Popen('docker ' + directive, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        try:
            while pro.poll() is None:
                line = pro.stdout.readline().strip()
                if line != '':
                    output.append(line)
        except KeyboardInterrupt:
            print("\n")

        return (output, pro.returncode)

    # Execute command
    def call(self, cmd, args):

        if self.in_container():
            self.container.call(cmd, args)
        else:
            command = 'docker %s %s' % (cmd, args)

            # Exec directive
            self.directive(command)

    # Execute directive
    def directive(self, command):
        pro = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stdout, shell=True)
        try:
            pro.wait()
        except KeyboardInterrupt:
            print("\n")

class Container:

    def __init__(self, id, name, docker):
        self.id         = id
        self.name       = name
        self.docker     = docker
        # alias list
        self.aliases    = {
            'll'    : 'ls -alF --color=auto',
        }
        self.commands   = {
            'alias' : self.alias_command,
            # not supported
            'cd'    : self.not_supported_command,
        }

    # Execute docker directive
    def call(self, cmd, args):

        if self.commands.has_key(cmd):
            handler = self.commands[cmd]
            handler(args)
        else:
            command = 'docker exec --user=root -it %s %s %s ' % (self.id, self.alias(cmd), args)

            # Exec directive
            self.docker.directive(command)

    def alias(self, alias):
        if self.aliases.has_key(alias):
            return self.aliases[alias]
        else:
            return alias

    def alias_command(self, args):
        for alias in self.aliases.keys():
            print('alias %s=\'%s\'' % (alias, self.aliases[alias]))

    def not_supported_command(self, args):
        print('docker-ctl: command not supported')