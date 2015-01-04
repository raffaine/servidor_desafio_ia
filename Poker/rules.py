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
        return (2,two_pair(ranks),ranks)
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

    def set_hand(self, hand):
        self.hand = hand

    def bet(self, ammount):
        self.money -= ammount
        return ammount

    def receive(self, ammount):
        self.money += ammount

class TexasGame:
    def __init__(self, players_list, start_money, start_blind = 10, min_bet = 10):
        self.players = [Player(p,start_money) for p in players_list]
        self.deck = [v+n for v in ranks for n in suites]
        self.blindval = start_blind
        self.min_bet = min_bet
        self.table = []
        self.pot = [] # Pot is a list to handle hard bet situations
        self.dealer = -1
        self.turn = 0

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
        self.pot = [(self.players,0)]
        # Set the new dealer
        self.dealer = (self.dealer+1)%len(self.players)
        # Set initial turn
        self.turn = (self.dealer+3)%len(self.players)

    """Calculate and collect blind bets"""
    def collect_blinds(self):
        # Return list of pairs (player, bet)
        big = self.players[(self.dealer+1)%len(self.players)]
        small = self.players[(self.dealer+1)%len(self.players)]

        # Calculate blinds (TODO: Should use only int division?)
        bet = self.blindval
        ret = [(big.name,big.bet(bet)),
               (small.name,small.bet(bet/2))]

        # Increment pot
        self.pot[-1][1] += sum(v for _,v in ret) 

        return ret

    """Finish the round, distribute money and remove players
        Returns list of removed players"""
    def endhand(self):
        #TODO: Find the winner
        # Start creating an array of hands
        hands = [p.hand + self.table for p in self.pot[0][0]]
        # Use poker() function to find the winner/ties
        # Split the main and side pots
        #TODO: distribute the money in the pot
        # Reference http://poker.stackexchange.com/questions/462/how-are-side-pots-built
        self.pot = []

        # Remove people with not enough money from the game
        removed = [p.name for p in self.players if p.money < self.blindval]
        self.players = [p for p in self.players if p.name not in removed]

        return removed

    """Return given player hand"""
    def get_hand(self, player):
        return next((x.hand for x in self.players if x.name == player), None)
        
    """Return a tuple with player name and available options"""
    def get_turn(self):
        # Player can always fold
        actions = ['FOLD']
        player = self.players[self.turn]

        #remember: if no raise, big blind (or last raise) can check
        #remember: small blind have already paid some ammount

        #calculate if player can call/raise, or it would be allin
        
        #TODO TODO TODO
                
        return (player.name, actions)

    """Check to see if this is a game over"""
    def is_gameover(self):
        return len(self.players) == 1

    """Check to see if this is the end of a hand"""
    def is_handover(self):
        return len(self.pot) == 0


# If user call as script, run the tests
if __name__ == '__main__':
    print(test_poker())