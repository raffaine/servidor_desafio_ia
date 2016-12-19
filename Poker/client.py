import sys
import zmq

class Server:

    def __init__(self, usr):
        self.usr = usr

        ### ZMQ Initialization ###
        self.ctx = zmq.Context()

        self.pubsrv = ctx.socket(zmq.SUB)
        self.pubsrv.connect('tcp://127.0.0.1:5556')
        self.pubsrv.setsockopt_string(zmq.SUBSCRIBE,'')

        self.srv = ctx.socket(zmq.REQ)
        self.srv.bind("tcp://127.0.0.1:5555")
    
    def list_table(self):
        pass

    def create_table(self):
        pass

    def join_table(self, name):
        self.srv.send_string("SUBSCRIBE %s"%(self.usr))
        self.srv.recv_string()

if __name__ == "__main__":
    usr = ''
    tbl = ''

    if len(sys.argv) > 1:
        usr = sys.argv[1]
    
    srv = Server(usr)

    if len(sys.argv) > 2:
        tbl = sys.argv[2]
    