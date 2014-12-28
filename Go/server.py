#!/usr/bin/env python3
import zmq
from board import *

port = 5555

ctx = zmq.Context()

action_server = ctx.socket(zmq.REP)
action_server.bind("tcp://*:%d"%port)

status_publisher = ctx.socket(zmq.PUB)
status_publisher.bind("tcp://*:%d"%(port+1))

table = GoTable()

while True:
    msg = action_server.recv_string();
    print(msg)
    (valid, result) = strip_message(msg)
    if valid:
        (who, row, col) = result
        if table.move(who, row, col):
            action_server.send_string("ACK")
            if table.game_over:
                msg = "GAMEOVER DRAW" if table.winner == GoTable.EMPTY \
                                      else "GAMEOVER %s WINS"%table.winner
                status_publisher.send_string(msg)
                break

            #TODO Publicar mais info, tipo o placar?
            status_publisher.send_string("TURN %s TABLE #%s"%table.get_state())
            continue
        else:
            result = "Invalid Move"
        
    action_server.send_string("ERROR %s"%result)
