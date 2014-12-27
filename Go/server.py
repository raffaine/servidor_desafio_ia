#!/usr/bin/env python3
import zmq

port = 5555

EMPTY = ' '
BLACK = 'B'
WHITE = 'W'

BOARD_SIZE = 9

class GoTable:
    def __init__(self):
        self._board = [' ' for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)]
        self._score = dict([(BLACK,0),(WHITE,0)])
        self.game_over = False
        self.winner = EMPTY

    def _set(self, row, col, val):
        self._board[row*BOARD_SIZE+col] = val

    def _get(self, row, col):
        return self._board[row*BOARD_SIZE+col]

    def _is_bound(self, row, col):
        return (row < BOARD_SIZE and col < BOARD_SIZE and row >= 0 and col >= 0)

    def move(self, player, row, col):
        if (not self._is_bound(row,col) or self._get(row,col) != EMPTY):
            return False

        self._set(row, col, player)
        return True
        #TODO Suponho que aqui venha a aplicacao de algumas regras do jogo, como peca come outra e tal
        #TODO Calcular também os pontos de cada jogador
        
    def print_board(self):
        return '\n'.join([''.join(self._board[i*BOARD_SIZE:(i+1)*BOARD_SIZE]) for i in range(BOARD_SIZE)]) 

def strip_message(msg):
    """
    A mensagem deve ser do formato "PLAYER LINHA COLUNA"
    onde PLAYER in {'B','W'} e LINHA/COLUNA in range(BOARD_SIZE)
    """
    arr = msg.split(' ')
    if len(arr) < 3:
        return (False,"Invalid Message")

    who = arr[0]
    if who != WHITE and who != BLACK:
        return (False,"Invalid Player")

    try:
        row = int(arr[1])
        col = int(arr[2])

    except ValueError:
        return (False,"Invalid position")

    return (True,(who,row,col))



#COMEÇA A BRINCADEIRA!

ctx = zmq.Context()

action_server = ctx.socket(zmq.REP)
action_server.bind("tcp://*:%d"%port)

status_publisher = ctx.socket(zmq.PUB)
status_publisher.bind("tcp://*:%d"%(port+1))

table = GoTable()

active_player = WHITE

while True:
    msg = action_server.recv_string();
    (valid, result) = strip_message(msg)
    if valid:
        (who, row, col) = result
        if table.move(who, row, col):
            action_server.send_string("ACK")
            if table.game_over:
                if table.winner == EMPTY:
                    status_publisher.send_string("GAMEOVER DRAW")
                else:
                    status_publisher.send_string("GAMEOVER %s WINS"%table.winner)
                break

            active_player = BLACK if (active_player == WHITE) else WHITE
            #TODO Publicar mais info, tipo o placar?
            status_publisher.send_string("TURN %s TABLE #%s"%(active_player, table.print_board()))
            continue
        else:
            result = "Invalid Move"
        
    action_server.send_string("ERROR %s"%result)
