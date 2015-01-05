from random import shuffle

suites = 'SDHC'
ranks  = '23456789TJQKA'

def poker(hands):
    """Return a list of winning hands: poker([hand,...]) => [hand,...]"""
    return allmax(hands, key=hand_rank)

def allmax(iterable, key=None):
    """Return a list of all items equal to the max of the iterable."""
    result, maxval = [], None
    key = key or (lambda x: x)
    for x in iterable:
        xval = key(x)
        if not result or xval > maxval:
            result, maxval = [x], xval
        elif xval == maxval:
            result.append(x)

    return result

def hand_rank(hand):
    """Return the rank of a given hand as a tuple"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4,ranks):
        return (7,kind(4,ranks),kind(1,ranks))
    elif kind(3,ranks) and kind(2,ranks):
        return (6,kind(3,ranks),kind(2,ranks))
    elif flush(hand):
        return (5,ranks)
    elif straight(ranks):
        return (4,max(ranks))
    elif kind(3,ranks):
        return (3,kind(3,ranks),ranks)
    elif two_pairs(ranks):
        return (2,two_pairs(ranks),ranks)
    elif kind(2,ranks):
        return (1,kind(2,ranks),ranks)
    else:
        return (0,ranks)

def card_ranks(hand):
    """Return a decrescent ordered list of ranks in the hand using integers"""
    ranks = ['--23456789TJQKA'.index(r) for r,s in hand]
    ranks.sort(reverse=True)
    # Adjust if we have an A-5 straight (A becomes 1)
    return [5,4,3,2,1] if ranks == [14,5,4,3,2] else ranks

def straight(ranks):
    "Return True if the ordered ranks form a 5-card straight."
    return (max(ranks)-min(ranks) == 4) and (len(set(ranks)) == 5)

def flush(hand):
    "Return True if all the cards have the same suit."
    return [s for r,s in hand] == (5*[hand[0][1]])

def kind(count, ranks):
    """Return the first rank that this hand has exactly n of.
    Return None if there is no n-of-a-kind in the hand."""
    for r in ranks:
        if ranks.count(r) == count: return r
    return None

def two_pairs(ranks):
    """If there are two pair, return the two ranks as a
    tuple: (highest, lowest); otherwise return None."""
    pair = kind(2, ranks)
    lowpair = kind(2, list(reversed(ranks)))

    if pair and pair != lowpair:
        return (pair, lowpair)
    
    return None

def test_poker():
    """Test cases for the functions in poker program"""
    sf = "6C 7C 8C 9C TC".split() # Straight Flush
    fk = "9D 9H 9S 9C 7D".split() # Four of a Kind
    fh = "TD TC TH 7C 7D".split() # Full House    
    s1 = "AS 2S 3S 4S 5C".split() # A-5 straight
    s2 = "2C 3C 4C 5S 6S".split() # 2-6 straight
    ah = "AS 2S 3S 4S 6C".split() # A high
    sh = "2S 3S 4S 6C 7D".split() # 7 high
    
    fkranks = [9, 9, 9, 9, 7]
    tpranks = [9, 9, 6, 5, 5]

    # Testing kind
    assert kind(4, fkranks) == 9
    assert kind(3, fkranks) == None
    assert kind(2, fkranks) == None
    assert kind(1, fkranks) == 7

    # Testing card_rank
    assert card_ranks(sf) == [10, 9, 8, 7, 6]
    assert card_ranks(fk) == [9, 9, 9, 9, 7]
    assert card_ranks(fh) == [10, 10, 10, 7, 7]

    # Testing Straight and Flush
    assert straight([9, 8, 7, 6, 5]) == True
    assert straight([9, 8, 8, 6, 5]) == False
    assert flush(sf) == True
    assert flush(fk) == False
    
    # Testing full poker
    assert poker([s1, s2, ah, sh]) == [s2]
    assert poker([sf, fk, fh]) == [sf]
    assert poker([fk, fh]) == [fk]
    assert poker([sf]) == [sf]
    assert poker([sf] + 99*[fh]) == [sf]
    assert poker(2*[sf]+[sh]) == [sf,sf]

    # Testing hand_rank
    assert hand_rank(sf) == (8, 10)
    assert hand_rank(fk) == (7, 9, 7)
    assert hand_rank(fh) == (6, 10, 7)
    
    return 'tests pass'

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = []
        self.last_bet = 0

    def __str__(self):
        return str((self.name, self.hand, self.money, self.last_bet))

    def set_hand(self, hand):
        self.hand = hand

    def bet(self, ammount, correction=0):
        self.money -= ammount
        self.last_bet = ammount+correction #correction is for small blinds and calls
        return ammount

    def receive(self, ammount):
        self.money += ammount
        return ammount

class TexasGame:
    def __init__(self, players_list, start_money, start_blind = 10, min_bet = 10):
        self.players = [Player(p,start_money) for p in players_list]
        self.deck = [v+n for v in ranks for n in suites]
        self.blindval = start_blind
        self.min_bet = min_bet
        self.table = []
        self.pots = [] # Pots is a list to handle hard bet situations
        self.dealer = -1
        self.turn = 0
        self.round_count = 0
        self.last_raise = ('', 0)

    """Start a new hand"""
    def starthand(self):
        shuffle(self.deck)
        # Prepare Player's Hands
        start, stop = 0, 2
        for player in self.players:
            player.set_hand(self.deck[start:stop])
            start, stop = stop, stop + 2

        # Prepare Table's Cards
        self.table = self.deck[start:start+5]
        # Set the initial pot
        self.pots = [(self.players,0)]
        # Set the new dealer
        self.dealer = (self.dealer+1)%len(self.players)
        # Set initial turn
        self.turn = (self.dealer+3)%len(self.players)
        # Reset the last raise variable
        self.last_raise = (self.players[self.turn].name, self.blindval)
        self.round_count = 0

    """Calculate and collect blind bets"""
    def collect_blinds(self):
        # Return list of pairs (player, bet)
        big = self.players[(self.dealer+1)%len(self.players)]
        small = self.players[(self.dealer+2)%len(self.players)]

        # Calculate blinds (TODO: Should use only int division?)
        bet = self.blindval
        ret = [(big.name,big.bet(bet)),
               (small.name,small.bet(bet//2))]

        # Increment pot
        mainpot = self.pots[0]
        self.pots[0] = (mainpot[0], sum((v for _,v in ret), mainpot[1]))

        return ret

    """ Finish the hand, distribute money and remove players
        Returns a tuple with list of winners, prizes and list of removed players
        Reference http://poker.stackexchange.com/questions/462/how-are-side-pots-built
    """
    def endhand(self):
        # Loop through all existing pots, finding the winners and spliting the pot
        winners = {}
        for pot in self.pots:
            # Start creating an array of hands
            hands = [p.hand + self.table for p in pot[0]]
            # Use poker() function to find the winner/ties
            winner_hands = poker(hands)
            pot_winners = [pot[0][hands.index(h)] for h in winner_hands]
            # Define the prize and split it
            prize = pot[1]/len(pot_winners)
            # Compound the returning dict of winners
            for w in pot_winners:
                winners[w.name] = winners.get(w.name, 0) + w.receive(prize)
            
        # Clean the pot
        self.pots = []

        # Remove people with not enough money from the game
        removed = [p.name for p in self.players if p.money < self.blindval]
        self.players = [p for p in self.players if p.name not in removed]

        # Return the tuple of array of tuples representing winners and array of removed
        return (list(winners.items()), removed)
        
    """Finish this round"""
    def endround(self):
        # Define the turn 
        self.turn = (self.dealer+1)%len(self.pots[0][0])
        # Reset the last raise variable
        self.last_raise = (self.pots[0][0][self.turn].name, 0)
        # Reset last bet of players
        for p in self.players: p.bet(0)
        # Increase the round count
        self.round_count += 1

    """Return given player hand"""
    def get_hand(self, player):
        return next((x.hand for x in self.players if x.name == player), None)
        
    """Return visible cards in table"""
    def show_flop(self):
        num = 3 if self.round_count >= 1 else 1
        num += self.round_count - 1
        return ' '.join(self.table[0:num])

    """Return a tuple with player name and available options"""
    def get_turn(self):
        # Player can always fold
        actions = ['FOLD']
        
        # Retrieve actual player, and calculate bet ammount
        player = self.pots[0][0][self.turn]
        dif = self.last_raise[1] - player.last_bet

        # If the bet placed is equal to the raise value, player can check
        if dif == 0:
            actions.append('CHECK')
        # Otherwise, it it's smaller he can call (and have enough money)
        elif (dif > 0) and (player.money >= dif):
            actions.append('CALL')

        # If player have money for such, he can bet/raise
        if player.money > dif:
            actions.append('BET' if self.last_raise[1] == 0 else 'RAISE')
                
        #TODO: All in is always available
        #actions.append('ALLIN')
                
        return (player.name, actions)

    def check_turn(self, player, action):
        pl,acts = self.get_turn()
        return (pl == player) and (action in acts)

    def advance_turn(self, inc=1):
        self.turn = (self.turn + inc)%len(self.pots[0][0])
        
    """Action: Check - No action is performed"""
    def act_check(self, player):
        # Check to see if it's the player turn
        if not self.check_turn(player, 'CHECK'):
            return False

        #TODO Caso jogador last_raise tenham feito fold, preciso atualizar last_raise

        # Advance Turn
        self.advance_turn()
        return True

    """Action: Fold - Remove the player for this hand"""
    def act_fold(self, player):
        # Check to see if it's the player turn
        if not self.check_turn(player, 'FOLD'):
            return False
        
        # Remove player from all existing pots
        self.pots = [([p for p in ps if p.name != player], v) for ps,v in self.pots]
        
        # In case of folding, review the dealer
        if self.dealer == self.turn:
            self.dealer = (self.dealer-1)%len(self.pots[0][0])
        elif self.dealer > self.turn:
            self.dealer -= 1
                        
        # Advance Turn, but as we are folding, do not increment
        self.advance_turn(0)
        
        return True
        
    """Action: Call - Player pays the remaining bet"""
    def act_call(self, player):
        # Check to see if it's the player turn
        if not self.check_turn(player, 'CALL'):
            return False

        # Pay the remaining ammount
        player = self.pots[0][0][self.turn]
        value = player.bet(self.last_raise[1] - player.last_bet, player.last_bet)
        
        # Call does not create new pots, so increase the last one
        self.pots[-1] = (self.pots[-1][0], self.pots[-1][1]+value)

        # Advance Turn
        self.advance_turn()
        return True
        
    """Action: Bet/Raise - Player increases bet value"""
    def act_raise(self, player, action, ammount):
        # Check to see if it's the player turn
        if not self.check_turn(player, action):
            return False

        # Pay the remaining ammount plus the raise/bet value
        player = self.pots[0][0][self.turn]
        value = player.bet(ammount - player.last_bet, player.last_bet)
        
        # Bet/Raise does not create new pots, so increase the last one
        self.pots[-1] = (self.pots[-1][0], self.pots[-1][1]+value)

        # Increase the last_raise var
        self.last_raise = (player.name, ammount)

        # Advance Turn
        self.advance_turn()
        return True
        
    """TODO: Action: All in - Player put all his money in the pot"""
    def act_allin(self, player):
        # Check to see if it's the player turn
        if not self.check_turn(player, 'ALLIN'):
            return False

        # Pay the remaining ammount plus the raise/bet value
        player = self.pots[0][0][self.turn]
        value = (self.last_raise[1] - player.last_bet)
        player.bet(value, player.last_bet)
        
        # TODO: All in can create side pots
        # TODO: Check how much covers the actual bet
        # TODO: Everything that does not cover, will be taken from others in this round

        # TODO: Increase the last_raise var if needed

        # Advance Turn
        self.advance_turn()
        return True

    """Check to see if it's time to end the round"""
    def check_endround(self):
        return (len(self.pots[0][0]) == 1) or \
               (self.pots[0][0][self.turn].name == self.last_raise[0])
    
    """Check to see if it's time to end the hand"""
    def check_endhand(self):
        return (len(self.pots[0][0]) == 1) or (self.round_count == 3)

    """Check to see if this is a game over"""
    def is_gameover(self):
        return len(self.players) == 1

    """Check to see if the hand have finished"""
    def is_handover(self):
        return len(self.pots) == 0


def test_table():
    t = TexasGame("a b c d".split(),100)
    t.starthand()

    print('Test Game Started:')
    for p in t.players:
        print(p)

    # After start, everyone has 2 cards
    assert all([len(p.hand) == 2 for p in t.players])

    blinds = t.collect_blinds()

    print('Blinds collected: %s'%str(blinds))
    assert blinds[0] == ('b',10) and blinds[1] == ('c',5)

    tu = t.get_turn()
    print(tu)
    assert tu == ('d', ['FOLD','CALL','RAISE'])

    print('d calls')
    assert t.act_call('d')
    assert not t.check_endround()
    
    tu = t.get_turn()
    print(tu)
    assert tu == ('a', ['FOLD','CALL','RAISE'])

    print('a folds')
    assert t.act_fold('a')
    assert not t.check_endround()
    #dealer folded ... 

    tu = t.get_turn()
    print(tu)
    assert tu == ('b', ['FOLD','CHECK','RAISE'])

    print('b checks')
    assert not t.act_call('b')
    assert not t.act_check('c')
    assert t.act_check('b')
    assert not t.check_endround()
    
    tu = t.get_turn()
    print(tu)
    assert tu == ('c', ['FOLD','CALL','RAISE'])
    print('c calls')
    assert t.act_call('c')
    
    # After this pot will be 30, there will be 3 left on game ...
    assert t.pots[0][1] == 30 and len(t.pots[0][0]) == 3
    # ... and everyone still playing should have 90 money left, last_bet = 10
    assert all([p.money == 90 and p.last_bet == 10 for p in t.pots[0][0]])

    # Round is over!
    assert t.check_endround()
    assert not t.check_endhand()
    t.endround()

    print('New round started, table:',t.show_flop())
    assert len(t.show_flop().split()) == 3
        
    # In the second round (and above), everyone can check
    for p in 'b c d'.split():
        tu = t.get_turn()
        print(tu)
        assert tu == (p, ['FOLD','CHECK','BET'])
        assert t.act_check(p)
        print(p, 'checks')

    assert t.check_endround()
    assert not t.check_endhand()
    t.endround()
    
    print('New round started, table:',t.show_flop())
    assert len(t.show_flop().split()) == 4
        
    tu = t.get_turn()
    print(tu)
    assert tu == ('b', ['FOLD','CHECK','BET'])
    print('b bets 10')
    assert t.act_raise('b','BET',10)
    print(t.last_raise, t.players[1])
    assert t.last_raise == ('b', 10)
    assert t.pots[0][1] == 40

    tu = t.get_turn()
    print(tu)
    assert tu == ('c', ['FOLD','CALL','RAISE'])    
    print('c raises 10, so 20')
    assert t.act_raise('c','RAISE',20)
    print(t.last_raise, t.players[2])
    assert t.last_raise == ('c', 20)
    assert t.pots[0][1] == 60

    tu = t.get_turn()
    print(tu)
    assert tu == ('d', ['FOLD','CALL','RAISE'])    
    print('d raises more 10, so 30')
    assert t.act_raise('d','RAISE',30)
    print(t.last_raise, t.players[3])
    assert t.last_raise == ('d', 30)
    assert t.pots[0][1] == 90
    
    tu = t.get_turn()
    print(tu)
    assert tu == ('b', ['FOLD','CALL','RAISE'])
    print('b folds')
    assert t.act_fold('b')
    
    tu = t.get_turn()
    print(tu)
    assert tu == ('c', ['FOLD','CALL','RAISE'])
    print('c calls')
    assert t.act_call('c')    
    print(t.last_raise, t.players[2])
    assert t.pots[0][1] == 100

    assert t.check_endround()
    assert not t.check_endhand()
    t.endround()
    
    print('Last round started, table:',t.show_flop())
    assert len(t.show_flop().split()) == 5
    
    tu = t.get_turn()
    print(tu)
    assert tu == ('c', ['FOLD','CHECK','BET'])
    print('c folds')
    assert t.act_fold('c')

    print(t.turn,t.pots[0],t.last_raise)
    assert t.check_endround()
    assert t.check_endhand()

    w = t.endhand()
    print(w)

    return 'test passes'


# If user call as script, run the tests
if __name__ == '__main__':
    print(test_poker())