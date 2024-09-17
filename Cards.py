from enum import Enum
import random
import pygame

class Suits(Enum):
    CLUB = 0
    DIAMOND = 1
    HEART = 2
    SPADE = 3

class LogicalCard():
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self) -> str:
        return repr((self.rank, self.suit))
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    

class Card():
    SCALE_FACTOR = 0.20
    visible = False
    orientation = 0
    permanent = False
    
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.image = None

    def set_orientation(self, new_orientation):
        delta = new_orientation - self.orientation
        self.image = pygame.transform.rotate(self.image, delta)
        self.orientation = new_orientation

    def switch_visibility(self, state=None, p=False):
        if self.permanent: return
        self.permanent = p
        if state is None:
            self.visible = not self.visible
        else:
            self.visible = state
        self.load_image()

    def load_image(self):
        if self.visible:
            self.image = pygame.image.load(f'Images/Cards/{self.rank}_of_{self.suit.name.lower()}s.png')
        else:
            self.image = pygame.image.load('Images/Cards/back_of_card.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.SCALE_FACTOR, self.image.get_height() * self.SCALE_FACTOR))
        self.image = pygame.transform.rotate(self.image, self.orientation)

class Deck():
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Suits for rank in range(2, 15)]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def is_empty(self):
        return len(self.cards) == 0

class Player():
    def __init__(self, name):
        self.name = name
        self.hand = []
    
    def pull(self, card):
        self.hand.append(card)
        return card
    
    def push(self, card):
        self.hand.remove(card)
        return card

    def sort_by_rank(self):
        self.hand = sorted(self.hand, key=lambda card: (card.rank, card.suit.value))
    
    def sort_by_suit(self):
        self.hand = sorted(self.hand, key=lambda card: (card.suit.value, card.rank))
