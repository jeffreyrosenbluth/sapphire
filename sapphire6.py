#!/usr/bin/env python

import random

def setup():
    """ return a dictionary of card groupings rank=[0,12], suit=[0,3] """
    deck = [(r,s) for s in range(4) for r in range(13)]
    state = {'deck' : deck, 'sapphire' : [], 'opponent' : [], 'discards' : [], 'knock' : 0}
    return state

def card_name(tup):
    ranks = 'A23456789TJQK'
    suits = 'SCHD'
    return ranks[tup[0]] + suits[tup[1]]

def show_group(g):
    """ g a list of card tuples """
    for c in g:
        print card_name(c),
    print        

def deal(state):
    """ initialize a two player game, returns state dictionary """
    order = range(52)
    for i in range(52):
        j = random.randrange(i,52)
        order[i], order[j] = order[j], order[i]
    deck = state['deck']    
    for k in range(13):
        state['sapphire'].append(deck[order[k]])
        state['opponent'].append(deck[order[k+13]])
    state['discards'].append(deck[order[26]])    
    for c in state['sapphire'] + state['opponent'] + state['discards']:
        deck.remove(c)  
    return state  

def runs(hand):
    def runs_for_suit(hand, suit):
        ranks = range(13)
        cards_of_suit = [c[0] for c in hand if c[1] == suit]
        xs = [0] * 13
        for i in range(13):
            if i in cards_of_suit: xs[i] = 1 
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
                        run.append((ranks[j+k],suit)) 
                if run:        
                    result.append(run)  
        return result 
    all_runs = []
    for s in range(4):
        all_runs += runs_for_suit(hand, s)
    return all_runs   

def sets(hand):
    result = []
    for i in range(13):
        s = [c for c in hand if c[0] == i]
        if len(s) > 1:
            result.append(s)
    return result       

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

def flatten(seq):
    """ flatten a singley nested list of lists """
    return [x for xs in seq for x in xs]  

def possibilities(hand):
    """ generate a list of ways to organize a hand
        only consider hands with the maximum number of melds
        mmc, then add pairs and only accept hands with max 
        number of melds plus pairs """
    allruns = runs(hand)
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
        for y in hand:
            if not y in flatten(x):
                x.append([y])
    return uniqify(q)

def main():
    game = setup()
    game = deal(game)
    show_group(game['sapphire'])
    show_group(game['opponent'])
    show_group(game['discards'])
    show_group(game['deck'])
    print 'runs:',runs(game['sapphire'])
    print 'sets:',sets(game['sapphire'])

if __name__ == "__main__":
    # cProfile.run('main()')  
    main()