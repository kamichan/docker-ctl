# -*- coding: utf-8 -*-

class Command:

    def __init__(self, handler, args):
        # handler
        self.handler = handler
        # args
        if type(args) == list or callable(args):
            self.args = args
        else:
            self.args = []
    
    # Call handler
    def handle(self, args):
        if callable(self.handler):
            self.handler(args)

    # Return argument list
    def list_args(self):
        if callable(self.args):
            return self.args()
        return self.args