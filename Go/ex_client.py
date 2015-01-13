#!/usr/bin/env python3

import zmq

ctx = zmq.Context()
ac = ctx.socket(zmq.REQ)
ac.connect("tcp://localhost:5555")
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")

#importante criar um filtro, mesmo que vazio!!
sub.setsockopt_string(zmq.SUBSCRIBE,'') 

msg = sub.recv_string()
if msg.startswith('AVAILABLE'):
    color = msg.split()[1]
    ac.send_string('SUBSCRIBE %s'%color)
    msg = ac.recv_string()
    print(msg)

while True:
    msg = sub.recv_string()
    if msg.startswith('TURN'):
        msg = msg.split()
        table = msg[3]
        turn = msg[1]
        if turn == color:
            available = [(i//9,i%9) for (i,c) in enumerate(table) if c == '.']
            print(table,'and',available)
            if len(available) == 0:
                break

            ac.send_string("%s %d %d"%((color,)+available[0]))
            #opcional parametro zmq.NOBLOCK, mas cuidado se nao tiver msg ele joga exceção!
            msg = ac.recv_string() 
            if (msg != "ACK"):
                print("joga de novo!") #erro!
                break