servidor_desafio_ia
===================

Servidor para rodar os jogos propostos na lista da EC04 e testar quão bem uma IA desempenha frente as demais IAs oferecidas.

Go: Servidor simples para regular partidas de Go.
PROTOCOLO: 
ações: $JOGADOR $LINHA $COLUNA (JOGADOR é B ou W, LINHA E COLUNA sao entre (0,8))
resp: ACK/ERROR %s
sub: TURN $JOGADOR TABLE #$MESA (MESA É uma sequencia de 9*9 valores, linhas separadas por \n, onde os valores podem ser ' ', 'W', 'B'), usei o caracter # para marcar o inicio da mesa!
sub: GAMEOVER $RESULTADO (RESULTADO pode ser $JOGADOR WINS! ou DRAW)

FLUXO
TODO Aperto de mãos inicial para sincronizar subscribers (algo precisa ser feito para reliability tb)
Jogadores recebem via Subscriber status da mesa e de quem é a vez
Jogadores usam REQ para enviar ações, e enquanto não receberem ACK, permanece a vez dele (mensagem de erro será retornada caso contrário) - Lembre-se todo send para o socket REQ precisa ter um recv depois.
Após a ação novo status da mesa e jogador é retornado.
Caso o jogo encerre, ao invés do status da mesa será retornado gameover

O servidor está usando unicode (utf-8 signed), lembre-se disso nos clientes! Isso pode mudar também, não é necessário, fiz porque fiz!

Exemplo atual de como montar um cliente em Python 2.7 (zmq 2.x também!)
	import zmq
	ctx = zmq.Context()
	ac = ctx.socket(zmq.REQ)
	ac.connect("tcp://localhost:5555")
	sub = ctx.socket(zmq.SUB)
	sub.connect("tcp://localhost:5556")
	sub.setsockopt_string(zmq.SUBSCRIBE,unicode("")) #importante criar um filtro, mesmo que vazio!!
	
	ac.send_string("W 1 1")
	msg = ac.recv_string() #opcional parametro zmq.NOBLOCK, mas cuidado se nao tiver msg ele joga exceção!
	if (msg <> "ACK"):
		print("joga de novo!") #erro!
	else:
		result = sub.recv_string() #ou seja, se deu certo ele publica o status da mesa!

	
	
