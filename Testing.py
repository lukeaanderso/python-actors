__author__ = 'landerson'

import socket as socket
import uuid as uuid
from multiprocessing import Process, Pipe
import time as time


class Actor:
    def __init__(self, uid=None, func=None, conn=None):
        """
        Actors do work

        @param uid: Unique ID of Actor/Actor Ref Pair
        @param func: Function to do
        """
        self._uid = uid
        self._func = func
        self._conn = conn

    def act(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def listen(self):
        while 1:
            self._log('Listening')
            args, kwargs = self._conn.recv()
            self._log('Recieved')
            res = self.act(*args, **kwargs)
            self._log('Sending response back')
            self._conn.send(res)

    def _log(self, msg=None):
        print('{id} Actor ::: {msg}'.format(id=self._uid, msg=msg))


class ActorRef:
    def __init__(self, uid=None, conn=None, timeout=1):
        """
        Reference to an actor

        @param uid Unique ID of Actor/Actor Ref Pair
        @param conn Connection to the actor
        """
        self._uid = uid
        self._conn = conn
        self._timeout = timeout

    def ask(self, *args, **kwargs):
        self._log('Sending args to actor: {} {}'.format(args, kwargs))
        self._conn.send((args, kwargs))
        self._log('Waiting for response')
        if self._conn.poll(self._timeout):
            res = self._conn.recv()
            self._log('Response recieved')
        else:
            res = None
        return res

    def _log(self, msg=None):
        print('{id} Actor Ref ::: {msg}'.format(id=self._uid, msg=msg))


class ActorService:
    """ Service to start actors """

    def __init__(self, host=None, port=None):
        self._host = host or socket.gethostname()
        self._port = port or 13338
        self._uid = gen_key()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self._socket.bind((self._host,
        #                   self._port))
        temp = 'Starting Actor Service at {host}:{port}'.format(host=self._host,
                                                                port=self._port)
        print(temp)
        #self._socket.listen(1)
        self._actors = {}
        self._actor_refs = {}

    def actor_of(self, func=None):
        key = gen_key()
        actor_conn, ref_conn = Pipe()
        actor = Actor(uid=key, func=func, conn=ref_conn)
        actor_ref = ActorRef(uid=key, conn=actor_conn)
        self._log('Adding actor: {}'.format(key))
        self._add_actor(key, actor)
        self._start_actor(key)
        self._add_actor_ref(key, actor_ref)
        return actor_ref

    def _add_actor(self, uid=None, actor=None):
        p = Process(target=_actor_spinup, args=(actor,))
        self._actors[uid] = p

    def _start_actor(self, uid=None):
        self._actors[uid].start()

    def _stop_actor(self, uid=None):
        self._actors[uid].terminate()

    def list_actors(self):
        for k in self._actors.iterkeys():
            self._log('Has actor {}'.format(k))

    def _add_actor_ref(self, uid=None, actor_ref=None):
        self._actor_refs[uid] = actor_ref

    def get_message(self):
        conn, addr = self._socket.accept()
        return conn.recv(1024)

    def shutdown(self):
        for k in self._actors.iterkeys():
            self._stop_actor(k)

    def _log(self, msg=None):
        print('{id} Service ::: {msg}'.format(id=self._uid, msg=msg))


def add(a=None, b=None):
    return a + b


def mult(a=None, b=None):
    return a * b


def subtract(a, b):
    return a - b


def gen_key():
    return str(uuid.uuid4())


def _actor_spinup(actor=None):
    actor.listen()


host = 'friskies'
port = 13342
actorService = ActorService(host=host, port=port)
adder = actorService.actor_of(add)
multer = actorService.actor_of(mult)
subber = actorService.actor_of(subtract)
actorService.list_actors()
time.sleep(1)
res = adder.ask(a=3, b=4)
print('Adder res is {}'.format(res))
time.sleep(2)
res2 = multer.ask(a=3.2, b=1.2)
print('Mult res is {}'.format(res2))
res3 = multer.ask(a=4.2, b=1.2)
print('Mult res is {}'.format(res3))
print(subber.ask(3, 2))
actorService.shutdown()
