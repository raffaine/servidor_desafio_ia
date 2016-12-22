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

    def get_turn(self):
        self.srv.send_string("GETTURN %s"%(self.table))
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

    def poll_sub(self, handler):
        while(self.pubsrv.poll(1)):
            _, _, data = (self.pubsrv.recv_string()).partition(' ')
            handler(data)

class Game:
    """ Keeps track of game information """
    def __init__(self, server):
        self.money = 0
        self.hand = []
        self.players = []
        self.round = 0
        self.turn = 0
        self.table = []
        self.blind = 0
        self.is_over = False
        self.handlers = {k[len('H_'):]:v for k, v in Game.__dict__.items() if k.startswith('H_')}
        self.server = server

    def handle_msg(self, content):
        print("Handling ", content)
        content = content.split(' ')
        cmd = self.handlers.get(content[0], lambda _: print("Invalid message"))
        cmd(self, *content[1:])

    def H_START(self, start_money, blind_val, *players):
        self.money = int(start_money)
        self.blind = int(blind_val)
        self.players = list(players)

    def H_GETHANDS(self):
        self.hand = json.loads(self.server.get_hand())

    def H_BLIND(self, player, value):
        if player == self.server.usr:
            self.money -= int(value)

    def H_GAMEOVER(self):
        self.is_over = True



if __name__ == "__main__":
    usr = ''

    if len(sys.argv) > 1:
        usr = sys.argv[1]

    srv = Server(usr)
    srv.hunt_table()

    game = Game(srv)
    while not game.is_over:
        srv.poll_sub(game.handle_msg)
