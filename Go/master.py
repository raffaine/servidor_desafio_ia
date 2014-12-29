#!/usr/bin/env python3

import zmq
import threading
import time

def server(id):
    ctx = zmq.Context.instance()
    skt = ctx.socket(zmq.REP)
    skt.set_string(zmq.IDENTITY, '%d'%id)
    skt.connect('inproc://router_be')    

    print("server %d started"%id)
    for i in range(5):
        msg = skt.recv_multipart()
        print("%d received:"%id, msg)
        rid = msg[0]
        skt.send_multipart([rid,b'ok'])

def client(id, cid):
    ctx = zmq.Context.instance()
    skt = ctx.socket(zmq.REQ)
    skt.connect('inproc://router_fe')

    srv_id = bytes('%d'%id,encoding='utf-8')

    print("client started")
    for i in range(5):
        skt.send_multipart([srv_id,bytes('%d message %d'%(cid,i)
                                         ,encoding='utf-8')])
        msg = skt.recv_multipart()
        print(msg)


def pserver(id):
    ctx = zmq.Context.instance()
    skt = ctx.socket(zmq.PUB)
    skey = bytes('%d'%id,encoding='utf-8')
    skt.connect('inproc://fwdrcv')    
    
    time.sleep(2)
    print("server %d started"%id)
    for i in range(5):
        skt.send_multipart([skey,bytes('msg %d'%i,
                                       encoding='utf-8')])

def pclient(id):
    ctx = zmq.Context.instance()
    skt = ctx.socket(zmq.SUB)
    skey = bytes('%d'%id,encoding='utf-8')

    skt.connect('tcp://127.0.0.1:6000')    
    skt.setsockopt(zmq.SUBSCRIBE,skey)

    print("client for %d started"%id)
    for i in range(5):
        msg = skt.recv_multipart()
        print("%d received:"%id, msg)
        
def forwarder():
    ctx = zmq.Context.instance()
    rcv = ctx.socket(zmq.SUB)
    rcv.bind('inproc://fwdrcv')
    rcv.setsockopt(zmq.SUBSCRIBE,b'')

    snd = ctx.socket(zmq.PUB)
    snd.bind('tcp://127.0.0.1:6000')

    zmq.device(zmq.FORWARDER,rcv,snd)

for i in range(2):
    threading.Thread(target=pclient,args=(i,)).start()
    threading.Thread(target=pserver,args=(i,)).start()

forwarder()

#ctx = zmq.Context.instance()
#fe = ctx.socket(zmq.ROUTER)
#fe.bind('inproc://router_fe')
#be = ctx.socket(zmq.ROUTER)
#be.bind('inproc://router_be')

#for i in range(3):
#    threading.Thread(target=server,args=(i,)).start()
#    threading.Thread(target=client,args=(i,i*10,)).start()

#poller = zmq.Poller()
#poller.register(fe, zmq.POLLIN)
#poller.register(be, zmq.POLLIN)

#print("broker started")

#while threading.active_count() > 1:
#    socks = dict(poller.poll(100))

#    if socks.get(fe) == zmq.POLLIN:
#        msg = fe.recv_multipart()
#        msg[0],msg[2] = msg[2],msg[0]
#        be.send_multipart(msg)

#    if socks.get(be) == zmq.POLLIN:
#        msg = be.recv_multipart()
#        msg[0],msg[2] = msg[2],msg[0]
#        fe.send_multipart(msg)
