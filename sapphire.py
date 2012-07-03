#!/usr/bin/env python

import random
import time
from itertools import *

class Card(object):
    """ playing card
        location: p = pick pile, h = sapphire's hand, g = sapphire's unknown,
        u = opponents uknown hand, k = opponents known hand, d = discards """
    def __init__(self, rank, suit, position):
        self.rank = rank
        self.suit = suit
        self.position = position
        self.row = 0
        self.col = 0
        self.location = 'p'

    def __repr__(self):
        return '%s%s' % (self.rank, self.suit)

def make_deck(shuffle = False):
    """ create a deck of cards, if shuffle = True, then make_deck   
        the position attribute a random number between 0 and 51 """
    deck = []
    if shuffle:
        order = range(52)
        for i in range(52):
            j = random.randrange(i,52)
            order[i], order[j] = order[j], order[i]
    for i, suit in enumerate('SCHD'):
        row = []
        for j, rank in enumerate('A23456789TJQK'):
            idx = i * 13 + j
            pos = order[idx] if shuffle else idx
            card = Card(rank, suit, pos)
            card.row = i
            card.col = j
            row.append(card)
        deck.append(row) 
    return deck   

def set_locations(deck, strng, location):
    """use a plain text string to set up a group of cards"""
    ranks = 'A23456789TJQK'
    suits = 'SCHD'
    t = strng.split()
    for c in t:
        r = ranks.index(c[0].upper())
        s = suits.index(c[1].upper())
        deck[s][r].location = location

def show_locations(deck, location):
    """ show the cards for a particular location, eg. hand, discards, etc. """
    seq = [c for row in deck for c in row if c.location == location]
    for c in seq:
        print c.rank+c.suit + ' ',
    print    

def get_location(deck, location):
    """ the subset of the deck with in location """
    return [c for row in deck for c in row if c.location == location]   

def get_card(deck, rank, suit):
    """ utitlity function to return a card object given it's ranks and suit """
    row = 'SCHD'.index(suit)
    col = 'A23456789TJQK'.index(rank)
    return deck[row][col]

def get_adjacent_card(deck, card, offset):
    """ get the card of the same suit offset cards to the right """
    col = card.col + offset
    if col not in range(13):
        return None
    else:
        return deck[card.row][col]   

def get_coord(deck, position):
    """ return the coordinates in the deck for a position
        in a  shuffled deck """
    for i, row in enumerate(deck):
        for j, card in enumerate(row):
            if card.position == position:
                return i, j

def card_count(deck, location):
    """ number of cards in location """
    return len([c for row in deck for c in row if c.location == location])                    

def display(deck, location):
    cards = sorted([card for row in deck for card in row], key = lambda x : (x.location, x.suit, x.col))
    cards = [c for c in cards if c.location == location]
    for card in cards:
        print 'Card: %s%s Pos: %2i Loc: %s Col: %2i' % (card.rank, card.suit, card.position, card.location, card.col)
    print    

def show_grid(deck):
    """ print out of grid of locations for the entire deck """
    print '     A   2   3   4   5   6   7   8   9   T   J   Q   K'
    print '     -   -   -   -   -   -   -   -   -   -   -   -   -'
    for idx, row in enumerate(deck):
        print 'SCHD'[idx], ': ',
        for card in row:
            print card.location, ' ',
        print
    print    

def runs(deck, suit, location):
    """ creat a list of lists of runs for each suit """
    idx = 'SCHD'.index(suit)
    cards = deck[idx]
    # xs is list of 0s and 1s denoting the prescence of abscence of the card
    # in the location
    xs = [(lambda x: 1 if x.location == location else 0)(x) for x in cards]
    result = []
    for n in range(2,6):
        size =  len(xs)
        run_length = []
        for i in range(size):
            m = min(i + n, size)
            run_length.append(sum(xs[i:m]))
        for j, x in enumerate(run_length):
            run = []
            if x == n:
                for k in range(n):
                    run.append(cards[j+k]) 
            if run:        
                result.append(run)  
    return result    

def sets(deck, location):
    cards = get_location(deck, location)
    result = []
    for i in range(14):
        s = [c for c in cards if c.col == i]
        if s:
            result.append(s)
    return result            

def points(seq):
    """ points from non melded cards in the sequence seq """
    pts = 0
    for m in seq: 
        if len(m) < 3:
            for  c in m:
                pts += min(c.col + 1, 10)
    return pts    

def conflict(r, s):
    """ True of any of the cards in r are also in s """
    return any([(c in s) for c in r])  

def no_conflicts(seq):
    n = len(seq)
    if n <= 1:
        return True        
    for i in range(n):
        for j in range(i+1,n):
            if conflict(seq[i],seq[j]):
                return False
    return True
        
def remove_conflicts(seq):
    if not seq: 
        return []
    clean = [seq.pop(0)]
    for g in seq:
        if not any([conflict(g,h) for h in clean]):
            clean.append(g)
    return clean    

def flatten(seq):
    """ flatten a singley nested list of lists """
    return [x for xs in seq for x in xs]  

def uniqify(seq):
    """convert a nested list of lists into a nested frozenset of frozensets"""
    return frozenset(map(uniqify, seq))  if isinstance(seq, list) else seq   

def meld_count(seq):
    """ number of melds and the number of cards that are in melds """
    melds = [s for s in seq if len(s) >= 3]
    cs = sum([min(len(t),4) for t in melds]) 
    return cs  

def possibilities(deck, location):
    """ generate a list of ways to organize a hand (location)
        only consider hands with the maximum number of melds
        mmc, then add pairs and only accept hands with max 
        number of melds plus pairs """
    cards = [c for row in deck for c in row if c.location == location]
    allruns = flatten([runs(deck, s, location) for s in 'SCHD'])
    r3 = [r for r in allruns if len(r) >= 3]
    r2 = [r for r in allruns if len(r) == 2]
    allsets = sets(deck, location)
    s4 = [s for s in allsets if len(s) == 4]
    # if there is a set of 4 add in the subsets of lenght 3
    s4 = s4 + flatten([map(list,(combinations(s,3))) for s in s4])
    s3 = [s for s in allsets if len(s) == 3]
    s3 = s3 + s4
    s2 = [s for s in allsets if len(s) == 2]

    # create a list of combinations of set and run melds taken
    # 1,2, and 3 at a time
    p = [[]]
    for i in range(1,4):
        p += [list(e) for e in combinations(r3 + s3,i)] 

    # eliminated lists that contain melds that share cards     
    p = [e for e in p if no_conflicts(e)]

    # calculate the maximum number of melds and eliminate
    # all the hands that have less
    mmc = max([len(e) for e in p])
    p = [e for e in p if len(e) == mmc]

    # calculate the maximum number of pairs that can be added
    # to a hand with mmc melds of at least 3 cards each. And then
    # proceed for pairs as with melds
    q = [[]]
    max_pairs = int((11 - mmc * 3) / 2) + 1 
    for i in range(1,max_pairs):
        q += [list(e) for e in combinations(r2 + s2,i)]
    q = [e for e in q if no_conflicts(e)] 

    # consider adding the pairs to the melds and then eliminated
    # pairs that use cards from melds
    q = [e + f for e in p for f in q]
    q = map(remove_conflicts, q)
    mmd = max([len(e) for e in q])
    q = [e for e in q if len(e) == mmd]

    # fill the rest of the hand with single cards
    for x in q:
        for y in cards:
            if not y in flatten(x):
                x.append([y])
    return uniqify(q)

def possible_runs(deck, card):
    """ to calculate wildness from sapphires perspective ONLY """
    opp = get_location(deck, 'u') + get_location(deck, 'p') + [card]
    hits = 0
    cu = get_adjacent_card(deck, card, 1)
    cuu = get_adjacent_card(deck, card, 2)
    cd = get_adjacent_card(deck, card, -1)
    cdd = get_adjacent_card(deck, card, -2)
    isin = [c in opp for c in [cdd, cd, card, cu, cuu]]
    for i in range(3):
        if all(isin[i:i + 3]):
            hits += 1
    return hits

def wildness(deck, card):
    """ how many pairs of cards could be in the opponents hand
        that the card would make into a meld -- sapphires perspective
        ONLY """
    combos = [3,1,0,0]
    known = get_location(deck, 'h') + get_location(deck, 'd')

    # subtract 1 since the card is in sapphires hand
    r = len([c.rank for c in known if c.rank == card.rank]) - 1
    hits = combos[r] + possible_runs(deck, card)
    return hits

def best_hand(hands):
    min_points = 110
    for hand in hands:
        p = points(hand)
        if p < min_points:
            min_points = p
            h = hand
    return h

def show_orgs(xs):
    n = len(xs)
    print 'ARRANGEMENTS : ',n
    for j in range(25): print '-',
    print
    for o in xs:
        for arr in sorted(o, key = lambda x: len(x), reverse = True):
            for a in sorted(arr):
                print a.rank + a.suit,
            print ' | ',  
        print '\nPOINTS:%2i MELD COUNT:%2i ' % (points(o), meld_count(o))
        print                             

def should_take_discard(deck, location, discard):
    old_poss = possibilities(deck, location)
    max_meld_count = max(map(meld_count, old_poss))
    discard.location = location
    new_poss = possibilities(deck, location)
    new_max_meld_count = max(map(meld_count, new_poss))
    discard.location = 'd'
    return True if new_max_meld_count > max_meld_count else False

def pick_from_deck(deck):
    idx = 52 - card_count(deck, 'p')
    row, col = get_coord(deck, idx)
    return deck[row][col]  

def sapphire_throw(deck, location):
    cards = [c for row in deck for c in row if c.location == location]
    poss = possibilities(deck, location)
    min_points = 110
    for h in poss:
        p = points(h)
        if p < min_points:
            min_points = p
            hand = h 
    throws = [s for s in hand if len(s) < 2]
    if not throws:           
        throws = [s for s in hand if len(s) < 3]
    if not throws:    
        throws = [s for s in hand]
    throws = flatten(throws)
    min_wild = 7
    for c in throws:
        w = wildness(deck, c)
        if w < min_wild:
            min_wild = w
            card = c
    return card  
          
def choose_throw(deck, location):
    cards = [c for row in deck for c in row if c.location == location]
    poss = possibilities(deck, location)
    min_points = 110
    for h in poss:
        p = points(h)
        if p < min_points:
            min_points = p
            hand = h  
    throws = [s for s in hand if len(s) < 2]
    if not throws:           
        throws = [s for s in hand if len(s) < 3]
    if not throws:    
        throws = [s for s in hand]
    throws = flatten(throws) 
    max_points = -1
    for c in throws:
        p = c.col
        if p > max_points:
            max_points = p
            card = c
    return card  

def take_turn(deck, location, discard, knock_value):
    poss = possibilities(deck, location)
    min_points = points(best_hand(poss))
    # throw_func = sapphire_throw if location == 'h' else choose_throw
    throw_func = choose_throw
    if min_points <= knock_value:
        return None, False        
    if should_take_discard(deck, location, discard):
        discard.location = location
    else:
        pick = pick_from_deck(deck)
        pick.location = location
    disc = throw_func(deck, location)
    disc.location = 'd'        
    g = False if points(best_hand(possibilities(deck,location))) <= knock_value else True
    return disc, g

def deal():
    deck = make_deck(shuffle = True)
    sapphire_turn = True
    game = True
    cards_left = card_count(deck,'p')
    for pos in range(21):
        row, col = get_coord(deck, pos)
        if pos < 10:
            deck[row][col].location = 'h'
        elif pos < 20:
            deck[row][col].location = 'u'
        else:
            discard = deck[row][col]
            discard.location = 'd' 
            knock_value = min(deck[row][col].col + 1,10)
            if knock_value == 1: knock_value = 0                    
    sapphire_wins = False
    score = 0
    turns = 0
    while game and cards_left > 2 and turns < 50:
        turns += 1
        # print '.',
        if sapphire_turn:
            discard, game = take_turn(deck, 'h', discard, knock_value)
            if not game:
                sapphire_wins = True
                score = points(best_hand(possibilities(deck,'u')))
        else:
            discard, game = take_turn(deck, 'u', discard, knock_value)
            if not game:
                score = points(best_hand(possibilities(deck,'h'))) 
        sapphire_turn = not sapphire_turn
        cards_left = card_count(deck, 'p')
    # if sapphire_wins:
    #     print score 
    # else:
    #     print -score        
    if cards_left > 2:    
        return sapphire_wins, score
    else:
        return False, 0    
    
def play():
    s_score = 0
    o_score = 0
    while max(s_score, o_score) < 200:
        win, s = deal()
        if win:
            s_score += s
        else:
            o_score += s    
    print 'Sapphire: %3i Opponent %3i' % (s_score, o_score)
    return True if s_score > o_score else False  

def test():
    s = o = 0
    for i in range(1000):
        print i,
        if play():
            s += 1
        else:
            o += 1
    print 'sappire wins: %4i opponent wins %4i' % (s,o)                
    
test()


