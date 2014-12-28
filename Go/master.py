import zmq
import threading

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



ctx = zmq.Context.instance()
fe = ctx.socket(zmq.ROUTER)
fe.bind('inproc://router_fe')
be = ctx.socket(zmq.ROUTER)
be.bind('inproc://router_be')

for i in range(3):
    threading.Thread(target=server,args=(i,)).start()
    threading.Thread(target=client,args=(i,i*10,)).start()

poller = zmq.Poller()
poller.register(fe, zmq.POLLIN)
poller.register(be, zmq.POLLIN)

print("broker started")

while threading.active_count() > 1:
    socks = dict(poller.poll(100))

    if socks.get(fe) == zmq.POLLIN:
        msg = fe.recv_multipart()
        msg[0],msg[2] = msg[2],msg[0]
        be.send_multipart(msg)

    if socks.get(be) == zmq.POLLIN:
        msg = be.recv_multipart()
        msg[0],msg[2] = msg[2],msg[0]
        fe.send_multipart(msg)
