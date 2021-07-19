from enum import Enum


class Status(Enum):
    created = 0
    restarting = 1
    running = 2
    removing = 3
    paused = 4
    exited = 5
    dead = 6