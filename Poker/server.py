#!/usr/bin/env python3

import zmq
import time
from rules import *

port = 5555
start_money = 100

ctx = zmq.Context()

action_server = ctx.socket(zmq.REP)
action_server.bind("tcp://127.0.0.1:%d"%port)

status_publisher = ctx.socket(zmq.PUB)
status_publisher.bind("tcp://127.0.0.1:%d"%(port+1))

poller = zmq.Poller()
poller.register(action_server, zmq.POLLIN)

max_players = 4
player_list = []

# Waiting for players to sync and join table
while len(player_list) < max_players:
    socks = poller.poll(1000)
    if not len(socks):
        print('trying') 
        status_publisher.send_string('AVAILABLE')
        continue

    msg = action_server.recv_string()

    print('received:',msg)
    if msg.startswith('SUBSCRIBE'):
        msg = msg.split()
        if len(msg) < 2:
            result = 'ERROR Invalid Message'
        elif player_list.count(msg[1]) > 0:
            result = 'ERROR Name already exists'
        else:
            player_list.append(msg[1])
            result = 'ACK'
    else:
        result = 'ERROR Invalid Message'

    action_server.send_string(result)

# Game ready to start, establish table and handle main protocol
table = TexasGame(player_list, start_money)

while True:
    table.starthand()
    status_publisher('GETHANDS %s DEALER'%table.get_dealer())
    