# -*- coding: utf-8 -*-

import sys
import subprocess
from process import Process

class Docker:

    def __init__(self):
        self.container = None
        self.commands   = {
            'attach'    : None,
            'build'     : None,
            'commit'    : None,
            'cp'        : None,
            'create'    : None,
            'diff'      : None,
            'events'    : None,
            'export'    : None,
            'history'   : None,
            'images'    : None,
            'import'    : None,
            'info'      : None,
            'inspect'   : None,
            'kill'      : None,
            'load'      : None,
            'login'     : None,
            'logout'    : None,
            'logs'      : None,
            'pause'     : None,
            'port'      : None,
            'ps'        : None,
            'pull'      : None,
            'push'      : None,
            'rename'    : None,
            'restart'   : None,
            'rm'        : None,
            'rmi'       : None,
            'run'       : None,
            'save'      : None,
            'search'    : None,
            'start'     : None,
            'stats'     : None,
            'stop'      : None,
            'tag'       : None,
            'top'       : None,
            'unpause'   : None,
            'version'   : None,
            'wait'      : None,
        }

    # Enter a container
    def enter_container(self, id):
        status, output = self.execute('inspect -f "{{.Name}}" %s' % id)
        if status != 0:
            print('Invalid container')            
        else:
            self.container = Container(id, output[0], self)
            if not self.container.is_running():
                self.container = None
                print('This container is stopping')

    # Exit current container
    def exit_container(self):
        self.container = None

    # Check if it's in a container
    def in_container(self):
        return self.container != None

    # Execute directive and get output
    def execute(self, directive):
        # Exec directive
        return Process('docker', directive).execute()

    # Execute command
    def call(self, cmd, args):
        if self.in_container():
            self.container.call(cmd, args)
        else:
            Process('docker', '%s %s' % (cmd, args)).execute(True)

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
        }
        # not supported
        self.forbidden = ['cd']

    def is_running(self):
        status, output = self.docker.execute('inspect -f "{{.State.Running}}" %s' % self.id)
        if status == 0:
            return output[0] == 'true'
        else:
            return False

    # Execute docker directive
    def call(self, cmd, args):
        if cmd in self.forbidden: # forbidden
            self.not_supported_command(args)
        elif self.commands.has_key(cmd): # docker-ctl's commands
            handler = self.commands[cmd]
            handler(args)
        else: # container's commands
            Process('docker', 'exec --user=root -it %s %s %s' % (self.id, self.alias(cmd), args)).execute(True)

    def alias(self, alias):
        if self.aliases.has_key(alias):
            return self.aliases[alias]
        else:
            return alias

    # Command: alias
    def alias_command(self, args):
        for alias in self.aliases.keys():
            print('alias %s=\'%s\'' % (alias, self.aliases[alias]))

    # When a command is not supported
    def not_supported_command(self, args):
        print('docker-ctl: command not supported')