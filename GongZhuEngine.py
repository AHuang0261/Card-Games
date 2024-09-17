from enum import Enum
from typing import Any
from Cards import *
import random
import pygame
import time
from GongZhuISMCTS import ISMCTSNode
import copy

class GameState(Enum):
    MAINMENU = -1
    STARTING = 0
    PLAYING = 1
    SCORING = 2
    BIDDING = 3
    WAITING = 4
    ENDED = 5

class ComMode(Enum):
    MULTIPLAYER = 0
    RANDOM = 1
    BASIC = 2
    SMART = 3

#Using 3.14 as a flag for the doubler for scoring
class GZCard(pygame.sprite.Sprite, Card):
    selected = [None] #static variable
    score = 0
    scoreable = False
    is_sellable = False
    rect = None
    def __init__(self, rank, suit):
        pygame.sprite.Sprite.__init__(self)
        Card.__init__(self, rank, suit)
        if self.suit == Suits.HEART:
            self.scoreable = True
            if self.rank <= 4: self.score = 0
            elif self.rank <= 10: self.score = 10
            else: self.score = 10 * (self.rank - 9)
        elif self.suit == Suits.SPADE: 
            if self.rank == 12: 
                self.score = 100
                self.scoreable = True
                self.is_sellable = True
        elif self.suit == Suits.DIAMOND:
            if self.rank == 11: 
                self.scoreable = True
                self.score = -100
                self.is_sellable = True
        else:
            if self.rank == 10: 
                self.scoreable = True
                self.score = 3.14 
                self.is_sellable = True
        if self.rank == 14 and self.suit == Suits.HEART: self.is_sellable = True
        # self.score *= -1

    def __repr__(self) -> str:
        return super().__repr__()

    def init_image(self):
        self.load_image()
        self.rect = self.image.get_rect(topleft = (0,0))

    def clicked(self):
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            # print(f"{self.rank} of {self.suit}s clicked. Score is {self.score}")
            return True
        return False
    
    def get_clicked(self):
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            return self

    def update(self):
        if self.clicked():
            GZCard.selected.append(self)
            while len(GZCard.selected) > 1:
                GZCard.selected.pop(0)          
            
class LogicalGZCard(LogicalCard):
    score = 0
    scoreable = False
    is_sellable = False
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        if self.suit == Suits.HEART:
            self.scoreable = True
            if self.rank <= 4: self.score = 0
            elif self.rank <= 10: self.score = 10
            else: self.score = 10 * (self.rank - 9)
        elif self.suit == Suits.SPADE: 
            if self.rank == 12: 
                self.score = 100
                self.scoreable = True
                self.is_sellable = True
        elif self.suit == Suits.DIAMOND:
            if self.rank == 11: 
                self.scoreable = True
                self.score = -100
                self.is_sellable = True
        else:
            if self.rank == 10: 
                self.scoreable = True
                self.score = 3.14 
                self.is_sellable = True
        if self.rank == 14 and self.suit == Suits.HEART: self.is_sellable = True
        # self.score *= -1
        

class GZDeck(Deck):
    def __init__(self):
        self.cards = []
        for suit in Suits:
            for rank in range(2,15):
                self.cards.append(GZCard(rank,suit))
    
class LogicalGZDeck(Deck):
    def __init__(self):
        self.cards = []
        for suit in Suits:
            for rank in range(2, 15):
                self.cards.append(LogicalGZCard(rank, suit))


class GongZhuPlayer(Player):
    collection = None
    score = None
    def __init__(self, name):
        super().__init__(name)
        self.sort_by_suit()
        self.collection = []
        self.score = 0
    
    def sort_collection(self):
        self.collection = sorted(self.collection, key= lambda card: (card.suit.value, card.rank))

class LogicalGongZhuPlayer(Player):
    collection = None
    score = None
    def __init__(self, name):
        super().__init__(name)
        self.collection = []
        self.score = 0


class GongZhuEngine():
    players = None # list of players
    state = None #game state
    current_player = None # index of current player
    client_player = 0 #player running this program
    board = [None, None, None, None] # The cards that have been played of that trick
    board_size = 0 # Number of cards played in that trick
    lead_suit = None
    is_leader = True
    sells = [False, False, False, False]
    suit_played = [False, False, False, False]
    loser = None
    developer_mode = False
    com_mode = ComMode.SMART
    played_cards = []

    def __init__(self):
        self.players = (GongZhuPlayer("Player 1"), GongZhuPlayer("Player 2"), GongZhuPlayer("Player 3"), GongZhuPlayer("Player 4"))
        self.state = GameState.MAINMENU

    def deal_new_round(self, load_images = True):
        for player in self.players:
            player.collection =[]
            player.hand = []
        deck = GZDeck()
        deck.shuffle()
        for i in range(13):
            for player in self.players:
                card = deck.deal()
                if load_images: card.init_image()
                player.pull(card)
        if self.current_player == None:
            self.current_player = 0 #int(random.random() * 4)
        for player in self.players:
            player.sort_by_suit()
        if self.developer_mode and load_images:
            for player in self.players:
                for card in player.hand:
                    card.switch_visibility(True, True)
        elif load_images: 
            i = 0
            for player in self.players:
                for card in player.hand:
                    if i == self.client_player: card.switch_visibility(True, True)
                    else: card.switch_visibility(False)
        self.state = GameState.BIDDING 
        self.sells = [False, False, False, False]
        self.suit_played = [False, False, False, False]

    def sell_card(self, card):
        if self.state == GameState.BIDDING and card.is_sellable: self.sells[card.suit.value] = True

    def next_player(self):
        self.current_player += 1
        self.current_player %= 4
    
    def check_card(self, card):
        count = 0
        if self.is_leader: 
            for c in self.players[self.current_player].hand: 
                if c.suit == card.suit: count +=1
            if count == 1: return True
            if card.is_sellable: return not (self.sells[card.suit.value]) or self.suit_played[card.suit.value]
            else: return True
        
        if card.suit == self.lead_suit: 
            for c in self.players[self.current_player].hand: 
                if c.suit == self.lead_suit: count +=1
            if count == 1: return True
            if card.is_sellable: return not (self.sells[card.suit.value]) or self.suit_played[card.suit.value]
            return True
        
        for c in self.players[self.current_player].hand:
            if c.suit == self.lead_suit: return False
        return True
    
    #assumes valid card
    def play_card(self, card):        
        self.board[self.current_player] = card
        self.players[self.current_player].hand.remove(card)
        self.board_size += 1
        self.played_cards.append(card)
        
        if self.board_size == 1:
            self.is_leader = False
            self.lead_suit = card.suit        
        if self.board_size < 4:
            self.next_player()
        if self.board_size == 4:
            self.suit_played[self.lead_suit.value] = True
    
    #same as play_card but involves a collect at the end. This is for playing GZ purely in the engine, no display issues
    def next_state(self, card):
        self.play_card(card)
        if self.board_size == 4:
            self.collect()
        return self

    #Set the card selection based on some algorithm, skips when not a com player's turn, returns milliseconds of delay
    def com_select_card(self):
        start = time.time()
        if self.com_mode == ComMode.MULTIPLAYER: return 0       
        if self.current_player == 0: return 0

        if self.com_mode == ComMode.RANDOM:
            GZCard.selected = [self.random_select()]
            return 500

        if self.com_mode == ComMode.BASIC:
            return 500

        if self.com_mode == ComMode.SMART:
            GZCard.selected = [self.smart_select()]
            # print(f"Selected card: {GZCard.selected[0]}")
            ellapsed = round(1000*(time.time() - start))
            print(f"Time taken: {ellapsed}ms")
            return 500 - ellapsed if ellapsed < 500 else 0
    
    #returns a random valid playable card
    def random_select(self):
        while True:
            x = random.choice(self.players[self.current_player].hand)
            if self.check_card(x): return x
        # curr_hand = self.players[self.current_player].hand
        # follow_cards = [card for card in curr_hand if card.suit == self.lead_suit]
        # if len(follow_cards == 0): return  random.choice(curr_hand)
        # else: return random.choice(follow_cards)

    def smart_select(self):
        # print(self.players[self.current_player])
        # print(self.players[self.current_player].hand)
        pov_engine = POVGongZhuEngine(self.current_player, self)
        # pov_engine.set_attributes(self)
        root = ISMCTSNode(pov_engine)
        rs = root.best_action()
        for card in self.players[self.current_player].hand:
            if card.rank == rs.rank and card.suit == rs.suit: return card
        print("Algorithmically determined card does not exist in hand")
        return None
        # return root.best_action()
    
    #returns index of collector
    def collect(self):
        #determine collector
        highest_rank = 0
        ind = -1
        for i in range(len(self.board)):
            if self.board[i].rank > highest_rank and self.board[i].suit == self.lead_suit:
                highest_rank = self.board[i].rank
                ind = i
        for card in self.board:
            if card.scoreable:
                self.players[ind].collection.append(card)
        self.current_player = ind
        self.is_leader = True
        self.board = [None, None, None, None]
        self.board_size = 0
        return ind
            

    def score_game(self):
        if self.state != GameState.SCORING: return
        for player in self.players:
            if len(player.collection) == 16: #collecting everything condition
                player.score -= 2000
                continue
            round_score = 0
            doubled = False
            heart_count = 0
            for card in player.collection:
                if card.score != 3.14:
                    if self.sells[card.suit.value]:
                        round_score += card.score * 2
                    else: round_score += card.score
                else:
                    doubled = True
                if card.suit == Suits.HEART: heart_count += 1
            #all hearts logic
            if heart_count == 13:
                round_score -= 400 #200 to nullfiy the negative and another 200 bonus
                if self.sells[Suits.HEART.value]: round_score -= 400
            #doubler logic
            if doubled and len(player.collection) == 1:
                round_score = -50
                if self.sells[0]: round_score *= 2
            elif doubled:
                round_score *= 2
                if self.sells[0]: round_score *= 2
                
            player.score += round_score
        self.state = GameState.WAITING

    #returns the index of the player who has collected the pig
    def find_pig(self):
        for i in range(len(self.players)):
            for card in self.players[i].collection:
                if card.rank == 12 and card.suit == Suits.SPADE: return i

    def check_loser(self):
        max = 0
        min = 2**31 -1
        for player in self.players:
            if player.score < min:
                min = player.score
        
        for player in self.players:
            if player.score > 1000 + min and player.score > max:
                self.loser = player
                max = player.score
                
        if self.loser != None:
            self.state = GameState.ENDED

class POVGongZhuEngine(GongZhuEngine):
    
    def __init__(self, seat,engine_in):
        self.seat = seat
        self.set_attributes(engine_in)
    
    #engine_in is a GongZhuEngine obj that is in game
    def set_attributes(self, engine_in):
        if engine_in.state not in (GameState.PLAYING, GameState.BIDDING):
            print(f"Tried to set attributes but in: {engine_in.state}")
            return
        self.current_player = engine_in.current_player
        self.board = [self.convert_to_logical(card) if card is not None else None for card in engine_in.board]
        self.board_size = engine_in.board_size
        self.lead_suit = engine_in.lead_suit
        self.is_leader = engine_in.is_leader
        self.sells = engine_in.sells[:]
        self.suit_played = engine_in.suit_played[:]
        self.played_cards = [self.convert_to_logical(card) for card in engine_in.played_cards]
        self.state = engine_in.state
        
        self.players = []
        i = 0
        for player in engine_in.players:
            copied_player = GongZhuPlayer(player.name)
            # if self.seat == i: 
            copied_player.hand = [LogicalGZCard(card.rank, card.suit) for card in player.hand]
            copied_player.collection = [LogicalGZCard(card.rank, card.suit) for card in player.collection]
            #Do not copy over score
            self.players.append(copied_player)
            i+=1
        # print(f"Initial Player {engine_in.players[self.seat]}")
        self.pov_hand = [self.convert_to_logical(card) for card in engine_in.players[self.seat].hand]
        # print(f"Initial povhand {self.pov_hand}")

    def convert_to_logical(self, card):
        logical = LogicalGZCard(card.rank, card.suit)
        logical.score = card.score
        logical.is_sellable = card.is_sellable
        logical.scoreable = card.scoreable
        return logical

    def find_card_ind(self, card, list):
        for i in range(len(list)):
            if list[i].rank == card.rank and list[i].suit == card.suit: return i
        return -1

    def copy(self):
        return POVGongZhuEngine(self.seat, self)

    def set_hands(self, full_random):
        deck = LogicalGZDeck()
        # print(f"All Random: {full_random}. ")
        for card in self.played_cards:
            deck.cards.pop(self.find_card_ind(card, deck.cards))
            # print(f"Played: {card.rank} of {card.suit}. Deck size {len(deck.cards)}")
        if not full_random:
            # print(self.pov_hand)
            for card in self.pov_hand:
                deck.cards.pop(self.find_card_ind(card, deck.cards))
                # print(f"In hand: {card.rank} of {card.suit}. Deck size {len(deck.cards)}")
                # print(len(deck.cards))
        deck.shuffle()
        # print("deck shuffled")
        self.players[self.current_player]
        for i in range(4):
            if full_random: self.players[i].hand = []
            elif not full_random and i != self.seat: self.players[i].hand = []
        
        i = 0
        while not deck.is_empty():
            if i % 4 == 0 and not full_random:
                # print(f"Skipping")
                i += 1
                continue
            self.players[(self.seat + i)%4].hand.append(deck.deal())
            i+=1
            # print(f"cards dealt: {i}")

        if not full_random: self.players[self.seat].hand = self.pov_hand
        # for i in range(4):
        #     print(f"hands dealt. Player {i} hand Check-> {self.players[i].hand} len = {len(self.players[i].hand)}")

    def is_round_over(self):
        return all(len(p.hand) == 0 for p in self.players) and self.state == GameState.PLAYING
    
    def score_game(self):
        old_score = []
        for p in self.players:
            old_score.append(p.score)
        gs = self.state
        self.state = GameState.SCORING
        super().score_game()
        self.state = gs
        score_change = []
        for i in range(4):
            score_change.append(self.players[i].score - old_score[i])
        personal_score = score_change[self.seat]
        score_change.pop(self.seat)
        max_outside_score = max(score_change)
        bonus = 0
        # print("Adjusted Game Score Calculated")
        return max_outside_score - personal_score + bonus


'''
array of viewing player's cards
array of missing cards

player to act
viewing player
board - suit_played
played cards
'''

class Image():
    def __init__(self, name):
        self.image = pygame.image.load(name)
        self.orientation = 0
    
    def set_orientation(self, new_orientation):
        delta = new_orientation - self.orientation
        self.image = pygame.transform.rotate(self.image, delta)
        self.orientation = new_orientation     
        