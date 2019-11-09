import os, sys
import _thread
from socket import *
import argparse

class ChatServer():
    connection_pool = []
    _render_msg = "init"

    def __init__(self, parent, args):
        self.main(parent, args)

    def main(self, parent, args):
        for i in range(args.backlog):
            self.connection_pool.append(None)

        try:
            serverSock = socket(AF_INET, SOCK_STREAM) # TCP
            serverSock.bind(('', args.port)) # localhost
            serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            serverSock.listen(args.backlog)
        except OSError as e:
            if serverSock:
                serverSock.close()
            print(e)
            sys.exit(1)

        print('..listening..')

        while 1:
            connectionSock, client_addr = serverSock.accept()
            if(connectionSock):
                print("accepted")
                _thread.start_new_thread(self.connection_thread, (parent, connectionSock, client_addr, args))

        serverSock.close()

    def connection_thread(self, parent, _connectionSock, _client_addr, args):
        user = None
        username = ""
        while 1:
            request = _connectionSock.recv(args.max_data_recv).decode('utf-8')
            print(request)
            if(request == 'exit'):
                _connectionSock.send(('[exit]').encode('utf-8'))
                _connectionSock.close()
                print('connection closed')
                break
            if(request == ''):
                _connectionSock.send(('[exit]').encode('utf-8'))
                _connectionSock.close()
                print('connection closed')
                break
            if(request.split(':')[0] == 'user_id'): # first meet
                if self.connection_pool[int(request.split(':')[1])] == None:
                    user = int(request.split(':')[1])
                    username = request.split(':')[2]
                    self.connection_pool[user] = _connectionSock
                    _connectionSock.send(("user[" + username + "] is connected").encode('utf-8'))
                    # _connectionSock.send(('connected user ' + request.split(':')[1]).encode('utf-8'))
                else:
                    _connectionSock.send('[error] invalid access detected'.encode('utf-8'))
                    _connectionSock.close()
                    self.connection_pool[int(request.split(':')[1])] = None
                    print('connection closed')
                    break
            else:
                if(self.connection_pool[int(request.split('#', 1)[0])] == None):
                    _connectionSock.send(('[error] user' + (request.split('#', 1)[0]) + ' not connected').encode('utf-8'))
                    _connectionSock.close()
                    self.connection_pool[user] = None
                    print('connection closed')
                    break
                else:
                    self.connection_pool[int(request.split('#', 1)[0])].send(("\n[user" + str(user) + "]: " + request.split('#')[1]).encode('utf-8'))

    def render_msg(self):
        return self._render_msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    args = parser.parse_args()
    chatServer = ChatServer(None, args)
