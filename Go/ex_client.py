import zmq

ctx = zmq.Context()
ac = ctx.socket(zmq.REQ)
ac.connect("tcp://localhost:5555")
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")

#importante criar um filtro, mesmo que vazio!!
sub.setsockopt_string(zmq.SUBSCRIBE,'') 

ac.send_string("W 1 1")
#opcional parametro zmq.NOBLOCK, mas cuidado se nao tiver msg ele joga exceção!
msg = ac.recv_string() 
if (msg != "ACK"):
    print("joga de novo!") #erro!
else:
    result = sub.recv_string() #ou seja, se deu certo ele publica o status da mesa! 
    print(result)
