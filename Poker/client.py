import sys
import zmq
import json
import uuid

class Server:

    def __init__(self, usr):
        self.usr = usr        
        self.table = ''

        ### ZMQ Initialization ###
        ctx = zmq.Context()

        self.pubsrv = ctx.socket(zmq.SUB)
        self.pubsrv.connect('tcp://127.0.0.1:5556')
        self.pubsrv.setsockopt_string(zmq.SUBSCRIBE, '')

        self.srv = ctx.socket(zmq.REQ)
        self.srv.connect("tcp://127.0.0.1:5555")

    def list_table(self):
        self.srv.send_string("LIST")
        return self.srv.recv_string()

    def create_table(self, name):
        self.srv.send_string("TABLE %s"%(name))
        return self.srv.recv_string()

    def join_table(self, name):
        self.srv.send_string("JOIN %s %s"%(self.usr, name))
        return self.srv.recv_string()

    def get_hand(self):
        self.srv.send_string("GETHAND %s"%(self.usr))
        return self.srv.recv_string()

    def get_turn(self, table):
        self.srv.send_string("GETTURN %s"%(table))
        return self.srv.recv_string()

    def resubscribe(self, table):
        self.pubsrv.setsockopt_string(zmq.UNSUBSCRIBE, '')
        self.pubsrv.setsockopt_string(zmq.SUBSCRIBE, table)

    def hunt_table(self):
        while not self.table:
            msg = self.list_table()
            if msg.startswith('ERROR'):
                msg = '[]'

            tables = json.loads(msg)

            while tables:
                tmp = tables.pop()
                self.resubscribe(tmp)

                msg = self.join_table(tmp)
                if not msg.startswith('ERROR'):
                    self.table = tmp
                    return True

            msg = self.create_table(str(uuid.uuid4()))
            if msg.startswith('ERROR'):
                self.resubscribe('')
                return False


if __name__ == "__main__":
    usr = ''

    if len(sys.argv) > 1:
        usr = sys.argv[1]

    srv = Server(usr)
    srv.hunt_table()
     