# -*- coding: utf-8 -*-

import sys
import subprocess

class Process:

    def __init__(self, path, args = ''):
        self.path   = path
        self.args   = args
        self.object = None
    
    # Execute binary
    def execute(self, interactive = False):
        if interactive:
            self.object = subprocess.Popen('%s %s' % (self.path, self.args), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stdout, shell=True)
            try:
                self.object.wait()
            except Exception: # KeyboardInterrupt or others
                pass

            return self.object.returncode == 0
        else:
            output = []
            # Exec directive
            self.object = subprocess.Popen('%s %s' % (self.path, self.args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            try:
                while self.object.poll() is None:
                    line = self.object.stdout.readline().strip()
                    if line != '':
                        output.append(line)
            except Exception: # KeyboardInterrupt or others
                pass

            return (self.object.returncode, output)