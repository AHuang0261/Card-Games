from enum import Enum
from Cards import *
import pygame

class GameState(Enum):
    PLAYING = 0
    ENDED = 1

class WarEngine():
    p1 = None
    p2 = None
    p1_key = pygame.K_1
    p2_key = pygame.K_2
    game_state = None    
    current_player = None
    winner = None
    p1_board = []
    p2_board = []
    def __init__(self):
        self.p1 = Player("Player 1")
        self.p2 = Player("Player 2")
        deck = Deck()
        deck.shuffle()
        i = 0
        while not deck.is_empty():
            if i % 2 == 0: self.p1.pull(deck.deal())
            else: self.p2.pull(deck.deal())
            i +=1
        self.game_state = GameState.PLAYING
        self.current_player = self.p1
    
    def switch_player(self):
        if self.current_player == self.p1: self.current_player = self.p2
        else: self.current_player = self.p1
    
    def check_winner(self):
        if len(self.p2.hand) == 0:
            self.winner = self.p1
            self.game_state = GameState.ENDED
            return
        if len(self.p1.hand) == 0:
            self.winner = self.p2
            self.game_state = GameState.ENDED

    def give_cards(self):
        if len(self.p1_board) == 1 and len(self.p2_board) == 1:
            self.give_cards_rec(0)
    
    def give_cards_rec(self, shift):
        
        #recursive call to do I-De-clare-war 
        if self.p1_board[shift].rank == self.p2_board[shift].rank:
            for i in range(4):    
                self.p1_board.append(self.p1.hand.pop(0))
                self.p2_board.append(self.p2.hand.pop(0))
                if len(self.p1.hand) == 0:
                    self.winner = self.p2
                    self.game_state = GameState.ENDED
                    return
                if len(self.p2.hand) == 0:
                    self.winner = self.p1
                    self.game_state = GameState.ENDED
                    return
            return WarEngine.give_cards_rec(self, shift + 4)
            
        #pushing into winner's hand
        if self.p1_board[shift].rank > self.p2_board[shift].rank:
            for i in range(len(self.p1_board)):
                self.p1.hand.append(self.p1_board.pop())
                self.p1.hand.append(self.p2_board.pop())
        else: 
            for i in range(len(self.p2_board)):
                self.p2.hand.append(self.p1_board.pop())
                self.p2.hand.append(self.p2_board.pop())


    def play(self, key):
        if key == None: return
        if self.game_state == GameState.ENDED: return
        
        if self.current_player == self.p1 and key == self.p1_key:
            self.p1_board.append(self.p1.hand.pop(0))
            self.switch_player()
        if self.current_player == self.p2 and key == self.p2_key:
            self.p2_board.append(self.p2.hand.pop(0))
            self.switch_player()
        




