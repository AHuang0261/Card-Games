from enum import Enum
from typing import Any
from Cards import *
import random
import pygame
#I think the different threads are not working together


class GameState(Enum):
    STARTING = 0
    PLAYING = 1
    SCORING = 2
    BIDDING = 3
    WAITING = 4
    ENDED = 5

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
        self.rect = self.image.get_rect(topleft = (0,0))
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
            
            
class GZDeck(Deck):
    def __init__(self):
        self.cards = []
        for suit in Suits:
            for rank in range(2,15):
                self.cards.append(GZCard(rank,suit))
    

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
    
    def serialize(self):
        return {
            'name': self.name,
            'hand': [card.serialize() for card in self.hand],
            'collection': [card.serialize() for card in self.collection],
            'score': self.score
        }
    
    @classmethod
    def deserialize(cls, data):
        player = cls(data['name'])
        player.hand = [GZCard.deserialize(card_data) for card_data in data['hand']]
        player.collection = [GZCard.deserialize(card_data) for card_data in data['collection']]
        player.score = data['score']
        return player
    

class GongZhuEngine():
    players = None # list of players
    state = None #game state
    current_player = None # index of current player
    board = [None, None, None, None] # The cards that have been played of that trick
    board_size = 0 # Number of cards played in that trick
    lead_suit = None
    is_leader = True
    sells = [False, False, False, False]
    suit_played = [False, False, False, False]
    loser = None
    developer_mode = True

    def __init__(self):
        self.players = (GongZhuPlayer("Player 1"), GongZhuPlayer("Player 2"), GongZhuPlayer("Player 3"), GongZhuPlayer("Player 4"))
        self.state = GameState.STARTING
    
    def deal_new_round(self):
        for player in self.players:
            player.collection =[]
            player.hand = []
        deck = GZDeck()
        deck.shuffle()
        for i in range(13):
            for player in self.players:
                player.pull(deck.deal())
        if self.current_player == None:
            self.current_player = 0 #int(random.random() * 4)
        for player in self.players:
            player.sort_by_suit()
        if self.developer_mode:
            for player in self.players:
                for card in player.hand:
                    card.switch_visibility(True)
        else: 
            for card in self.players[self.current_player].hand: card.switch_visibility(True)
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
    
    def play_card(self, card):
        #card validity is checked in event loop
        self.board[self.current_player] = card
        self.players[self.current_player].hand.remove(card)
        self.board_size += 1
        
        if self.board_size == 1:
            self.is_leader = False
            self.lead_suit = card.suit        
        if self.board_size < 4:
            self.next_player()
        if self.board_size == 4:
            self.suit_played[self.lead_suit.value] = True

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
            
    #!There seems to be an issue w the scoring where
    def score_game(self):
        if self.state != GameState.SCORING: return
        for player in self.players:
            if len(player.collection) == 16: #collecting everything condition
                player.score += 2000
                continue
            round_score = 0
            doubled = False
            for card in player.collection:
                if card.score != 3.14:
                    if self.sells[card.suit.value]:
                        round_score += card.score * 2
                    else: round_score += card.score
                else:
                    doubled = True
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
        for player in self.players:
            if player.score > 1000 and player.score > max:
                self.loser = player
                max = player.score
                
        if self.loser != None:
            self.state = GameState.ENDED

    def serialize(self):
        return {
            'players': [player.serialize() for player in self.players],
            'state': self.state.value,
            'current_player': self.current_player,
            'board': [card.serialize() if card else None for card in self.board],
            'board_size': self.board_size,
            'lead_suit': self.lead_suit.value if self.lead_suit else None,
            'is_leader': self.is_leader,
            'sells': self.sells,
            'suit_played': self.suit_played,
            'loser': self.loser.serialize() if self.loser else None
        }
    
    @classmethod
    def deserialize(cls, data):
        engine = cls()
        engine.players = [GongZhuPlayer.deserialize(player_data) for player_data in data['players']]
        engine.state = GameState(data['state'])
        engine.current_player = data['current_player']
        engine.board = [GZCard.deserialize(card_data) if card_data else None for card_data in data['board']]
        engine.board_size = data['board_size']
        engine.lead_suit = Suits(data['lead_suit']) if data['lead_suit'] is not None else None
        engine.is_leader = data['is_leader']
        engine.sells = data['sells']
        engine.suit_played = data['suit_played']
        engine.loser = GongZhuPlayer.deserialize(data['loser']) if data['loser'] else None
        return engine
    
    # deck = GZDeck()
    # deck.shuffle()
    # p = GongZhuPlayer("p1")
    # for i in range(15):
    #     p.pull(deck.deal())
    # print(p.hand)
    # p.sort_by_suit()
    # print(p.hand)   
class Image():
    def __init__(self, name):
        self.image = pygame.image.load(name)
        self.orientation = 0
    
    def set_orientation(self, new_orientation):
        delta = new_orientation - self.orientation
        self.image = pygame.transform.rotate(self.image, delta)
        self.orientation = new_orientation     
        