servidor_desafio_ia
===================

Servidor para rodar os jogos propostos na lista da EC04 e testar quão bem uma IA desempenha frente as demais IAs oferecidas.

Go: Servidor simples para regular partidas de Go.

PROTOCOLO: 

- sincronia: AVAILABLE $CORES (CORES é a lista de cores disponiveis separadas por espaço, B, W ou ambas)
- ação na sincronia: SUBSCRIBE $COR (COR deve ser B ou W, e deve estar disponivel)
- resposta a ação na sincronia: ACK/ERROR %s
- ações: $JOGADOR $LINHA $COLUNA (JOGADOR é B ou W, LINHA E COLUNA sao entre (0,8))
- resposta: ACK/ERROR %s
- mensagens gerais: TURN $JOGADOR TABLE #$MESA (MESA É uma sequencia de 9*9 valores, linhas separadas por \n, onde os valores podem ser ' ', 'W', 'B'), usei o caracter # para marcar o inicio da mesa!
- mensagens gerais: GAMEOVER $RESULTADO (RESULTADO pode ser $JOGADOR WINS! ou DRAW)

FLUXO

1. Aperto de mãos inicial para sincronizar subscribers, onde o servidor envia a lista de 
2. Jogadores recebem via Subscriber status da mesa e de quem é a vez
3. Jogadores usam REQ para enviar ações, e enquanto não receberem ACK, permanece a vez dele (mensagem de erro será retornada caso contrário) - Lembre-se todo send para o socket REQ precisa ter um recv depois.
4. Após a ação novo status da mesa e jogador é retornado.
5. Caso o jogo encerre, ao invés do status da mesa será retornado gameover

**O servidor está usando unicode (utf-8 without BOM), lembre-se disso nos clientes! Isso pode mudar também, não é necessário, fiz porque fiz!**

Exemplo atual de como montar um cliente em Python 2.7 está apresentado no arquivo Go\ex_client.py

Poker: Servidor simples para regular partidas de Poker (Texas).

PROTOCOLO: 
- sincronia (recv SUB): AVAILABLE
- ação na sincronia (send REQ): SUBSCRIBE $NOME (NOME deve ser diferente de vazio e não estar em uso na mesa)
- resposta a ação na sincronia (recv REQ): ACK/ERROR %s
- começo de mão (recv SUB): GETHAND $DEALER (DEALER é o nome do jogador que será o DEALER nesta mão)
- ação começo de mão (send REQ): GETHAND $NOME (NOME é quem quer receber a mão)
- resposta a ação no começo de mão (recv REQ): $MÃO/ERROR (HAND é uma string com 2 cartas representando a mão)
- ações: $NOME $AÇÃO \[$VALOR\] (NOME do jogador, AÇÃO desejada dentre \[CALL, CHECK, FOLD, BET, ALLIN\] e VALOR é opcional sendo usado em caso de ação ser BET)
- resposta ACK/ERROR %s
	
