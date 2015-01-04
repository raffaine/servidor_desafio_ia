#!/usr/bin/env python3

import zmq
import time
from rules import *

port = 5555
start_money = 100
max_players = 4
player_list = []

"""Pool Request handler, just to keep it of with game logic"""
def pool_req(handler_map, timeout=1000):
    socks = poller.poll(timeout)
    if not len(socks):
        return False

    msg = action_server.recv_string()
    print('received: %s'%msg)

    title, _, content = msg.partition(' ')
    cmd = handler_map.get(title, lambda _: 'Error: Invalid Message')

    action_server.send_string(cmd(content))
    return True

"""Game Logic: Subscribe - Used to add new players to the game"""
def subscribe(name):
    #TODO As I use spaces to separate names lists, it would be a good idea to remove then
    if name != '' and player_list.count(name) == 0:
       player_list.append(name)
       return 'ACK'    
    else:
       return 'ERROR Invalid Argument'  

"""Game Logic: GetHand - Used to get a players hand"""
def gethand(name):
    return hand or 'ERROR Invalid Player'


### ZMQ Initialization ###
ctx = zmq.Context()

action_server = ctx.socket(zmq.REP)
action_server.bind("tcp://127.0.0.1:%d"%port)

status_publisher = ctx.socket(zmq.PUB)
status_publisher.bind("tcp://127.0.0.1:%d"%(port+1))

poller = zmq.Poller()
poller.register(action_server, zmq.POLLIN)

#This is used to hold all possible options for handling
#   protocol messages
handlers = {
    'SUBSCRIBE': subscribe(name)       
}


# Waiting for players to sync and join table
while len(player_list) < max_players:
    if not pool_req(handlers):
        status_publisher.send_string('AVAILABLE')
 

# Game ready to start, establish table and handle main protocol
table = TexasGame(player_list, start_money)

# Show players table position and general info
status_publisher('START %d %d %s'%(start_money, table.min_bet, 
                                   ' '.join([s.name for s in table.players])))

# Reajust handlers
handlers.pop('SUBSCRIBE', None)
handlers['GETHAND'] = gethand

# Main Game Loop
while not table.is_gameover():
    # When this is signalized, start a new hand
    if table.is_handover():
        table.starthand()
        status_publisher.send_string('GETHANDS')

        # Gives a few secs for players to get their hands
        while pool_req(handlers, 2000): pass

        #TODO Inform Big and Small Blinds bets
        for p,v in table.collect_blinds():
            status_publisher.send_string('BLIND %s %d'%(p,v))

    # Inform Turn
    status_publisher.send_string('TURN %s %s'%table.get_turn())

    # Wait a few for some message and do it all again
    while pool_req(handlers, 500): pass

  

    