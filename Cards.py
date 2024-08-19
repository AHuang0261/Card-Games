from enum import Enum
import random
import pygame

class Suits(Enum):
    CLUB = 0
    DIAMOND = 1
    HEART = 2
    SPADE = 3

class Card:
    SCALE_FACTOR = 0.20
    cardBack = pygame.image.load('Images/back_of_card.png')
    
    @staticmethod
    def preload_images():
        images = {}
        images['cardBack'] = pygame.image.load('Images/back_of_card.png')
        for i in range(2, 15):
            for suit in Suits:
                image_path = f'Images/{i}_of_{suit.name.lower()}s.png'
                images[image_path] = pygame.image.load(image_path)
        return images

    images = preload_images()

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.visible = False
        self.orientation = 0
        self.permanent = False
        self.update_image()

    def update_image(self):
        if self.visible:
            self.image = Card.images[f'Images/{self.rank}_of_{self.suit.name.lower()}s.png']
        else:
            self.image = Card.images['cardBack']
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.SCALE_FACTOR), int(self.image.get_height() * self.SCALE_FACTOR)))
        self.image = pygame.transform.rotate(self.image, self.orientation)

    def __repr__(self):
        return repr((self.rank, self.suit))

    def set_orientation(self, new_orientation):
        delta = new_orientation - self.orientation
        self.image = pygame.transform.rotate(self.image, delta)
        self.orientation = new_orientation

    def switch_visibility(self, state=None, p=False):
        if self.permanent:
            return
        self.permanent = p
        if state is None:
            self.visible = not self.visible
        else:
            self.visible = state
        self.update_image()

    def serialize(self):
        return {
            'rank': self.rank,
            'suit': self.suit.value,  # Serialize suit as its value
            'visible': self.visible,
            'permanent': self.permanent,
            'orientation': self.orientation
        }

    @classmethod
    def deserialize(cls, data):
        suit = Suits(data['suit'])  # Deserialize suit from its value
        card = cls(data['rank'], suit)
        card.visible = data['visible']
        card.permanent = data['permanent']
        card.orientation = data['orientation']
        card.update_image()
        return card

class Deck():
    def __init__(self):
        self.cards = []
        for suit in Suits:
            for rank in range(2,15):
                self.cards.append(Card(rank,suit))
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        return self.cards.pop()
    
    def is_empty(self):
        return (len(self.cards) == 0)
    
class Player():
    name = None
    hand = None

    def __init__(self, name):
        self.name = name
        self.hand = []
    
    #may or may not want to sort after doing this
    def pull(self, card):
        self.hand.append(card)
        return card
    
    def push(self, card):
        self.hand.remove(card)
        return card

    def sort_by_rank(self):
        self.hand = sorted(self.hand, key= lambda card: (card.rank, card.suit.value))
    
    def sort_by_suit(self):
        self.hand = sorted(self.hand, key= lambda card: (card.suit.value, card.rank))
