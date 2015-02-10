__author__ = 'landerson'

__author__ = 'landerson'

import time
from actors import ActorService

def add(a=None, b=None):
    return a + b


def mult(a=None, b=None):
    return a * b


def subtract(a, b):
    return a - b


host = 'friskies'
port = 13342
actorService = ActorService(host=host, port=port)