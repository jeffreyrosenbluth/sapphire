#!/usr/bin/env python

import random 
from itertools import permutations

class Card(object):
    """playing card"""
    def __init__(self, rank = 0, suit = ''):
        self.rank = rank
        self.suit = suit
        self.wild_score = 6
        self.in_meld = False

    def valid(self):
        if self.rank in range(1,14) and self.suit in ('schd'):
            return True
        else:
            return False 

    def format(self):
        if not self.valid(): return 'INVALID CARD'
        if self.rank in range(10,14):
            r = 'TJQK'[self.rank - 10]
        elif self.rank == 1:
            r = 'A'
        else:
            r = str(self.rank)
        return r + self.suit.upper()
    
class Group(object):
    """a set of cards"""
    def __init__(self, cards = None):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards 

    def show(self, title = None):  
        if title: print title.upper() + ' : ' + str(len(self.cards))
        for j in range(20): print '-',
        not_empty = False
        print
        for suit in 'schd':
            for c in sorted((c for c in self.cards if c.suit == suit)):
                print c.format(),
                not_empty = True
            if not_empty: print
            not_empty = False
        print            

    def enter(self, text):
        """use a plain text string to set up a group of cards"""
        ranks = '0a23456789tjqk'
        t = text.split()
        for c in t:
            r = ranks.index(c[0].lower())
            s = c[1].lower()
            t = Card(r,s)
            self.cards.append(t)

    def take_from(self, card_name, grp):
        """move cards from grp to self.cards"""
        ranks = '0a23456789tjqk'
        rs = (ranks.index(card_name[0].lower()), card_name[1].lower())
        for card in grp.cards:
            if (card.rank, card.suit) == rs:
                c = card
                break;
        self.cards.append(c)
        grp.cards.remove(c)

class Deck(Group):
    """a standard 52 card deck"""
    def __init__(self, shuffle = False):
        super(Deck, self).__init__()
        self.cards = [Card(r,s) for s in 'schd' for r in range(1,14)]
        if shuffle:
            n = len(self.cards)
            for i in range(n - 1):
                j = random.randrange(i,n)
                self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
                        
class Hand(Group):
    """A gin rummy hand"""
    def __init__(self, text = None):
        super(Hand, self).__init__()
        self.orgs = frozenset()
        if text:
            self.enter(text)

    def show_orgs(self):
        n = len(self.orgs)
        print 'ARRANGEMENTS : ',n
        for j in range(20): print '-',
        print
        for o in self.orgs:
            for arr in sorted(o, key = lambda x: len(x), reverse = True):
                for a in sorted(arr):
                    print a.format(),
                print  
            print 'MELD COUNT: ', meld_count(o)
            print                     

    def run(self, suit, cards):
        def runner(cs, rs):
            if not cs:
                return rs
            else:
                rs.append(cs[0])
                if len(cs) > 1 and cs[1].rank - cs[0].rank == 1:
                    runner(cs[1:], rs)
            return rs
        return runner(cards,[])    

    def runs(self, suit):
        cards = [c for c in self.cards if c.suit == suit]
        cards.sort(key = lambda x: x.rank)
        def runs_iter(cs, rs):
            if not cs:
                return rs
            else:
                r = self.run(suit, cs)
                n = len(r)
                rs.append(r)
                return runs_iter(cs[n:], rs)
        return runs_iter(cards, []) 

    def points(self):
        result = 100
        for h in self.orgs: 
            p = 0
            for m in h:
                if len(m) < 3:
                    for  c in m:
                        p += min(c.rank, 10)
            result = min(result, p)
        return result    

    def possibilities(self):
        allruns = self.runs('s') + self.runs('c') + self.runs('h') + self.runs('d')
        r3 = [r for r in allruns if len(r) >= 3]
        r2 = [r for r in allruns if len(r) == 2]
        r1 = [r for r in allruns if len(r) == 1]
        allsets = []
        for i in range(14):
            s = [c for c in self.cards if c.rank == i + 1]
            if s:
                allsets.append(s)
        s3 = [s for s in allsets if len(s) >= 3]
        s2 = [s for s in allsets if len(s) == 2]
        s1 = [s for s in allsets if len(s) == 1]
        p = [list(e) for e in permutations(r3 + s3)]
        p =  map(remove_conflicts, p)
        q = [list(e) for e in permutations(r2 + s2)]
        q = [e + f for e in p for f in q]
        q = map(remove_conflicts, q)
        for x in q:
            for y in self.cards:
                if not y in flatten(x):
                    x.append([y])
        self.orgs = uniqify(q)
        

############################################################################################

def conflict(r, s):
        con = False
        for c in r:
            if c in s:
                con = True
        return con    

def remove_conflicts(grps):
    if not grps: 
        return []
    clean = [grps.pop(0)]
    for g in grps:
        if not any([conflict(g,h) for h in clean ]):
            clean.append(g)
    return clean    

def flatten(ohand):
    return [x for xs in ohand for x in xs]  

def uniqify(lst):
    """convert a nested list of lists into a nested frozenset of frozensets"""
    return frozenset(map(uniqify, lst))  if isinstance(lst, list) else lst       

def meld_count(ohand):
    return sum([min(len(t),4) for t in ohand if len(t) >= 3])

def possible_runs(card, opponent_known, unknown):
    uk = Group(opponent_known.cards + unknown.cards)
    hits = 0
    def in_u(c):
        return c in uk
    cu = (card.rank + 1,card.suit)
    cuu = (card.rank + 2,card.suit)
    cd = (card.rank - 1,card.suit)
    cdd = (card.rank - 2,card.suit)
    isin = map(in_u, [cdd, cd, uk.rank, cu, cuu])
    for i in range(3):
        if all(isin[i:i + 3]):
            hits += 1
    return hits

def wildness(card, myhand, opponent_known, discards, unknown):
    combos = [3,1,0,0]
    known = Group(myhand.cards + discards.cards)
    r = len([c.rank for c in known.cards if c.rank == card.rank])
    hits = combos[r] + possible_runs(card, opponent_known, unknown)
    return hits

def goodness(card, myhand, opponent_known, discards, unknown):
    result = 0
    for h in myhand.orgs:
        for s in h:
            if card in s and len(s) >= 3:
                result = 1
    return result          

def throw(myhand, opponent_known, discards, unknown):  
    candidates = [c for c in myhand.cards if goodness(c, myhand, opponent_known, discards, unknown) == 0]
    card_wildness = 6
    card = (0,'')
    for c in candidates:
        c_wild = wildness(c, myhand, opponent_known, discards, unknown)
        if c_wild <= card_wildness:
            card_wildness = c_wild 
            card = c 
    return card

############################################################################################

def game_sim():
    """ Play gin without a physical deck"""
    deck = Deck(shuffle = True)
    hand = Hand()
    opponent = Hand()
    discards = Group([deck.cards.pop()])
    for i in range(4):
        print
    for i in range(10):
        hand.cards.append(deck.cards.pop())
    print
    hand.cards.append(discards.cards.pop())
    hand.show(title = "sapphire's hand")
    opponent.show(title = "opponent's hand")
    deck.show(title = 'deck')
    discards.show(title = 'discard pile')
    hand.possibilities()
    hand.show_orgs()
    print '*** POINTS: ', hand.points()
    thwow_choice = throw(hand, opponent, discards, deck)
    print thwow_choice.format()


game_sim()


