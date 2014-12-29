#!/usr/bin/env python3

import zmq
import time
from board import *

port = 5555

ctx = zmq.Context()

action_server = ctx.socket(zmq.REP)
action_server.bind("tcp://127.0.0.1:%d"%port)

status_publisher = ctx.socket(zmq.PUB)
status_publisher.bind("tcp://127.0.0.1:%d"%(port+1))

table = GoTable()
players = dict([(GoTable.BLACK,'*'),(GoTable.WHITE,'*')])

while len(players) > 0:
    print('trying') 
    status_publisher.send_string('AVAILABLE %s'%(' '.join(players.keys())))

    try:
        msg = action_server.recv_string(flags=zmq.NOBLOCK);
    except zmq.error.Again:
        time.sleep(1)
        continue

    print('received:',msg)
    if msg.startswith('SUBSCRIBE'):
        msg = msg.split()
        if len(msg) < 2 or not players.get(msg[1]):
            result = 'ERROR Invalid Message'
        else:
            players.pop(msg[1])
            result = 'ACK'
    else:
        result = 'ERROR Invalid Message'

    action_server.send_string(result)

    
status_publisher.send_string("TURN %s TABLE #%s"%table.get_state())

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
