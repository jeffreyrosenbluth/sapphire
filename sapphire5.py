#!/usr/bin/env python

import random
import time
from itertools import *

class Card(object):
    """ playing card rank=[0,12], suit=[0,3], position in deck """
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        ranks = 'A23456789TJQK'
        suits = 'SCHD'
        return '%s%s' % (ranks[self.rank], suits[self.suit])

class State(object):
    """ Game state information and methods """
    def __init__(self, shuffle = False):
        self.deck = [Card(r,s) for s in range(4) for r in range(13)]
        self.sapphire = []
        self.opponent = []
        self.discard = []
        self.knock = 0
        if shuffle:
            order = range(52)
            for i in range(52):
                j = random.randrange(i,52)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def show(self, group):
        print group

    def deal(self):
        for i in range(10):
            self.sapphire.append(self.deck.pop())    
            self.opponent.append(self.deck.pop())
        self.discard.append(self.deck.pop())
        self.knock = min(self.discard[0].rank, 9)
        if self.knock > 0: self.knock += 1  

    def get_same_suit(group, suit):
        cards = [c for c in group if c.suit == suit]
        return cards.sort()      

def show_state(game):
    game.deal()
    game.show(game.sapphire)
    game.show(game.opponent)
    game.show(game.deck)
    game.show(game.discard)
    print game.knock
    return game

def main():
    game = State(shuffle = True)
    show_state(game) 
    print game.get_same_suit(game.sapphire,0)
    # print runs(game.sapphire, 0)
    # print runs(game.sapphire, 1)   
    # print runs(game.sapphire, 2)   
    # print runs(game.sapphire, 3)   
   

# def runs(group, suit):
#     """ creat a list of lists of runs for each suit """
#     cards = [c for c in group if c.suit == suit]
#     card_ranks = [c.rank for c in cards]

#     # xs is list of 0s and 1s denoting the prescence of abscence of the card
#     xs = [0] * 13
#     for idx in range(13):
#         if idx in card_ranks: xs[idx] = 1
#     result = []
#     for n in range(2,6):
#         size =  len(xs)
#         run_length = []
#         for i in range(size):
#             m = min(i + n, size)
#             run_length.append(sum(xs[i:m]))
#         for j, x in enumerate(run_length):
#             run = []
#             if x == n:
#                 for k in range(n):
#                     run.append(cards[j+k]) 
#             if run:        
#                 result.append(run)  
#     return result        

if __name__ == "__main__":
    # cProfile.run('main()')  
    main()                  