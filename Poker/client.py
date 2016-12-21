import sys
import zmq

class Server:

    def __init__(self, usr):
        self.usr = usr

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

if __name__ == "__main__":
    usr = ''
    tbl = ''

    if len(sys.argv) > 1:
        usr = sys.argv[1]
    
    srv = Server(usr)

    if len(sys.argv) > 2:
        tbl = sys.argv[2]
    