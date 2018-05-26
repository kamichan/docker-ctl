# -*- coding: utf-8 -*-

from console import Console

if __name__ == '__main__':
    print("--- docker-ctl starting ---")
    # Daemon
    Console().start_daemon()

    print("bye!")