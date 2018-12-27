#!/usr/bin/env python

# encoding: utf-8

# @author: Durand Wang

# @file: DarkRiverServer.py

# @time: 2018/12/7 12:00

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

HOST = '127.0.0.1'
PORT = 5003
BUFSIZE = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)


class DarkRiverServer:          # The server class
    def __init__(self):
        self.clients = {}       #
        self.addresses = {}     # store the connection information as {client: addr}

    def accept_connect_request(self):
        """Add new client to the river."""
        while True:
            client, client_addr = SOCK.accept()
            print('{}: {} has connected.'.format(client, client_addr))
            client.send('Welcome to the Dark River!\nPlease type your name and join the chat now!'.encode('utf-8'))
            self.addresses[client] = client_addr
            Thread(target=self.handle_client, args=(client, client_addr)).start()

    def broadcast(self, msg, prefix=''):
        """Broadcasts the massage to all clients."""
        for sock in self.clients:
            sock.send(bytes(prefix, 'utf8') + msg)

    def sendCurrentMembers(self):
        """Send the current members to a new joined client"""
        if not self.clients:        # no current members
            return
        clients = []
        for i in self.clients:
            clients.append(self.clients[i])
        for sock in self.clients:
            sock.send(bytes('$%' + '\t'.join(clients), 'utf8'))

    def handle_client(self, conn, addr):
        """
        Handles one client connection.
        conn: the client socket

        """
        while True:             # no two identical names in chat room
            flag = False
            name = conn.recv(BUFSIZE).decode('utf-8')
            for i in self.clients:
                if self.clients[i] == name:
                    flag = True
                    break
            if flag:
                conn.send(bytes('Name has been used, pick another one!', 'utf8'))
            else:
                break
        conn.send(bytes('Welcome {}! Talk anything you like!'.format(name), "utf8"))
        msg = "{} from [{}:{}] has joined the Dark River!".format(name, addr[0], addr[1])
        self.broadcast(bytes(msg, 'utf8'))          # broadcast welcome message(not to the conn)
        self.clients[conn] = name  # add conn to self.clients
        self.sendCurrentMembers()               # send the current members(no conn yet) to conn
        while True:
            msg = conn.recv(BUFSIZE)
            if msg != bytes("#exit", 'utf8'):
                self.broadcast(msg, name + ': ')
            else:
                conn.send(bytes("#exit", "utf8"))
                conn.close()
                del self.clients[conn]
                self.broadcast(bytes('{} has left the Dark River.'.format(name), 'utf8'))
                self.sendCurrentMembers()
                break


if __name__ == "__main__":
    dr = DarkRiverServer()
    SOCK.listen(4)          # Listens for 4 connections at most
    print('The Dark River has started!')
    print('Waiting for clients to join in......')
    ACCEPT_THREAD = Thread(target=dr.accept_connect_request)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SOCK.close()
