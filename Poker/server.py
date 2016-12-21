#!/usr/bin/env python3

import zmq
import time
from rules import *

port = 5555
start_money = 100

tables = dict()
players = dict()

flatten = lambda l: [item for sublist in l for item in sublist]

class TableEntry():
    def __init__(self, min_players, max_players):
        self.game = None
        self.waiting = []
        self.min_players = min_players
        self.max_players = max_players

def pool_req(handler_map, timeout=1000):
    """Pool Request handler, just to keep it of with game logic"""
    socks = poller.poll(timeout)
    if not len(socks):
        return False

    msg = action_server.recv_string()
    print('received: %s'%msg)

    msg = msg.split(' ')
    cmd = handler_map.get(msg[0], lambda _: 'ERROR: Invalid Message')
    try:
        action_server.send_string(cmd(*msg[1:]))
    except TypeError:
        action_server.send_string('ERROR Invalid Call')

    return True

def create_table(table_name, min_players='2', max_players='4'):
    """Manager Logic: TABLE - Creates a new table with the given parameters"""
    if table_name in tables:
        return 'ERROR Table already exists'

    try:
        tables[table_name] = TableEntry(int(min_players), int(max_players))
    except ValueError:
        return 'ERROR Invalid parameters for table size'

    return 'ACK'

def list_tables():
    """Manager Logic: LIST - List all available tables"""
    return str([n for n in tables.keys()])

def join_table(usr_name, table_name):
    """Game Logic: JOIN - Used to add new players to an existing table"""
    if usr_name in players or usr_name in flatten(map(lambda t: t.waiting, iter(tables.values()))):
        return 'ERROR Player already in table'

    tbl = tables.get(table_name, None)
    #TODO logic for joining table already open
    if tbl and not tbl.game and usr_name not in tbl.waiting:
        tbl.waiting.append(usr_name)
        if len(tbl.waiting) == tbl.min_players:
            # Game ready to start, establish table and handle main protocol
            tbl.game = TexasGame(tbl.waiting, start_money)

            # Quick access to game from player's name
            while tbl.waiting:
                players[tbl.waiting.pop()] = tbl.game

            # Show players table position and general info
            status_publisher.send_string('%s START %d %d %s'%(table_name, start_money, \
                            tbl.game.min_bet, ' '.join([s.name for s in tbl.game.players])))

        return 'ACK'
    else:
        return 'ERROR Invalid Argument'

def leave_table(usr_name, table_name):
    """Game Logic: LEAVE - Used to remove players from a waiting table"""
    if usr_name in players:
        return 'ERROR Cannot leave running table ... yet'

    tbl = tables.get(table_name, None)
    if not tbl:
        return 'ERROR Table does not exist'

    if usr_name in tbl.waiting:
        tbl.waiting.remove(usr_name)
    else:
        return 'ERROR Player not in table'

    return 'ACK'

def get_hand(usr_name):
    """Game Logic: GetHand - Used to get a players hand"""
    tbl = players.get(usr_name, None)
    if not tbl:
        return 'ERROR Invalid Player'

    return str(tbl.get_hand(usr_name) or 'ERROR Invalid Player')

def get_turn(table_name):
    """Game Logic: GetTurn - Used to get a table current turn"""
    tbl = tables.get(table_name, None)
    if not tbl:
        return 'ERROR Invalid Table'

    return '%s %s'%tbl.game.get_turn()

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
    'JOIN': join_table,
    'LEAVE': leave_table,
    'TABLE': create_table,
    'LIST': list_tables,
    'GETHAND': get_hand,
    'GETTURN': get_turn
}

# Main Game Loop
try:
    while True:
        # Wait a few for some message and do it all again
        while pool_req(handlers, 500):
            pass

        # Do some table related logic
        for name, table in filter(lambda entry: entry[1].game, iter(tables.items())):
            # When this is signalized, start a new hand
            if table.game.is_handover():
                table.game.starthand()
                status_publisher.send_string('%s GETHANDS'%(name))

                # Give a few secs for players to get their hands
                while pool_req(handlers, 2000): pass

                # Inform Big and Small Blinds bets
                for p, v in table.game.collect_blinds():
                    status_publisher.send_string('%s BLIND %s %d'%(name, p, v))

except KeyboardInterrupt:
    status_publisher.send_string('GAMEOVER')

