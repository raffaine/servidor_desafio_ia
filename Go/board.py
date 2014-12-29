
class GoTable:
    EMPTY = ' '
    BLACK = 'B'
    WHITE = 'W'

    def __init__(self, size = 9):
        self._size = size
        self._board = [' ' for i in range(self._size) 
                           for j in range(self._size)]

        self._score = dict([(GoTable.BLACK,0),(GoTable.WHITE,0)])
        self.game_over = False
        self.winner = GoTable.EMPTY
        self.active_player = GoTable.WHITE

    def _set(self, row, col, val):
        self._board[row*self._size+col] = val

    def _get(self, row, col):
        return self._board[row*self._size+col]

    def _is_bound(self, row, col):
        return (row < self._size and col < self._size and row >= 0 and col >= 0)

    def move(self, player, row, col):
        if (not self._is_bound(row,col) or self._get(row,col) != GoTable.EMPTY):
            return False
        
        #TODO Suponho que aqui venha a aplicacao de algumas regras do jogo, como peca come outra e tal
        #TODO Calcular também os pontos de cada jogador
        self._set(row, col, player)
        self.active_player = GoTable.BLACK if (self.active_player == GoTable.WHITE) \
                                           else GoTable.WHITE
        return True
        
    def get_state(self):
        return (self.active_player, self.print_board())

    def print_board(self):
        return '\n'.join([''.join(self._board[i*self._size:(i+1)*self._size]) 
                          for i in range(self._size)]) 

def strip_message(msg):
    """
    A mensagem deve ser do formato "PLAYER LINHA COLUNA"
    onde PLAYER in {'B','W'} e LINHA/COLUNA in range(BOARD_SIZE)
    """
    arr = msg.split(' ')
    if len(arr) < 3:
        return (False,"Invalid Message")

    who = arr[0]
    if who != GoTable.WHITE and who != GoTable.BLACK:
        return (False,"Invalid Player")

    try:
        row = int(arr[1])
        col = int(arr[2])

    except ValueError:
        return (False,"Invalid position")

    return (True,(who,row,col)) 
